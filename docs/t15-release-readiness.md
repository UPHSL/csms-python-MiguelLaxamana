# T15 - System Hardening and Regression Testing

## 1. Developer Information

- **Name:** Miguel D. Laxamana
- **GitHub Username:** MiguelLaxamana
- **Tech Stack:** Python, Flask, SQLite, HTML, CSS, JavaScript, pytest
- **T15 Branch:** `feature/t15-system-hardening`

## 2. Release Candidate Baseline

The T14 implementation was successfully merged into the main branch before T15 development began.

The application was manually started and the following routes were verified:

| Verification | Result |
|---|---|
| Application startup | PASS |
| Health endpoint (`/health`) | PASS - HTTP 200 |
| Dashboard (`/dashboard`) | PASS - HTTP 200 |
| Resident Management (`/residents`) | PASS |
| Service Request Management (`/service-requests`) | PASS - HTTP 200 |
| Pre-T15 regression tests | PASS - 186 tests |

## 3. Hardening Changes

| Area | Issue or Risk Found | Action Taken | Files Changed | Test/Evidence |
|---|---|---|---|---|
| Query/database safety | Reviewed recent-request limit enforcement and SQL parameter binding. | Confirmed the existing T14 implementation validates the limit and uses parameterized SQL `LIMIT ?`. No T15 code change was required. | `src/csms/repositories/service_request_repository.py` (reviewed; unchanged) | Dashboard tests passed, including the seven-request/five-result test. |
| Full regression behavior | Reviewed existing T01-T14 functionality. | No additional defect identified. | Existing application files | Full test suite passed twice. |
| Invalid/missing input | Reviewed invalid input handling. | No additional defect identified. | Existing application files | T15 malformed-date test. |
| Persistence integrity | Reviewed database persistence and rejected mutations. | No additional defect identified. | Existing repositories and tests | T15 persistence tests. |
| HTTP and mutation safety | Reviewed route responses and mutation behavior. | No additional defect identified. | Existing routes and tests | T15 rejected-mutation test. |
| Workflow/lifecycle | Reviewed resident and service request workflows. | No additional defect identified. | Existing services and tests | T15 cross-feature and repeated-transition tests. |
| Interface/navigation | Reviewed dashboard, resident, and service request routes. | No additional defect identified. | Existing templates and routes | Baseline route verification. |
| Test reliability | Added focused regression and hardening tests. | Added five T15 tests. | `tests/test_t15_hardening.py` | Five tests passed. |
| Repository/release hygiene | Reviewed debug statements, unfinished markers, database ignore rules, and SQL parameter binding. | No additional defect identified during review. | Existing repository files | Debug-marker scan and `git diff --check`. |

## 4. Five New T15 Hardening Tests

### 4.1 Malformed Submission Date

**Test:** `test_malformed_submission_date_returns_400_without_persistence`

- Verifies that malformed request dates receive HTTP 400.
- Confirms that no service request is persisted.
- Adds protection against invalid input.

### 4.2 Rejected Status Mutation

**Test:** `test_rejected_status_mutation_preserves_entire_request`

- Verifies that an invalid status update does not modify the stored request.
- Compares the record before and after the rejected mutation.
- Protects persistence integrity.

### 4.3 Read-Only Route Safety

**Test:** `test_read_only_routes_preserve_resident_and_request_records`

- Checks dashboard, resident, search, service request, and detail GET routes.
- Confirms that resident and request records remain unchanged.
- Protects read-only operations from unintended database changes.

### 4.4 Resident Deactivation and Dashboard Integration

**Test:** `test_deactivation_updates_dashboard_and_blocks_new_requests`

- Verifies that deactivation updates dashboard statistics.
- Confirms that inactive residents cannot submit new requests.
- Tests integration across multiple application features.

### 4.5 Repeated Status Transition

**Test:** `test_repeating_same_status_transition_preserves_current_record`

- Verifies that repeating an existing status transition does not modify the record again.
- Confirms that the current status remains unchanged.
- Protects workflow consistency.

## 5. Full Regression Test Results

Command:

```powershell
python -m pytest -q
```

| Run | Result | Duration |
|---|---|---|
| Run 1 | 191 passed, 0 failed | 5.21 seconds |
| Run 2 | 191 passed, 0 failed | 7.48 seconds |

Both consecutive regression runs completed successfully.

Additional test results:

- T15 hardening tests: 5 passed.
- Dashboard tests: 24 passed.

## 6. Manual Release Verification

Baseline application startup and route checks were completed. The following detailed scenarios were manually verified where possible.

| # | Scenario | Result |
|---|---|---|
| 1 | Valid and invalid resident registration, generated ID, Active status, persistence, and list presence. | PENDING |
| 2 | Valid and invalid resident update; verify ID and status remain unchanged after rejection. | PENDING |
| 3 | Resident deactivation, continued searchability, and repeated deactivation. | PENDING |
| 4 | Valid service request submission for an Active resident; verify generated ID, resident ID, and Pending status. | PENDING |
| 5 | Reject service request submission for missing or inactive residents without persistence. | PENDING |
| 6 | Service request listing, search, status filtering, combined filtering, and details. | PARTIAL - Listing and details verified; filters not fully tested. |
| 7 | Valid Pending -> In Progress -> Completed workflow and rejection of invalid Pending -> Completed transition. | PARTIAL - Valid workflow verified; invalid transition not manually tested. |
| 8 | Completed and Cancelled requests remain queryable and cannot transition again. | PASS |
| 9 | Dashboard reflects resident deactivation and service request status changes. | PARTIAL - Service request statistics verified; resident deactivation not manually tested. |
| 10 | Repeated dashboard, search, list, and detail GET requests do not modify database records. | PENDING |
| 11 | Missing resident and service request records are handled safely. | PENDING |
| 12 | Navigation between Dashboard, Residents, and Service Requests works correctly. | PENDING |

Resident deactivation was intentionally not performed on existing records because their test-data status could not be confirmed.

## 7. Repository Hygiene Review

| Check | Result | Notes |
|---|---|---|
| Debug output and breakpoints | PASS | Scan returned no matches for `print()`, `breakpoint()`, or `pdb.set_trace`. |
| TODO/FIXME markers | PASS | Scan returned no matches. |
| Temporary files and generated artifacts | REVIEWED | Unrelated files will not be included in the T15 commit. |
| Local database files | PASS | Local `.db` files are ignored through the existing `*.db` rule. |
| Abandoned commented code | REVIEWED | No release-related changes made. |
| Secrets and credentials | REVIEWED | Development and test secret values were identified. Production must use an environment-provided secret. |
| Navigation | REVIEWED | Main application routes were checked. |
| SQL parameter binding | PASS | User-controlled query values use parameterized SQL. The existing recent-request query uses `LIMIT ?`. |
| Patch validation | PASS | `git diff --check` returned no errors. |

The unrelated pre-existing untracked folder `csms-python-MiguelLaxamana/` was intentionally left untouched and must not be included in the T15 commit.

## 8. Known Limitations

The application configuration contains a development-only fallback secret. Production deployment must provide `CSMS_SECRET_KEY` through the environment and use an appropriate production configuration.

Some detailed manual release verification scenarios remain pending or partially verified.

## 9. Release Candidate Statement

**NOT YET READY FOR T16 FINAL EXAM.**

The automated regression suite passed twice, and all five T15 hardening tests passed.

The existing recent-request limit implementation was reviewed and verified through regression testing.

Final readiness remains pending completion of the remaining manual release verification, documentation of the results, and successful review and merge of the T15 pull request.