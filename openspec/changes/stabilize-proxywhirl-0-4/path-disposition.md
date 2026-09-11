# Path Disposition Ledger

This ledger binds the exact initial dirty inventory to deterministic ownership
rules without opening protected-name files. It is evidence for B0, B1, B5, and
J1; it does not grant commit, publication, deployment, or secret access.

## Recovered baseline

The complete initial expanded status was recovered from the session event at
`2026-08-12T21:40:48.985Z` in the local rollout ledger. The event contains the
literal output between `UNTRACKED_STATUS` and `CHECK_IGNORES`.

| Evidence | Result |
| --- | --- |
| Local branch / HEAD | `main` / `040fa6a001097bf21828687439a3ba206066a08c` |
| Initial collapsed | 310 records: 201 modified, 16 deleted, 93 untracked |
| Initial expanded | 327 paths: 201 modified, 16 deleted, 110 untracked files |
| Initial expanded status SHA-256 | `519e25353d77c89f9fe9557a49d8ae6889b7abf12c9e19bc98f5adbd8640aaf3` |
| Canonical sorted path-name SHA-256 | `52ac50293767aba54cd9ffec558feb2a3dc9fa11d831c6b93fceeaef7a7cf095` |
| Attribution-union SHA-256 | `a5615778a91fb0d33acbe7b206146615a32a98507ae76732cb34076736e8ee58` |

The recovered attribution union contains 427 rows: one header and 426 unique
paths representing the 327-path initial set union the 424-path reconciliation
snapshot. It records old status, current status, membership, lane, and exactly
one disposition for every row.

## Reconciliation snapshot

At `2026-08-13T00:16:34-04:00`, the expanded candidate contained 424 paths:
262 modified, 21 deleted, and 141 untracked. Comparison with the recovered
baseline produced:

- 325 original paths retained;
- 99 paths added by attributable implementation, test, docs, workflow,
  deployment, dependency, and control-plane writers;
- two departed paths, both excluded Terraform provider-cache artifacts;
- three retained Kubernetes paths changed from modified to intentionally
  deleted: `hpa.yaml`, `role.yaml`, and `service-external.yaml`;
- exact arithmetic: modified `201 + 64 - 3 = 262`, deleted
  `16 + 2 + 3 = 21`, untracked `110 + 33 - 2 = 141`.

## Mutually exclusive disposition rules

Rules are evaluated top to bottom. The first match owns the path, so every
initial and current path has exactly one disposition.

| Priority | Match | Disposition | Owner and constraint |
| ---: | --- | --- | --- |
| 1 | Terraform provider-cache paths under `deploy/terraform/.terraform/` | Exclude local cache | Never integrate, package, scan as source, or use as release evidence. |
| 2 | Secret- or credential-named deployment templates and credential-manager code/tests | Preserve unopened | Only path/status metadata is used by this ledger; ordinary writers do not open or reassign these paths. |
| 3 | Script-owned generated MDX/JSON/OpenAPI and `web/public/llms.txt` | Regenerate through docs owner | Generator output only; never hand-edit. |
| 4 | Other `web/**`, docs source, and documentation assets | Docs steward or generator owner | Source changes precede one serialized generation and a second-run drift check. |
| 5 | `tests/**` | Assurance owner by subsystem | Test writers follow the corresponding product owner and cannot rewrite shared snapshots concurrently. |
| 6 | `proxywhirl/**` and `alembic/**` | Runtime owner by module | Package facade, storage/migration, API, MCP, CLI, and runtime state-machine locks remain serialized where shared. |
| 7 | `.github/**`, Docker/Compose, deployment manifests, dependency locks, and release metadata | Serialized release integrator | One writer per workflow, manifest, dependency-lock, and release-metadata family. |
| 8 | `openspec/**` and goal/evidence ledgers | Control-plane ledger owner | Evidence and scope only; no product behavior is inferred from a checked box. |
| 9 | Remaining root files | Root integrator review | Reconcile public prose, instructions, task runner, ignore rules, and shared metadata after subsystem writers release. |

Disposition counts for the 424-path reconciliation snapshot are:

