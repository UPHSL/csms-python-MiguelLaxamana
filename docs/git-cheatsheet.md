# CSMS Python Git Cheatsheet

## Check Repository Status
```bash
git status
```

## Show Current Branch
```bash
git branch --show-current
```

## View Remote Repositories
```bash
git remote -v
```

## View Recent Commits
```bash
git log --oneline -5
```

## Switch to Main
```bash
git switch main
```

## Update Main
```bash
git pull origin main
```

## Create a Feature Branch
```bash
git switch -c feature/<ticket>-<short-description>
```

Example:
```bash
git switch -c feature/t01-resident-domain-model
```

## View Unstaged Changes
```bash
git diff
```

## Stage a File
```bash
git add <file>
```

Example:
```bash
git add src/csms/models/resident.py
```

## Stage Multiple Specific Files
```bash
git add src/csms/models/resident.py tests/test_application.py
```

Prefer staging the files that belong to the ticket explicitly.

## Review Staged Changes
```bash
git diff --staged
```

## Commit
```bash
git commit -m "type: short description"
```

Example:
```bash
git commit -m "feat: define resident domain model"
```

## Push a New Branch
```bash
git push -u origin <branch-name>
```

Example:
```bash
git push -u origin feature/t01-resident-domain-model
```

## Push an Existing Tracked Branch
```bash
git push
```

## Unstage a File
```bash
git restore --staged <file>
```

This removes the file from the staging area without deleting your working copy changes.

## Restore an Unstaged File
```bash
git restore <file>
```

Use this carefully.
Uncommitted changes in that file will be discarded.

## Standard Ticket Workflow

1. Check your repository.
```bash
git status
```

2. Switch to main.
```bash
git switch main
```

3. Update main.
```bash
git pull origin main
```

4. Create the required ticket branch.
```bash
git switch -c feature/<ticket>-<description>
```

5. Implement the ticket.

6. Run automated tests.
```bash
pytest
```

7. Review your changes.
```bash
git status
git diff
```

8. Stage only the required files.
```bash
git add <files>
```

9. Review the staged changes.
```bash
git diff --staged
```

10. Commit.
```bash
git commit -m "<required commit message>"
```

11. Push.
```bash
git push -u origin <branch-name>
```

12. Create the required Pull Request.

## Commit Types

Common commit types:
* `feat`
* `fix`
* `test`
* `docs`
* `refactor`
* `chore`

Examples:
* `feat: define resident domain model`
* `fix: correct request validation`
* `test: add service request tests`
* `docs: update Python project documentation`
* `refactor: simplify resident service`
* `chore: update development configuration`

## Before Starting a Ticket

```bash
git switch main
git pull origin main
git status
```

## Before Committing

```bash
pytest
git status
git diff
```

## Before Pushing

```bash
pytest
git status
git log --oneline -5
```

## Pull Request Review

Before submitting a Pull Request, confirm:
* correct ticket reference
* correct feature branch
* implementation summary provided
* acceptance criteria completed
* tests pass
* manual verification completed when required
* no unrelated changes
* meaningful commit message
* no generated dependency files committed

## Main Branch

The `main` branch represents the stable integrated application.
Normal ticket development should occur in a separate feature branch.

## Important Rules

* Do not perform normal activity development directly on `main`.
* Do not commit `venv/` or `__pycache__/`.
* Do not commit unrelated files.
* Do not use another student's repository.
* Do not force push unless specifically instructed.
* Do not rewrite Git history unless specifically instructed.
* Always inspect `git status` before committing.
* Always inspect `git diff --staged` before committing.

## Ticket Completion

A ticket is ready when:
* The requirement works.
* Acceptance criteria are satisfied.
* Automated tests pass.
* Existing behavior still works.
* Changes are traceable in Git.
* Only intended files are included.
* The required development workflow was followed.