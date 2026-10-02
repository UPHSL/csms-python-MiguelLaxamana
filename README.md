[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=24293594&assignment_repo_type=AssignmentRepo)
Community Services Management System
# Community Services Management System

The Community Services Management System (CSMS) is the semester-long software development project for the Programming Languages Laboratory.

This repository contains the Python implementation of CSMS using Python and Flask.

Students will incrementally develop this application throughout the semester using professional software development practices including Git, GitHub, feature branches, automated testing, code review, Pull Requests, documentation, and incremental software delivery.

## Technology Stack

* Python 3.10 or later
* pip
* Flask 3
* Jinja2
* pytest
* Flask Test Client
* Git
* GitHub

## Important

This repository is a starter project.

Some models, repositories, services, utilities, controllers, and other components may intentionally contain minimal implementations or placeholders.

**Do not attempt to complete future functionality unless it is required by the current Moodle activity or development ticket.**

Students are expected to implement the system incrementally throughout the semester.

## Current Starter Scope

The starter repository currently provides:
* Flask application structure
* Jinja2 starter interface
* `/health` JSON endpoint
* HTTP 404 handling
* automated application tests
* layered application architecture
* Git workflow documentation
* Pull Request template

The starter does not yet provide completed:
* Resident management
* Service Request processing
* persistence
* authentication
* Resident user interface
* Resident API
* advanced validation
* other future CSMS functionality

These features will be introduced through later tickets.

## Prerequisites

Before starting, verify that the following tools are installed:

```bash
python --version
pip --version
git --version
```

The project requires:
* Python 3.10 or later
* pip

The required dependencies are declared in `pyproject.toml`.

Students may use an appropriate editor or IDE such as:
* Visual Studio Code
* PyCharm
* another Python-compatible development environment

## Initial Setup

After cloning your GitHub Classroom repository, open a terminal inside the project directory.

### 1. Verify Python and Virtual Environment

```bash
python --version
pip --version
```

Create and activate a virtual environment (recommended):

**Windows PowerShell:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

Install the project and its dependencies in editable mode:
```bash
pip install -e .
```

*(Note: The `venv/` directory is intentionally not stored in Git and must be generated locally).*

### 3. Run the Automated Tests

```bash
pytest
```

All baseline tests should pass before beginning a development activity.

### 4. Start the Application

```bash
flask run
```

The application normally starts at:
`http://127.0.0.1:5000`

### 5. Verify the Health Endpoint

While the application is running, open:
`http://127.0.0.1:5000/health`

The endpoint should return JSON similar to:
```json
{
  "status": "ok",
  "application": "Community Services Management System",
  "version": "0.1.0"
}
```

### 6. Development Debug Mode

During development, you may use:

```bash
flask run --debug
```

This starts the application with the interactive debugger and automatic reloader enabled.

## Automated Testing

This project uses `pytest` as its testing framework.

Run the complete test suite using:
```bash
pytest