| Disposition | Paths |
| --- | ---: |
| Runtime owner by module | 146 |
| Assurance owner by subsystem | 104 |
| Docs steward or generator owner | 94 |
| Regenerate through docs owner | 7 |
| Serialized release integrator | 46 |
| Control-plane ledger owner | 14 |
| Root integrator review | 8 |
| Protected preserve-unopened | 5 |
| Exclude local cache | 2 departed paths |

The eight current, non-departed dispositions total 424. Departed provider-cache
paths remain in the union solely to prove their intentional exclusion.

## Final pre-assurance recount

After implementation writers released at `2026-08-13T01:09:31-04:00`, the
candidate contained 406 collapsed records (279 modified, 24 deleted, 103
untracked) and 445 expanded paths (279 modified, 24 deleted, 142 untracked
files). The expanded increase from the 424-path reconciliation snapshot is 21
attributable source/test/docs/control-plane paths produced by the remaining
compatibility, redaction, health-monitor, documentation, and harness writers.
No path is staged.

| Final snapshot evidence | SHA-256 |
| --- | --- |
| Expanded porcelain status | `475b50b3bba0caf32820e7e2867ea9170a37af3b27e8d42e4d7efb386249fdf5` |
| Collapsed short status | `66195bc7b21bd4193add7f70edf9adcd1f8d8c0fa59d8326c13f35caf1ad74d9` |
| Sorted tracked-diff path names | `0ff59ff118646106312e4210a6666c5bfe84e97db3a38d06455bacd2e0fc1cf5` |
| Sorted untracked source path names | `dd9647d00f376bd65278aa2ee3901302d353602de2ff72154d8444a1c13c8cb2` |

The deterministic priority rules above cover the full 445-path final snapshot;
the earlier per-disposition counts remain an auditable mid-program snapshot,
not the final candidate count. Final generated docs may alter statuses in place
but must not introduce an unattributed source path.

## Instruction and writer mapping

- Root instructions apply to every path.
- Nested `AGENTS.md` files further constrain `docs/`, `proxywhirl/api/`,
  `proxywhirl/cache/`, `proxywhirl/mcp/`, `proxywhirl/models/`,
  `proxywhirl/rotator/`, `proxywhirl/strategies/`, `tests/`, and `web/`.
- The ownership queue is package/facades, configuration/storage/migrations,
  runtime state, API/MCP/CLI, dependency/workflows/deployment, then docs and
  generated output. Proxy-list churn is isolated last.
- Each owner reports files, commands, exit codes, counts, warnings, residual
  risk, and lock release before a dependent owner starts.

## Final post-assurance snapshot

After the final compatibility repairs, deterministic docs generation, release
workflow ordering change, and all local assurance lanes, the candidate still
contains 406 collapsed records and 445 expanded paths. The counts are unchanged
from the pre-assurance recount, but the path-name hashes below supersede the
earlier pre-assurance name-only hashes because final attributable files changed
status in place. No path is staged.

| Final evidence | SHA-256 |
| --- | --- |
| NUL-delimited collapsed porcelain | `762dd8d87d7913435f94983e0d2d459214a72ec1c7ee9d83edaf0ed4a2673d08` |
| NUL-delimited expanded porcelain | `65ecb516d65e122679fd117614fdfb6b2db57ba2141f3f615290b7714c839932` |
| Newline-delimited collapsed porcelain | `66195bc7b21bd4193add7f70edf9adcd1f8d8c0fa59d8326c13f35caf1ad74d9` |
| Newline-delimited expanded porcelain | `475b50b3bba0caf32820e7e2867ea9170a37af3b27e8d42e4d7efb386249fdf5` |
| Sorted tracked-diff path names | `96c7ac11cfa82433989f8108622b4ca7d64e0f328cb42153089b922d8817e4c3` |
| Sorted untracked source path names | `a43a91c93647bac5f3852e3f6316fa14612ee1c85c70d81628cc8a2adbb72a8e` |
| Build-authoritative protected-filtered source manifest before evidence-only ledger edits (809 files) | `a886b3970f881e179fa5955fbf77e9d87a5efa328524996c6bab59a4c8103035` |

