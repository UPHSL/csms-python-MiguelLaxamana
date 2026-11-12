# Preliminary Examination Checkpoint

## Developer Information

**Name:** Miguel Laxamana
**GitHub Username:** *MiguelLaxamana*
**Primary Technology Stack:** Python, Flask, SQLite, pytest
**T03 Branch:** `feature/t03-resident-persistence`

## My T03 Implementation

The SQLite database is stored locally in the `src/csms/` directory as `csms.db`. The database connection and table initialization are handled by `src/csms/database.py`. The `ResidentRepository` is responsible for saving and retrieving Resident records from SQLite. When `save()` is called, the resident's information is inserted into the `residents` table and the generated database ID is assigned back to the Resident object. SQLite generates the Resident ID automatically using the `INTEGER PRIMARY KEY AUTOINCREMENT` column. The `find_by_id()` method searches the database using the Resident ID and converts the returned database row back into a `Resident` object. If no matching record exists, `find_by_id()` returns `None`. My automated tests use temporary SQLite databases so that the tests do not depend on my normal development database.

## My Persistence Design Decision

One design decision I made was to allow the database path to be provided to both the database functions and the `ResidentRepository`. I implemented this so my automated tests can use pytest's temporary directory instead of modifying the actual development database. I considered using only the default `csms.db` file for every test, but that could cause test data to remain between test runs. Using a temporary database keeps each test isolated and makes the tests more repeatable. The default database path is still used when no custom path is provided, so the normal application behavior remains simple.

## Files I Changed

**File:** `src/csms/database.py`
**Purpose:** Creates SQLite connections and initializes the `residents` table.

**File:** `src/csms/repositories/resident_repository.py`
**Purpose:** Implements saving Residents to SQLite and retrieving them by ID.

**File:** `tests/test_resident_repository.py`
**Purpose:** Tests Resident persistence, retrieval, generated IDs, missing records, persistence across repository instances, and the student-designed multiple-resident scenario.

## Problem I Encountered

**Problem or error:** I encountered a `ModuleNotFoundError: No module named 'src'` when a test file was run directly.

**Cause:** The test was being executed as an individual Python file instead of being run from the project root through pytest, so Python did not resolve the project package structure correctly.

**How I resolved it:** I ran the tests from the project root using `python -m pytest`. This correctly loads the `src` package and runs the complete test suite.

## My Student-Designed Test

**Test name:** `test_multiple_residents_are_persisted_as_separate_records`

**What it verifies:** The test verifies that two different Residents can be saved in the database as separate records. It checks that they receive different IDs and that their individual names and statuses are preserved after retrieving them.

**Why I chose this scenario:** I chose this scenario because a persistence system should be able to store multiple residents without one record overwriting or mixing with another. This tests an important risk that is different from simply saving and retrieving one Resident.

## Tools and References Used

* **Visual Studio Code** — used to edit the Python source files and tests.
* **PowerShell** — used to run Git, Flask, and pytest commands.
* **Python** — used to implement the Resident persistence functionality.
* **Flask** — used for the existing web application.
* **SQLite** — used as the local database.
* **pytest** — used to create and run automated tests.
* **Git and GitHub** — used for branch-based development and version control.
* **Python/SQLite documentation and project instructions** — used as references for database connections, SQLite tables, and persistence behavior.
* **AI coding assistant (ChatGPT)** — helped me understand the T03 requirements, troubleshoot project structure and testing issues, design the repository and database implementation, and review the automated tests. I made the final implementation decisions based on my project's existing structure and requirements.
