from fastapi import FastAPI
from pydantic import BaseModel
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print("OpenAI Key Loaded:", "YES" if OPENAI_API_KEY else "NO")

REPO_NAME = "deeksharmlr-016/issue-to-pr"

from backend.github.github_service import (
    create_branch,
    commit_file,
    create_pull_request,
    get_open_issues
)

from backend.ai.ai_generator import generate_fix
from ai_pr_context import fetch_relevant_files

app = FastAPI()


# -----------------------------
# FALLBACK FIX (when AI fails)
# -----------------------------
def fallback_fix(issue_text):

    text = issue_text.lower()

    if "division" in text or "zero" in text:
        return """
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
"""

    elif "login" in text:
        return """
def login(username, password):
    if not username or not password:
        return "Invalid credentials"

    if username == "admin" and password == "admin":
        return "Login successful"

    return "Login failed"
"""

    else:
        return """
def fix_issue():
    print("Issue handled by fallback system")
"""


# -----------------------------
# ISSUE PRIORITY FUNCTION
# -----------------------------
def get_issue_priority(issue):

    if not isinstance(issue, dict):
        return 999

    title = issue.get("title", "")
    body = issue.get("body", "")

    text = (title + " " + body).lower()

    if "crash" in text:
        return 1
    elif "bug" in text:
        return 2
    else:
        return 3


# -----------------------------
# HOME ENDPOINT
# -----------------------------
@app.get("/")
def home():
    return {
        "message": "Issue to PR system running",
        "openai_key_loaded": True if OPENAI_API_KEY else False
    }


# -----------------------------
# LIST ISSUES
# -----------------------------
@app.get("/issues")
def list_issues():

    issues = get_open_issues(REPO_NAME)

    issues = [i for i in issues if isinstance(i, dict) and "pull_request" not in i]

    simplified = [
        {
            "number": i.get("number"),
            "title": i.get("title"),
            "body": i.get("body", ""),
            "state": i.get("state"),
            "url": i.get("html_url")
        }
        for i in issues
    ]

    sorted_issues = sorted(simplified, key=get_issue_priority)

    highest = sorted_issues[0] if sorted_issues else None

    return {
        "open_issues": simplified,
        "highest_priority_issue": highest
    }


# -----------------------------
# REQUEST MODEL
# -----------------------------
class Issue(BaseModel):
    text: str


# -----------------------------
# GENERATE PR (MANUAL ISSUE)
# -----------------------------
@app.post("/generate-pr")
def generate_pr(issue: Issue):

    branch_name = f"ai-fix-{int(time.time())}"

    repo_files = fetch_relevant_files(issue.text)

    try:
        generated_code = generate_fix(issue.text, repo_files)

        if not generated_code or len(generated_code.strip()) < 10:
            raise Exception("AI returned empty code")

        print("AI GENERATED FIX:\n", generated_code)

    except Exception as e:

        print("AI FAILED:", e)

        generated_code = fallback_fix(issue.text)

        print("USING FALLBACK FIX")

    create_branch(REPO_NAME, branch_name)

    commit_file(
        REPO_NAME,
        branch_name,
        "fix_ai.py",
        generated_code,
        "AI generated fix"
    )

    pr = create_pull_request(
        repo=REPO_NAME,
        title=f"AI Fix: {issue.text[:30]}",
        body=f"""
## AI Generated Fix
{generated_code}

""",
        head=branch_name,
        base="main"
    )

    return {
        "message": "PR attempted",
        "branch": branch_name,
        "generated_code": generated_code,
        "github_response": pr
    }


# --------------------------------
# AUTO GENERATE PR FROM HIGHEST PRIORITY ISSUE
# --------------------------------
@app.post("/generate-pr-highest-risk")
def generate_pr_highest_risk():

    issues = get_open_issues(REPO_NAME)

    issues = [i for i in issues if isinstance(i, dict) and "pull_request" not in i]

    if not issues:
        return {"message": "No issues found"}

    sorted_issues = sorted(issues, key=get_issue_priority)

    highest_issue = sorted_issues[0]

    issue_text = highest_issue.get("title", "")

    if highest_issue.get("body"):
        issue_text += "\n" + highest_issue["body"]

    repo_files = fetch_relevant_files(issue_text)

    try:

        generated_code = generate_fix(issue_text, repo_files)

        if not generated_code or len(generated_code.strip()) < 10:
            raise Exception("AI returned empty code")

        print("\nAI GENERATED FIX:\n", generated_code)

    except Exception as e:

        print("AI FAILED:", e)

        generated_code = """
def fallback_fix():
    print("AI generation failed, using fallback fix.")
"""

    branch_name = f"ai-fix-{int(time.time())}"

    create_branch(REPO_NAME, branch_name)

    commit_file(
        REPO_NAME,
        branch_name,
        "fix_ai.py",
        generated_code,
        "AI fix for highest priority issue"
    )

    pr = create_pull_request(
        repo=REPO_NAME,
        title=f"AI Fix: {issue_text[:40]}",
        body=f"""
AI generated fix for highest priority issue:


{generated_code}

""",
        head=branch_name,
        base="main"
    )

    return {
        "message": "PR created",
        "issue_title": highest_issue.get("title"),
        "branch": branch_name,
        "generated_code": generated_code,
        "github_response": pr
    }