# backend/github/github_service.py

import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}


def create_branch(repo, new_branch, base_branch="main"):
    url = f"https://api.github.com/repos/{repo}/git/ref/heads/{base_branch}"

    r = requests.get(url, headers=headers)
    sha = r.json()["object"]["sha"]

    data = {
        "ref": f"refs/heads/{new_branch}",
        "sha": sha
    }

    r = requests.post(
        f"https://api.github.com/repos/{repo}/git/refs",
        json=data,
        headers=headers
    )

    return r.json()


def commit_file(repo, branch, file_path, content, commit_message):

    url = f"https://api.github.com/repos/{repo}/contents/{file_path}"

    data = {
        "message": commit_message,
        "content": base64.b64encode(content.encode()).decode(),
        "branch": branch
    }

    r = requests.put(url, json=data, headers=headers)

    return r.json()


def create_pull_request(repo, title, body, head, base="main"):

    url = f"https://api.github.com/repos/{repo}/pulls"

    data = {
        "title": title,
        "body": body,
        "head": head,
        "base": base
    }

    r = requests.post(url, json=data, headers=headers)

    return r.json()


def get_open_issues(repo):

    url = f"https://api.github.com/repos/{repo}/issues?state=open"

    r = requests.get(url, headers=headers)

    print("GitHub Status:", r.status_code)
    print("GitHub Response:", r.json())

    if r.status_code != 200:
        return []

    return r.json()