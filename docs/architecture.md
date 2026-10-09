# CSMS Python Application Architecture

## Purpose

This document describes the intended architectural organization of the Python implementation of the Community Services Management System.

The architecture provides structure for development throughout the semester.

Some components may initially contain placeholders and will be implemented as activities introduce their responsibilities.

## Technology

The application uses:
* Python
* Flask
* Jinja2 (Templates)
* pytest
* Flask Test Client

## Project Structure

```text
src/csms/
├── config.py
├── database.py
├── main.py
├── __init__.py
├── models/
├── repositories/
├── services/
├── ui/
├── utils/
├── static/
│   └── css/
└── templates/

tests/
├── conftest.py
└── test_smoke.py
```

## Architectural Principle

CSMS separates responsibilities instead of placing all application logic in routes or controllers.

A typical request may involve:
1. A route receives an HTTP request.
2. A controller/view function handles the HTTP interaction.
3. A service coordinates application or business behavior.
4. A repository performs persistence-related operations when required.
5. A model represents domain information.
6. The controller returns an HTTP response or renders a Jinja2 template.

Not every activity will use every layer.

Students should implement only the layers required by the assigned ticket.

## Application Entry Points

### `src/csms/__init__.py`

Responsible for creating and configuring the Flask application using the Application Factory pattern.

Typical responsibilities include:
* creating the Flask application instance
* registering Blueprints (routes)
* configuring templates and static folders
* initializing extensions

Application configuration that must be testable should generally remain separate from starting the network server.

### `src/csms/main.py`

Responsible for starting the HTTP server (or serving as the WSGI entry point).

Keeping server startup separate from application creation allows automated tests to use the Flask application without opening a real network port.

## Configuration

Location:
`src/csms/config.py`

Contains shared application configuration.

Examples may include:
* application name
* version
* environment-related application values

Do not place unrelated business logic in configuration files.

## UI, Routes, and Controllers

Location:
`src/csms/ui/`

In this Python/Flask architecture, routing and controller logic are often grouped together in modules like `routes.py` using Flask Blueprints.

Typical responsibilities include:
* mapping incoming HTTP paths and methods to application behavior
* reading request information
* invoking application services
* selecting HTTP status codes
* returning JSON
* rendering templates

Routes and view functions should remain concise. Complex business logic should not be implemented directly inside route definitions.

## Services

Location:
`src/csms/services/`

Services coordinate application operations and business behavior.

As the application grows, services help keep UI routes focused on HTTP responsibilities.

Examples may include:
* `resident_service.py`
* `request_service.py`

Some service files may initially contain placeholders.
Do not implement them until required by a ticket.

## Repositories

Location:
`src/csms/repositories/`

Repositories provide an abstraction for data access when persistence is introduced.

Example:
* `resident_repository.py`

Repository responsibilities may include:
* storing data
* retrieving data
* updating data
* removing data

Persistence behavior should not be duplicated throughout the application.
Do not implement persistence before the corresponding ticket is released.

## Models

Location:
`src/csms/models/`

Models represent important domain concepts.

Examples include:
* `resident.py`
* `service_request.py`

A model should represent meaningful information and behavior from the CSMS problem domain.

Students should not add speculative properties or functionality simply because they may be useful later.

Implement only the requirements defined by the current ticket.

## Utilities

Location:
`src/csms/utils/`

Utilities contain small reusable supporting functions.

Examples:
* `validators.py`
* `logger.py`

Do not move major business processes into utility files merely to avoid creating an appropriate service or model.

## Templates

Location:
`src/csms/templates/`

Contains HTML/Jinja2 templates used to render HTML responses.

The user interface will evolve through later activities.
Do not implement future UI requirements before their corresponding tickets are released.

## Static Assets

Location:
`src/csms/static/`

Contains browser-accessible static resources such as:
* CSS
* images
* client-side assets

## Tests

Location:
`tests/`

The starter repository currently uses:
* `tests/test_smoke.py`
* `tests/conftest.py` (for test fixtures)

The project uses `pytest` and the Flask Test Client.
The test structure may evolve as the application becomes larger.

Students should follow the testing structure established by the current repository and ticket rather than reorganizing it without a requirement.

## Request Flow

A typical future request flow may be:
1. HTTP Request
2. Route / Controller (`ui/routes.py`)
3. Service
4. Repository
5. Model / Data Source
6. HTTP Response or Jinja2 Template

The sequence should be understood as a responsibility flow, not as a requirement that every request must use every layer.

For simple endpoints, fewer layers may be appropriate.

## Current Endpoints

The starter application provides:
* `GET /`
* `GET /health`

Unknown routes return HTTP 404.

## Domain Models

A domain model represents meaningful concepts from the application problem domain.

Students should distinguish between:
* representing an object
* validating an object
* processing an object
* persisting an object
* retrieving an object
* displaying an object

These are related but different responsibilities.

A ticket that introduces a domain model does not automatically require persistence, controllers, routes, or user interface functionality.

## Validation

Validation protects the application from invalid input.
Validation requirements will be introduced progressively.

Place validation in the location required by the current architecture and activity rather than duplicating validation logic throughout the application.

## Persistence

Database or other persistence mechanisms will be introduced when required by the semester activities.

The existence of a repository or model file does not mean persistence is already implemented.

## Dependency Direction

Prefer clear responsibility boundaries.

For example:
* UI Route depends on Service
* Service depends on Repository
* Repository works with persistence or data
* Model represents domain information

Avoid unnecessary coupling between unrelated components.

## Testing Architecture

Every implemented requirement should be verifiable.

Students should create or update automated tests as instructed by each activity.

Before submitting work, run:
```bash
pytest
```

The goal is not merely to make tests pass.
Students should understand what each test verifies and why the behavior is required.

## Architecture Evolution

This architecture is intentionally introduced progressively.

Do not create unnecessary:
* routes
* repositories
* services
* database structures
* endpoints
* middleware
* templates
* utilities

before they are required.

The repository should evolve together with the semester activities.