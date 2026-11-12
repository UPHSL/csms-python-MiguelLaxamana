# T16 - Final System Release and Development Checkpoint

## 1. Developer Information

- Name: Miguel D. Laxamana
- GitHub Username: MiguelLaxamana
- Tech Stack: Python, Flask, SQLite, HTML, CSS, JavaScript, pytest
- T16 Branch: `feature/t16-final-release`
- Release Version: `1.0.0`

## 2. Development Checkpoint

The T16 work was started from the updated `main` branch after the
T15 pull request had been merged.

The application version was updated centrally in configuration.
The version is exposed to templates through a Flask context processor
and displayed in the operational page footers.

## 3. Integration Verification

The new test `test_t16_resident_to_completed_request_workflow` verifies:

1. Resident registration through the registration service.
2. Service request submission through the Flask route.
3. Initial Pending status and resident association.
4. Transitions from Pending to In Progress to Completed.
5. Persisted request details and final status.
6. Continued persistence of the Active resident.

The test uses the isolated database fixture.

## 4. Automated Test Results

| Verification | Result |
|---|---|
| T15 baseline suite | 191 passed |
| T16 integration test | 1 passed |
| T16 full regression run 1 | 192 passed |
| T16 full regression run 2 | 192 passed |
| Health endpoint version | 1.0.0 |
| Patch whitespace check | Passed |

## 5. Manual Acceptance

Manual acceptance must be completed against the running application.
Record actual results for startup, health, UI version display, dashboard,
resident CRUD and deactivation, service request workflows, invalid
submissions, read-only behavior, missing records, and navigation.

Do not mark unperformed checks as passed.

## 6. Known Limitations and Follow-up

The merged T15 readiness document still records outstanding manual
verification scenarios. The T15 readiness prerequisite therefore needs
a documented follow-up before final release approval.

Production deployment requires an environment-provided `CSMS_SECRET_KEY`
and production-appropriate configuration.

## 7. Git and Release Checkpoint

- Required release commit message: `release: prepare csms v1.0.0`
- Pull request title: `T16 - Final System Release and Development Checkpoint`
- Target branch: `main`
- Required release tag: `v1.0.0`
- GitHub Release title: `CSMS v1.0.0`

Pull request review, merge, tag creation, and GitHub Release publication
must be recorded after they actually occur.
