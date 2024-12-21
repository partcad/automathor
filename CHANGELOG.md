# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added

- Added `Automathor_Jira_Exception` class for handling Jira errors.
- Added Automathor functionality.
- Added chown command to `.devcontainer/devcontainer.json` to address cache permissions.
- Added jinja2 dependency.
- Added support for `check-jsonschema` via pre-commit.
- Added support for assigning issues to users.
- Added support for epics.
- Added support for flake8, bandit, and black via pre-commit.
- Added support for JIRA issues creation.
- Added support for subtasks.
- Added support for using `pre-commit` to automatically update external dependencies.

### Changed

- Improved `submit.py` for better readability and robustness.
- Modified devcontainer for improved cache/config handling.
- Updated `submit.py` to handle exceptions gracefully.
- Updated `template.jinja2` to improve formatting.
- Updated poetry lock file for new jinja2 dependency.

### Fixed

- Fixed potential errors in `submit.py` that could cause issues with processing templates.
