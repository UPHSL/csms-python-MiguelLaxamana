# CSMS Python Developer Handbook

## Purpose

This handbook defines the standard development practices for the Python implementation of CSMS.
Students should follow these practices throughout the semester unless an activity provides more specific instructions.

## Required Tools

* Python 3.10 or later
* pip
* Git
* GitHub
* Visual Studio Code or another Python-compatible editor
* Web browser

## Verify the Environment

Run:
```bash
python --version
pip --version
git --version
```

The project requires Python 3.10 or later.
Ensure your virtual environment is activated before running project commands.

## Install Dependencies

For a repository using `pyproject.toml`, install the dependencies in editable mode:
```bash
pip install -e .
```

Do not commit:
* `venv/`
* `__pycache__/`

## Run the Application

```bash
flask run
```

The application normally runs at:
`http://127.0.0.1:5000`

## Development Debug Mode

```bash
flask run --debug
```

This uses Flask's interactive debugger and auto-reloader.

## Run Tests

```bash
pytest
```

All required tests must pass before submitting work.

## Before Starting an Activity

Begin from the project directory.
Check:
```bash
git status
git branch --show-current
```

Your previous work should be committed before starting another activity.

## Update Main

Switch to `main`:
```bash
git switch main
```

Update it:
```bash
git pull origin main
```

Do not begin a new activity from an unfinished feature branch.

## Create the Required Feature Branch

Use the branch name specified by the activity.
Example:
```bash
git switch -c feature/t01-resident-domain-model
```

Verify:
```bash
git branch --show-current
```

## Understand Before Editing

Before modifying code:
* Read the complete Moodle activity.
* Identify the required files.
* Identify the expected behavior.
* Identify the required automated tests.
* Review the existing project structure.
* Implement only the assigned scope.

Do not begin by randomly modifying files until tests pass.

## Development Cycle

A recommended development cycle is:
1. Make a small change.
2. Save the file.
3. Run the relevant test suite.
4. Read any error carefully.
5. Correct the implementation.
6. Run the tests again.
7. Continue until the requirement is complete.

## Python Conventions

Follow the conventions established by the existing codebase.
The starter project uses:
* PEP 8 style guidelines
* `snake_case` for variables, functions, and properties
* `PascalCase` for classes
* double or single quotes consistently
* 4-space indentation

Do not introduce a formatter, linter, type-checker, or different architecture unless the project or current ticket requires it.

## Testing

The project uses the `pytest` test framework and the Flask Test Client.
Run:
```bash
pytest
```

Before completing an activity, always run the complete suite.
Existing tests should continue to pass.
A new feature should not unnecessarily break previously completed functionality.

## Verify the Application

When the activity affects application behavior, run:
```bash
flask run
```

Verify the required endpoint or interface.
For the starter application, useful checks include:
* `http://127.0.0.1:5000`
* `http://127.0.0.1:5000/health`

Stop the server with:
`Ctrl + C`

## Review Your Work

Before staging files:
```bash
git status
git diff
```

Confirm that:
* only expected files changed
* `venv/` was not added
* temporary files were not added
* generated files were not added
* unrelated starter files were not modified

## Stage Changes

Prefer explicitly staging the files that belong to the activity.
Example:
```bash
git add src/csms/models/resident.py
git add tests/test_application.py
```

Then review:
```bash
git status
git diff --staged
```

Avoid using:
```bash
git add .
```
when unrelated files are present.

## Commit

Use the commit message required by the activity.
Example:
```bash
git commit -m "feat: define resident domain model"
```

Do not use vague messages such as:
* update
* changes
* done
* activity
* final
* fix

The commit message should describe the change.

## Commit Types

Common commit types include:
* `feat`
* `fix`
* `test`
* `docs`
* `refactor`
* `chore`

Examples:
* `feat: define resident domain model`
* `fix: correct health response`
* `test: add resident behavior coverage`
* `docs: update Python setup instructions`
* `refactor: simplify resident service`
* `chore: update development configuration`

## Push

Push a new feature branch:
```bash
git push -u origin <branch-name>
```

For later pushes on the same tracked branch:
```bash
git push
```

## Pull Requests

When required, create a Pull Request using the branches specified by the activity.

Before creating the Pull Request, verify:
```bash
git status
pytest
```

The working tree should be clean and all required tests should pass.
Review the Pull Request's "Files changed" section before submission.

## Debugging

When an error occurs, read the error message before changing code.
Determine:
* Which command failed?
* Which file is mentioned?
* Which line is mentioned?
* What error type occurred?
* Is the problem related to code, Python, dependencies, Git, tests, or application behavior?

Avoid making unrelated changes while troubleshooting one problem.

## Common Setup Problems

### Wrong Python Version

Check:
```bash
python --version
```
Ensure your virtual environment is activated (`venv`).

### Dependencies Are Missing

Run:
```bash
pip install -e .
```

### venv Was Deleted

Recreate it and reinstall dependencies:
```bash
python -m venv venv
# Activate it (OS specific), then:
pip install -e .
```

Do not restore or copy `venv` manually from another machine or student.

### Tests Fail After Your Changes

Inspect:
```bash
git diff
```

Determine which requirement or previous behavior was affected.
Do not modify unrelated files merely to force tests to pass.

### Application Does Not Start

Check:
```bash
python --version
pip --version
pip install -e .
flask run
```

Read the reported error carefully.

## Files That Should Not Be Committed

Do not intentionally commit local or generated files such as:
* `venv/`
* `__pycache__/`
* `.pytest_cache/`
* `.env`
* `.DS_Store`
* `coverage/`

Follow the repository's `.gitignore`.

## Student Responsibility

Students must understand their implementation.
You may be asked to explain:
* a class
* a function
* a test
* a Git command
* a commit
* a branch
* a Pull Request
* a design decision
* an error you encountered
* how you verified your solution

Successful execution alone is not sufficient if the submitted work cannot be explained.