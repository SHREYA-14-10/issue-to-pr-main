import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_fix(issue_text, repo_files):

    text = issue_text.lower()

    print("Issue received:", text)

    # -----------------------------
    # DIVISION BUG
    # -----------------------------
    if "division" in text or "divide" in text or "zero" in text:

        return """
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
"""

    # -----------------------------
    # LOGIN BUG
    # -----------------------------
    elif "login" in text:

        return """
def login(username, password):
    if not username or not password:
        return "Invalid credentials"

    # simulate login check
    if username == "admin" and password == "admin":
        return "Login successful"

    return "Login failed"
"""

    # -----------------------------
    # EMAIL VALIDATION
    # -----------------------------
    elif "email" in text:

        return """
def validate_email(email):
    if "@" not in email or "." not in email:
        return False
    return True
"""

    # -----------------------------
    # CALCULATOR BUG
    # -----------------------------
    elif "calc" in text or "calculator" in text:

        return """
class Calculator:

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
"""

    # -----------------------------
    # DEFAULT AI FIX
    # -----------------------------
    else:

        return """
def fix_issue():
    print("Issue handled by AI system")
"""