Final ownership accounting remains deterministic under the priority rules in
this ledger. Assurance created only ignored coverage/build/runtime artifacts or
owner-validated temporary directories; validated temporary directories were
removed. The pre-existing ignored `build/`, `dist/`, and
`proxywhirl.egg-info/` directories were preserved and excluded.

## Protected-path audit

The protected-name disposition contains five source paths. Their names were
classified from Git metadata only; this ledger neither reads nor reproduces
their contents. Environment files, private keys, local databases, backup files,
`.venv/`, build artifacts, coverage output, and browser/cache output remain
outside the candidate source inventory even when ignored artifacts exist in the
checkout.

## Resumed-wave final recount

After the lifecycle/resource, architecture-research, benchmark, docs, security,
deploy-static, and local gate waves completed, the candidate contains 410
collapsed records (`282 M`, `24 D`, `104 ??`) and 452 expanded paths (`282 M`,
`24 D`, 146 untracked files). The index remains empty. The seven-path increase
from the earlier 445-path snapshot is attributable to three OpenSpec inventory
artifacts, the modernization benchmark, and retained source/test lifecycle
repairs; no protected or local-cache path became a candidate input.

| Resumed final evidence | SHA-256 |
| --- | --- |
| NUL-delimited collapsed porcelain | `36fbf97fea6bd0375851956a2b4315acbd5c55554f2e12be36c91f7e33c88ca9` |
| NUL-delimited expanded porcelain | `05aa0c5525803d09c97b7556a99e8024fb220a89e3d031aebe13dd1073abd8bd` |
| Newline-delimited collapsed porcelain | `235cbfbec5d16f8442a99a79ddc987192a92b23589216c06e5aa48f292ec823b` |
| Newline-delimited expanded porcelain | `90fd1c738823fc3d515b76f14c418dbf385835ce5156f21a2e45449707804187` |
| Sorted tracked-diff path names | `1eaa577763e45bbd2b357e9208b72afe67ffd2843e772065046d1aaf810497e2` |
| Sorted untracked source path names | `737beae7b9335484ec8d798a9226b29ba66e8485625cb595bc74176d5dfcdffd` |
| Protected-filter v1 copy manifest (813 files) | `356e63ad991bead55ac4b49827d493d8d757eb84d27ddab845d0366c21328dfc` |
| Frozen/live sdist source inputs (158 files) | `5256ee0f0c36c3061ab509c9fa7e1853d1dd669b7b6c154b8e94c5d3dd361eb7` |

These status hashes identify the final local source surface; they are not a
commit/tree SHA and therefore cannot satisfy exact-SHA remote or release gates.

## Final control-plane closeout recount

After the API/deployment compatibility repair, final prose regeneration, local
container/Compose assurance, fresh artifact installation, and release-evidence
reconciliation, the candidate contains 411 collapsed records (`283 M`, `24 D`,
`104 ??`) and 453 expanded paths (`283 M`, `24 D`, 146 untracked files). The
single-path increase is the attributable release-operations source-doc update;
the index remains empty.

| Closeout evidence | SHA-256 |
| --- | --- |
| NUL-delimited collapsed porcelain | `747072f2fcdffb0195da33c7956913b6dfb4a956112da8a099dab2c468c73695` |
| NUL-delimited expanded porcelain | `32fb08ce8d3b17c56dc0eebcbace8368979256fe7fbe0401e141fc9f0dbd80bc` |
| Protected artifact copy (812 files) | `610e6cfa8a8afc8630a64a75b88c176019fa099eb141356506d7ec99e2fba6e5` |
| Frozen/live package inputs (142 files) | `56121e9ffada5b2c0e3e3023e69ee59e92c021e959ff54a1f94d0cd896b61882` |
| Frozen/live sdist inputs (158 files) | `41e0edf92642ab21ed84ef7b681ce3325df09182122cc210bdcb45b92ba591a0` |

The path/status hashes remain control-plane identifiers, not a commit/tree SHA.
The twelve unchecked leaves in `tasks.md` therefore retain their authority,
acceptance, deferral, or exact-SHA prerequisites.
