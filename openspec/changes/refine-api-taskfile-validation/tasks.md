# Tasks

- [x] Create OpenSpec change for approved refinement.
- [x] Add `GET /api/rotate` contract and implementation.
- [x] Remove root metrics routes and expose canonical `/api/metrics/*` paths only.
- [x] Add tracked `Taskfile.yml` and remove Makefile-centered workflow references.
- [x] Keep source validation strict with timeout and concurrency in CI/task/docs.
- [x] Move coverage enforcement out of global pytest addopts.
- [x] Fix CLI xdist lock isolation without disabling production locking.
- [x] Update credential URL tests to reject malformed URL credentials while allowing explicit empty fields.
- [x] Redact proxied request `proxy_used` values.
- [x] Preserve explicit empty credential objects.
- [x] Preserve `socks5h` protocol semantics in model and API validation.
- [x] Make pytest-xdist parallelism explicit instead of global.
- [x] Collapse CI coverage threshold enforcement into one explicit coverage command.
- [x] Run focused validation commands and record any remaining blockers.
