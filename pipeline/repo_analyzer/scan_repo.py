import os

def scan_repository(repo_path):

    files = []

    for root, dirs, filenames in os.walk(repo_path):

        for file in filenames:

            full_path = os.path.join(root, file)

            files.append({
                "filename": file,
                "path": full_path
            })

    return files


if __name__ == "__main__":

    repo = "../../flask"

    data = scan_repository(repo)

    print(data[:10])