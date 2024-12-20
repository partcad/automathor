import os
import subprocess
import re
from dataclasses import dataclass
from datetime import datetime
from typing import List
import logging
import json

# 1. Make user mentions work
# 2. Show summary table


@dataclass
class AnnotatedLine:
    # 1. Convert value to full commit hash
    commit: str
    filename: str
    author_email: str
    datetime: datetime
    line_number: int
    source_line: str


@dataclass
class Context:
    filename: str
    line: int
    commit: str
    author_email: str
    datetime: datetime
    todo: str
    text: str
    lines: List[AnnotatedLine]

    def __repr__(self):
        return f"{self.filename}:{self.line}\n{self.author_email} {self.datetime}\n{self.commit}\n"

    def render(self):
        template_loader = jinja2.FileSystemLoader(searchpath="./")
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template("template.jinja2")

        output = template.render(context=self)
        return output

    def user(self):
        if self.author_email == "ailin@partcad.org":
            return "@ailin"
        if self.author_email == "alexander@ilyin.eu":
            return "@ailin"
        if self.author_email == "openvmp@proton.me":
            return "@rkuz"
        if self.author_email == "not.committed.yet":
            return "Not Committed"
        if self.author_email == "clairbee@guidemaze.com":
            return "@rkuz"
        if self.author_email == "admin+github-admin@partcad.org":
            return "@rkuz"
        raise ValueError(f"Unknown user for email: {self.author_email}")

    def language(self):
        extensions = {
            ".py": "python",
            ".md": "markdown",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json",
            ".feature": "gherkin",
        }
        for ext, lang in extensions.items():
            if self.filename.endswith(ext):
                return lang
        raise ValueError(f"Unknown language for file: {self.filename}")


from dataclasses import dataclass, field
import subprocess
import jinja2


@dataclass
class Match:
    file: str
    line: int
    text: str

    def get_git_blame_output(self) -> Context:
        self.line = int(self.line)

        start_line = max(1, self.line - 4)
        end_line = self.line + 4
        command = f"git blame --show-email {self.file} | sed -n '{start_line},{end_line}p'"
        logging.debug(f"RUNNING {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Command failed with error: {result.stderr}")

        context = Context(self.file, self.line, None, None, None, None, None, [])
        for line in result.stdout.strip().split("\n"):
            logging.debug(f"PROCESSING {line}")
            data = self.parse_line(line)
            if data.line_number == self.line:
                context.commit = data.commit
                context.author_email = data.author_email
                context.datetime = data.datetime
                context.todo = self.text.strip().lstrip("#:TODO ")
                context.text = self.text.strip().lstrip("#:TODO ")
            context.lines.append(data)
        return context

    def parse_line(self, line) -> AnnotatedLine:
        pattern = r"(\w+)\s+(\S+)\s+\(<([^>]+)>\s+(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]\d{4})\s+(\d+)\)\s*(.*)"
        match = re.match(pattern, line)
        pattern_two = r"(\w+)\s+\(<([^>]+)>\s+(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]\d{4})\s+(\d+)\)\s*(.*)"
        match_two = re.match(pattern_two, line)
        if match:
            commit, filename, author_email, date_str, line_number, source_line = match.groups()
            date_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S %z")
            return AnnotatedLine(commit, filename, author_email, date_time, int(line_number), source_line)
        elif match_two:
            commit, author_email, date_str, line_number, source_line = match_two.groups()
            date_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S %z")
            return AnnotatedLine(commit, self.file, author_email, date_time, int(line_number), source_line)
        else:
            raise ValueError(f"Line does not match expected format: {line}")


@dataclass
class Automathor:

    grep: List[str] = field(default_factory=list)
    matches: List[Match] = field(default_factory=list)

    def run_git_grep(self) -> None:
        command = ["git", "grep", "-n", "TODO"]
        logging.debug(f"Running command: {' '.join(command)}")
        result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
        self.grep = result.stdout.strip().split("\n")

    def process_matches(self) -> None:
        for line in self.grep:
            self.matches.append(Match(*line.split(":", 2)))


logging.basicConfig(level=logging.INFO)

automathor = Automathor()
automathor.run_git_grep()
automathor.process_matches()
i = 0
metadata = {}
os.makedirs("tmp", exist_ok=True)
for match in automathor.matches:
    i += 1
    data = match.get_git_blame_output()
    filename = f"tmp/{i}.md"
    with open(filename, "w") as f:
        f.write(data.render())
        logging.info(f"Written {filename}")
        metadata[filename] = {
            "filename": data.filename,
            "line": data.line,
            "type": "Task",
            "summary": data.todo,
        }
        # break
with open("tmp/metadata.json", "w") as f:
    json.dump(metadata, f)
    logging.info(f"Written metadata to tmp/metadata.json")
