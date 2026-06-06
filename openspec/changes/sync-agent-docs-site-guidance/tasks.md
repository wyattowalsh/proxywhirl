# Tasks

## Change Control

- [x] Create OpenSpec change artifacts before docs-generation behavior edits.
- [x] Snapshot branch and dirty worktree state before mutation.

## Documentation

- [x] Refresh root and nested agent instructions.
- [x] Replace README badges with ShieldCN badges and verify badge endpoints.
- [x] Update active Fumadocs pages for production gates, CLI smoke checks, CI
      assurance, and proxy-list website verification.
- [x] Synchronize proxy-list README wording between source and public assets.
- [x] Update docs generation so documented public proxy-list artifacts are
      mirrored consistently.
- [x] Initialize API SQLite storage before loading it to remove empty-temp-DB
      startup warnings.

## Verification

- [x] Validate OpenSpec artifacts.
- [x] Run `pnpm --dir web run docs:generate`.
- [x] Run `pnpm --dir web run lint`.
- [x] Run `pnpm --dir web run test:run`.
- [x] Run `pnpm --dir web run build`.
- [x] Run focused API lifespan tests.
- [x] Verify ShieldCN badge URLs return SVG successfully.
- [x] Run strict source validation when network conditions allow.
