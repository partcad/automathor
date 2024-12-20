import re
import json
import subprocess

# 1. Add support for epics
# 2. Add support for subtasks
# 3. Add support for assigning issues to users

directory = "tmp"
with open(f"{directory}/metadata.json", "r") as f:
    metadata = json.load(f)

for template, data in metadata.items():
    # 1. Make summary Camelcase
    # 2. Add --dry-run flag
    if "issue" in data:
        print(f"Skipping {template} as it already has an issue")
        continue

    command = f"jira issue create --no-input -t{data['type']} -s'{data['summary']}' --template {template}"
    command = [
        "jira",
        "issue",
        "create",
        "--no-input",
        f"-t{data['type']}",
        f"-s{data['summary']}",
        "--template",
        template,
    ]
    print(command)

    result = subprocess.run(command, capture_output=True)
    if result.returncode != 0:
        print(result.stderr.decode())
        raise Exception("Failed to create issue")

    print(result.stdout.decode())
    pattern = r"TODO-(\d+)"
    result = re.search(pattern, result.stdout.decode())
    search = "TODO" + ":"

    if result:
        issue = result.group(0)
        number = int(result.group(1))
        print(f"Created issue {issue}")
        command = f"sed -i '{data['line']}s/{search}/TODO-{number}:/' {data['filename']}"
        print(f"Running command: {command}")
        result = subprocess.run(command, shell=True, capture_output=True)
        print(f"Added {issue} to {data['filename']}:{data['line']}")
        metadata[template]["issue"] = issue
        with open(f"{directory}/metadata.json", "w") as f:
            json.dump(metadata, f)
