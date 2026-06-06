## MODIFIED Requirements

### Requirement: Active documentation framework

ProxyWhirl SHALL treat the Next.js + Fumadocs site under `web/` as the active
published documentation framework.

#### Scenario: Docs generation runs

- **WHEN** maintainers regenerate docs
- **THEN** they run `pnpm --dir web run docs:generate`
- **AND** generated reference pages are written under `web/content/docs/generated/`
- **AND** generated data is written under `web/content/generated/`

#### Scenario: Legacy docs are referenced

- **WHEN** maintainers use `docs/Makefile`
- **THEN** the build delegates to the active `web/` docs build
- **AND** `docs/source/` is not presented as the active published docs framework

### Requirement: Public proxy-list assets

Documentation generation SHALL mirror documented proxy-list artifacts from
`docs/proxy-lists/` into `web/public/proxy-lists/`.

#### Scenario: Proxy-list assets are mirrored

- **WHEN** `pnpm --dir web run docs:generate` runs
- **THEN** `README.md`, `metadata.json`, `stats.json`, `proxies.json`,
  `proxies-rich.json`, `all.txt`, `http.txt`, `https.txt`, `socks4.txt`, and
  `socks5.txt` are copied when present
- **AND** the public website asset directory reflects the same README wording as
  the source proxy-list asset directory

### Requirement: Production-readiness documentation

Maintainer-facing docs SHALL document zero-warning production gates across local
docs, CLI, source validation, package, and remote CI surfaces.

#### Scenario: Maintainer checks production readiness

- **WHEN** a maintainer reads the operations docs or agent instructions
- **THEN** they can find commands for docs generation, docs lint, docs tests,
  docs build, strict source validation, CLI smoke checks, API health/readiness
  smoke checks, and GitHub Actions log marker scans
- **AND** optional Codecov upload is distinguished from required local coverage
  threshold enforcement

### Requirement: API storage lifecycle

ProxyWhirl API startup SHALL initialize configured SQLite storage before loading
proxies from that storage.

#### Scenario: API starts with an empty configured database

- **WHEN** `PROXYWHIRL_STORAGE_PATH` points to a new SQLite database path
- **THEN** API lifespan initializes the storage schema before loading proxies
- **AND** startup does not log a load-failure warning for missing storage tables
- **AND** `/api/ready` can report successful readiness after startup
