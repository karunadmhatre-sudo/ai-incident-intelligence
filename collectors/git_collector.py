import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


output_dir = Path("data/raw/git")
output_dir.mkdir(parents=True, exist_ok=True)


git_command = [
    "git",
    "log",
    "--pretty=format:%H|%aI|%an|%s",
    "--name-only"
]

result = subprocess.run(
    git_command,
    capture_output=True,
    text=True,
    check=True
)


lines = result.stdout.splitlines()

commits = []
current_commit = None

for line in lines:

    if not line.strip():
        continue

    parts = line.split("|", 3)

    if len(parts) == 4:

        if current_commit:
            commits.append(current_commit)

        commit_sha, commit_time, author, message = parts

        current_commit = {
            "commit_sha": commit_sha,
            "commit_time": commit_time,
            "author": author,
            "message": message,
            "changed_files": []
        }

    else:

        if current_commit:
            current_commit["changed_files"].append(line.strip())


if current_commit:
    commits.append(current_commit)


collection_time = datetime.now(timezone.utc).isoformat()

collection = {
    "collection_time": collection_time,
    "source": "git",
    "repository": Path.cwd().name,
    "branch": "main",
    "commit_count": len(commits),
    "commits": commits
}


timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

output_file = output_dir / f"git_{timestamp}.json"


with open(output_file, "w", encoding="utf-8") as file:
    json.dump(collection, file, indent=2)


print(f"Collected {len(commits)} Git commits")
print(f"Raw data written to: {output_file}")