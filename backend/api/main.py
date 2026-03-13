from fastapi import FastAPI
from pydantic import BaseModel
import time
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print("Loaded OpenAI Key:", "YES" if OPENAI_API_KEY else "NO")

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

    # keep only real issue objects
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
# MANUAL ISSUE INPUT
# -----------------------------
class Issue(BaseModel):
    text: str


@app.post("/generate-pr")
def generate_pr(issue: Issue):

    branch_name = f"ai-fix-{int(time.time())}"

    repo_files = fetch_relevant_files(issue.text)

    generated_code = generate_fix(issue.text, repo_files)

    create_branch(REPO_NAME, branch_name)

    commit_file(
        REPO_NAME,
        branch_name,
        "fix_ai.py",
        generated_code,
        "AI fix for issue"
    )

    pr = create_pull_request(
        repo=REPO_NAME,
        title=f"AI Fix: {issue.text[:30]}",
        body=generated_code,
        head=branch_name,
        base="main"
    )

    return {
        "message": "PR attempted",
        "branch": branch_name,
        "github_response": pr
    }


# -----------------------------
# AUTO PRIORITY ISSUE
# -----------------------------
@app.post("/generate-pr-highest-risk")
def generate_pr_highest_risk():

    issues = get_open_issues(REPO_NAME)

    # remove pull requests + invalid items
    issues = [i for i in issues if isinstance(i, dict) and "pull_request" not in i]

    if not issues:
        return {"message": "No issues found"}

    # apply priority sorting
    sorted_issues = sorted(issues, key=get_issue_priority)

    highest_issue = sorted_issues[0]

    issue_text = highest_issue.get("title", "")

    if highest_issue.get("body"):
        issue_text += "\n" + highest_issue["body"]

    repo_files = fetch_relevant_files(issue_text)

    generated_code = generate_fix(issue_text, repo_files)

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
        title=f"AI Fix: {issue_text[:30]}",
        body=generated_code,
        head=branch_name,
        base="main"
    )

    return {
        "message": "PR created",
        "issue_title": highest_issue.get("title"),
        "branch": branch_name,
        "github_response": pr
    }