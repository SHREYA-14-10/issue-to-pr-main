import openai
import os
from dotenv import load_dotenv

load_dotenv()

# Load OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_code(issue_text, repo_files=None):
    """
    Generate code for a given issue text and repo context.
    repo_files: Optional dict with filename -> content
    """

    context = ""

    if repo_files:
        for fname, content in repo_files.items():
            context += f"\n# File: {fname}\n{content}\n"

    prompt = f"""
You are a senior Python developer.

Fix the following issue and return ONLY the corrected Python code.

Issue:
{issue_text}

Repository context:
{context}

Return only the modified code.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        code = response["choices"][0]["message"]["content"].strip()
        return code

    except Exception as e:
        print("OpenAI Error:", e)
        return "# AI could not generate fix"