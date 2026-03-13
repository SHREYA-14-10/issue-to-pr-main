def generate_code(issue_text):

    # This is the prompt we send to AI
    prompt = f"""
    A developer created the following GitHub issue.

    Issue:
    {issue_text}

    Write Python code that solves this issue.
    """

    # For now we simulate AI output
    generated_code = f"""
# AI Generated Code
# Issue: {issue_text}

print("Fix applied for: {issue_text}")
"""

    return generated_code