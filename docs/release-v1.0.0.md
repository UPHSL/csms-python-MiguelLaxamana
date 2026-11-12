# CSMS v1.0.0 Release Notes

## 1. Release Information

- Application: Community Services Management System (CSMS)
- Version: 1.0.0
- Release type: Final system release
- Developer: Miguel D. Laxamana
- GitHub: MiguelLaxamana
- Branch: `feature/t16-final-release`

## 2. Release Summary

This release establishes CSMS version 1.0.0 and prepares the existing
resident management, service request management, and dashboard features
for final release.

No new major application feature was introduced.

## 3. Release Changes

- Updated the authoritative application version to `1.0.0`.
- Verified that `/health` returns the application name, healthy status,
  and release version.
- Added a global Flask template context processor for application metadata.
- Added a visible `CSMS v1.0.0` footer to operational templates.
- Added an integration test covering resident registration, service
  request submission, status transitions, and persisted final state.
- Strengthened automated health endpoint assertions.

## 4. Automated Verification

- T15 baseline: 191 tests passed.
- T16 integration test: 1 passed.
- T16 full regression: 192 passed on two consecutive runs.
- Health endpoint: HTTP 200 with version `1.0.0`.
- `git diff --check`: no errors.

## 5. Manual Verification

Automated checks do not replace the required manual acceptance checks.
Startup, browser rendering, navigation, resident operations, service
request operations, dashboard behavior, and read-only behavior must be
confirmed in the running application before release approval.

## 6. Known Limitations

- The T15 readiness document contains manual scenarios that were
  pending or partially verified. Those checks must not be treated as
  completed without evidence.
- Production deployment must provide `CSMS_SECRET_KEY` through the
  environment and use an appropriate production configuration.

## 7. Release Status

The automated T16 regression checks passed. Final release approval,
manual acceptance, pull request review and merge, release tagging,
and GitHub Release publication remain to be completed.
