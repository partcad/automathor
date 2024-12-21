"""
This module provides functionality to create Jira issues based on metadata from a JSON file.

Classes:
    Automathor_Jira_Exception: Custom exception for errors during Jira issue creation.

Usage:
    The script reads metadata from 'tmp/metadata.json', processes each template,
    and creates Jira issues if they do not already exist. It updates the metadata with the created issue information
    and modifies the corresponding file to include the issue number.
"""

import re
import json
import subprocess  # nosec B404


class Automathor_Jira_Exception(Exception):
    """
    Custom exception class for Automathor Jira integration errors.

    This exception is raised when there is an error related to the Automathor Jira integration.
    Attributes:
      message (str): Explanation of the error.

    """


# 1. Add support for epics
# 2. Add support for subtasks
# 3. Add support for assigning issues to users

directory = "tmp"
with open(f"{directory}/metadata.json") as f:
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

    result = subprocess.run(command, capture_output=True)  # nosec B603
    if result.returncode != 0:
        print(result.stderr.decode())
        raise Automathor_Jira_Exception("Failed to create issue")

    print(result.stdout.decode())
    pattern = r"TODO-(\d+)"
    result = re.search(pattern, result.stdout.decode())
    search = "TODO" + ":"

    if result:
        issue = result.group(0)
        number = int(result.group(1))
        print(f"Created issue {issue}")
        command = [
            "sed",
            "-i",
            f"{data['line']}s/{search}/TODO-{number}:/",
            data["filename"],
        ]
        print(f"Running command: {command}")
        result = subprocess.run(command, capture_output=True)  # nosec B603
        print(f"Added {issue} to {data['filename']}:{data['line']}")
        metadata[template]["issue"] = issue
        with open(f"{directory}/metadata.json", "w") as f:
            json.dump(metadata, f)
