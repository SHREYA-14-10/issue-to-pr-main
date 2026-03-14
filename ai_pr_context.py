import os

def fetch_relevant_files(issue_text, repo_path="."):

    relevant_files = {}
    keywords = issue_text.lower().split()

    for root, dirs, files in os.walk(repo_path):

        if "venv" in root or ".git" in root or "__pycache__" in root:
            continue

        for file in files:

            if not file.endswith(".py"):
                continue

            file_path = os.path.join(root, file)

            try:
                with open(file_path, "r", encoding="utf-8") as f:

                    content = f.read()

                    for keyword in keywords:
                        if keyword in content.lower():
                            relevant_files[file_path] = content[:2000]
                            break

            except:
                pass

    return relevant_files