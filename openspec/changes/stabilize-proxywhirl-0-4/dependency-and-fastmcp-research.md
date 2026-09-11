# Dependency Remediation and FastMCP 4 Research

## Scope and decision

This artifact closes the research deliverables for tasks **2.22 / F6.2** and
**5.7 / M4.1**. It evaluates the frozen candidate dependency graph and the
current upstream FastMCP 4 prerelease using primary upstream security
advisories, release notes, changelogs, documentation, and package metadata.
It does not change the manifest, lock, runtime, generated documentation, or
product code.

The dependency remediation is compatible with the project's Python `>=3.10`
floor. The lock resolves all five packages beyond the combined fixed floors,
and the relevant direct and transitive constraints are coherent. That is
necessary evidence, but release clearance still comes from the exact-candidate
security and behavioral gates already defined in `validation-matrix.md`.

**FastMCP decision: defer the major upgrade.** The current v4 release is
`4.0.0b1`, explicitly a beta, while the candidate deliberately constrains
`fastmcp<4` and `mcp<2`. FastMCP 4 requires MCP SDK 2, introduces `mcp-types`
and `httpx2`, changes typed middleware request/result boundaries, and expands
the protocol modes that must be tested. The upgrade is not a bounded RC
dependency bump. It should be an atomic post-`0.4.0` OpenSpec change after a
stable v4 release, with no dual-version adapter in this candidate.

## Reproducible local snapshot

The pre-artifact snapshot was taken at `2026-08-13T06:43:33Z` in a shared,
actively changing worktree.

| Evidence | Result |
| --- | --- |
| Branch | `main` |
| HEAD | `040fa6a001097bf21828687439a3ba206066a08c` |
| Expanded status | 446 records: 0 index, 304 worktree, 142 untracked |
| Expanded status SHA-256 | `6328695b3c31ef1f7b6aec305a3b4c2fcafc65430a90ff688f1129da98cc21a0` |
| `pyproject.toml` SHA-256 | `a101f7b9ac72719a263bfe528b52dbb9a96d19aa23277bb692fb05b69cd80ded` |
| `uv.lock` SHA-256 | `ad05e616b819a5ef66692e0c4d64267ccd264e71026beae5d683f0a64c999ced` |
| Candidate version | `0.4.0rc1` |
| Project Python floor | `>=3.10` |

The following read-only commands supplied the local results. The status digest
is included because the expanded path list is noisy and can expose unrelated
work in a shared tree.

```console
$ date -u '+%Y-%m-%dT%H:%M:%SZ'
2026-08-13T06:43:33Z

$ git rev-parse HEAD
040fa6a001097bf21828687439a3ba206066a08c

$ git branch --show-current
main

$ git status --porcelain=v1 -uall | awk '
    { total++ }
    substr($0,1,1) != " " && substr($0,1,2) != "??" { index++ }
    substr($0,2,1) != " " && substr($0,1,2) != "??" { worktree++ }
    substr($0,1,2) == "??" { untracked++ }
    END { printf "total=%d index=%d worktree=%d untracked=%d\n",
                 total, index, worktree, untracked }'
total=446 index=0 worktree=304 untracked=142

$ git status --porcelain=v1 -uall | shasum -a 256
6328695b3c31ef1f7b6aec305a3b4c2fcafc65430a90ff688f1129da98cc21a0  -

$ shasum -a 256 pyproject.toml uv.lock
a101f7b9ac72719a263bfe528b52dbb9a96d19aa23277bb692fb05b69cd80ded  pyproject.toml
ad05e616b819a5ef66692e0c4d64267ccd264e71026beae5d683f0a64c999ced  uv.lock

$ uv lock --check
Resolved 250 packages in 13ms
```

The frozen closure was inspected with:

```console
$ uv export --locked --all-extras --all-groups --no-hashes \
    --no-emit-project --no-header --no-annotate
# 249 exact records; 238 unique distributions
```

The relevant exact records are:

```text
authlib==1.7.2
beautifulsoup4==4.14.3
cryptography==50.0.0
fastapi==0.136.1
fastmcp==3.4.7
fastmcp-slim==3.4.7
httpx==0.28.1
joserfc==1.7.4
mcp==1.29.0
pydantic==2.13.3
pydantic-settings==2.15.0
pyjwt==2.13.0
soupsieve==2.9.2
starlette==1.3.1
```

The default development sync is not the all-extras release closure:

```console
$ uv run python - <<'PY'
from importlib.metadata import PackageNotFoundError, version
for name in ("fastmcp", "mcp", "cryptography", "joserfc",
             "pydantic-settings", "PyJWT", "soupsieve"):
    try:
        print(f"{name}={version(name)}")
    except PackageNotFoundError:
        print(f"{name}=not-installed-in-base-sync")
PY
fastmcp=not-installed-in-base-sync
mcp=not-installed-in-base-sync
cryptography=50.0.0
joserfc=not-installed-in-base-sync
pydantic-settings=2.15.0
PyJWT=not-installed-in-base-sync
soupsieve=2.9.2
```

Consequently, this audit treats `uv.lock` plus the locked all-extras export as
the candidate authority. It does not infer FastMCP runtime compatibility from
the incomplete base sync.

## Five-package remediation

The known blocker was Security Scan run `31285534474`, Safety job
`93173499813`, at SHA `3a2222c47b589f36ce245fecd6f4dad9bc5f9147`:
11 findings across cryptography 47.0.0 (1), joserfc 1.6.4 (2),
pydantic-settings 2.14.0 (1), PyJWT 2.12.1 (5), and SoupSieve 2.8.3 (2).
The counts identify the release blocker; upstream advisories determine the
security floors.

| Package | Prior version/findings | Combined upstream fixed floor | Manifest floor | Locked | Python floor of lock | Resolution |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| cryptography | 47.0.0 / 1 | 48.0.1 | `>=50.0.0` | 50.0.0 | `>=3.9`, excluding 3.9.0/3.9.1 | Fixed and Python-compatible |
| joserfc | 1.6.4 / 2 | 1.6.8 | `>=1.6.8` | 1.7.4 | `>=3.10` | Fixed; lock adopts stricter 1.7 behavior |
| pydantic-settings | 2.14.0 / 1 | 2.14.2 | `>=2.14.2` | 2.15.0 | `>=3.10` | Fixed; lock adopts 2.15 settings changes |
| PyJWT | 2.12.1 / 5 | 2.13.0 | `>=2.13.0` | 2.13.0 | `>=3.9` | Fixed and Python-compatible |
| SoupSieve | 2.8.3 / 2 | 2.8.4 | `>=2.8.4` | 2.9.2 | `>=3.10` | Fixed; lock adopts 2.9 parser changes |

### cryptography

The upstream [GHSA-537c-gmf6-5ccf advisory](https://github.com/pyca/cryptography/security/advisories/GHSA-537c-gmf6-5ccf)
identifies CVE-2026-34180 in wheels from 0.5 through 48.0.0 and marks 48.0.1
patched. The issue is the OpenSSL version embedded in wheels; source builds use
the system OpenSSL and therefore require separate system-level assurance.
The upstream [changelog](https://cryptography.io/en/stable/changelog/) records
the OpenSSL 4.0.1 wheel update in 48.0.1, removal of Python 3.8 in 48, removal
of x86-64 macOS and 32-bit Windows wheels in 49, and additional behavior and
security changes in 50. The
[50.0.0 package metadata](https://raw.githubusercontent.com/pyca/cryptography/50.0.0/pyproject.toml)
requires Python `>=3.9` except 3.9.0/3.9.1 and declares `cffi>=2.0.0` on
non-PyPy plus `typing-extensions>=4.15.0` below Python 3.11.

The project directly sets `cryptography>=50.0.0`. The lock resolves 50.0.0,
with the expected `cffi` and conditional `typing-extensions` edges. joserfc and
the `PyJWT[crypto]` extra also converge on the same distribution. ProxyWhirl's
direct cryptographic calls are Fernet/MultiFernet credential and cache paths,
so the documented low-level algorithm changes are not presently reachable.
The material risks are packaging/platform coverage, the bundled-versus-system
OpenSSL distinction, and regression in encrypt/decrypt/key-rotation behavior.

Focused gates:

- run cache, storage, config, and utility crypto tests, including invalid key,
  wrong key, rotation, and redaction cases;
- install the all-extras wheel on the supported Python matrix, including Python
  3.10 and any Intel macOS runner still claimed by release metadata;
- retain exact-lock pip-audit/Safety-equivalent evidence, and separately inspect
  the system OpenSSL path if a source distribution is built.

### joserfc

The upstream [payload-size advisory](https://github.com/authlib/joserfc/security/advisories/GHSA-wphv-vfrh-23q5)
describes a `b64=false` JWS verification denial of service and marks 1.6.7 as
patched. The upstream [empty-HMAC-key advisory](https://github.com/authlib/joserfc/security/advisories/GHSA-gg9x-qcx2-xmrh)
affects versions through 1.6.7 and marks 1.6.8 patched. The combined floor is
therefore 1.6.8, not 1.6.7.

The upstream [changelog](https://jose.authlib.org/en/changelog/) records empty
OctKey rejection in 1.6.8. It also records that 1.7 drops Python 3.9 and changes
the default JWK export to public-only; 1.7.3 adds default `iss`, `sub`, and
`aud` claim validation and self-contained payload-size enforcement; and 1.7.4
rejects empty general-JWS signatures and invalid `encrypted_key` values. The
[1.7.4 metadata](https://raw.githubusercontent.com/authlib/joserfc/1.7.4/pyproject.toml)
requires Python `>=3.10` and cryptography `>=45.0.1`.

The project constraint is `joserfc>=1.6.8`; the lock resolves 1.7.4. It is
transitive through FastMCP server/auth components and Authlib rather than a
direct ProxyWhirl import. Python 3.10 is exactly the upstream floor. The main
runtime risk is intentional strictness at token, key, claim, and serialization
boundaries, especially in MCP authentication integrations.

Focused gates:

- exercise MCP missing, malformed, invalid, and valid credentials over a real
  client/transport, including fail-closed write classification;
- assert token/key failures remain redacted and map to the intended MCP errors;
- make deprecation and compatibility warnings fatal in the focused MCP run.

### pydantic-settings

The upstream [GHSA-4xgf-cpjx-pc3j advisory](https://github.com/pydantic/pydantic-settings/security/advisories/GHSA-4xgf-cpjx-pc3j)
affects `>=2.12,<2.14.2` and marks 2.14.2 patched. It addresses nested-secrets
directory traversal through symlinks and a size-limit bypass. The official
[2.14.2 release](https://github.com/pydantic/pydantic-settings/releases/tag/v2.14.2)
is the security release.

The lock goes further to 2.15.0. Its official
[release notes](https://github.com/pydantic/pydantic-settings/releases/tag/v2.15.0)
record that `case_sensitive` now applies consistently to init and config-file
sources, unresolved forward references warn, and strict non-JSON environment
values raise `ValidationError`. The
[2.15.0 metadata](https://raw.githubusercontent.com/pydantic/pydantic-settings/v2.15.0/pyproject.toml)
requires Python `>=3.10`, Pydantic `>=2.7.0`, python-dotenv `>=0.21.0`, and
typing-inspection `>=0.4.0`.

The project directly sets `pydantic-settings>=2.14.2`, and FastMCP/MCP also
depend on it. The lock's Pydantic 2.13.3 satisfies the transitive floor. The
upstream Python floor equals the project's. Runtime risk centers on settings
source precedence/casing, strict environment parsing, and new warnings—not on
the nested-secrets feature alone.

Focused gates:

- run configuration source-of-truth and config tests across init, TOML, and
  environment inputs, including case variants and invalid strict values;
- run CLI, API startup, and MCP settings initialization with warnings fatal;
- verify no secret directory or environment value is echoed in errors/logs.

### PyJWT

The official [2.13.0 changelog](https://pyjwt.readthedocs.io/en/stable/changelog.html#v2-13-0)
records the security fixes behind the prior five findings: binding permitted
algorithms to a `PyJWK`, blocking a public JWK from being reused as an HMAC
secret, restricting `PyJWKClient` URLs to HTTP(S), bounding `b64=false`
processing, and preserving the cached JWK set on refresh failure. It also
records empty HMAC-secret rejection and critical-header compliance. The
[2.13.0 metadata](https://raw.githubusercontent.com/jpadilla/pyjwt/2.13.0/pyproject.toml)
requires Python `>=3.9`; its `crypto` extra requires cryptography `>=3.4.0`.

The project constraint and lock are both 2.13.0. PyJWT is brought in as
`PyJWT[crypto]` by MCP 1.29.0 and converges on cryptography 50.0.0. ProxyWhirl
does not import it directly. Python 3.10 is supported. Runtime risk is stricter
algorithm/key/URI rejection and changed JWK refresh failures in any MCP/OAuth
path that activates those features.

Focused gates:

- cover wrong algorithms, public-key/HMAC confusion, empty keys, non-HTTP(S)
  JWK URLs, malformed critical headers, and JWK refresh failure without leaks;
- exercise the actual MCP auth transport rather than only unit-test doubles;
- retain the exact frozen closure in both vulnerability scanners.

### SoupSieve

The upstream [selector-list advisory](https://github.com/facelessuser/soupsieve/security/advisories/GHSA-2wc2-fm75-p42x)
and [unterminated-attribute advisory](https://github.com/facelessuser/soupsieve/security/advisories/GHSA-836r-79rf-4m37)
both affect versions through 2.8.3 and mark 2.8.4 patched. Together they cover
memory exhaustion from enormous comma-separated selector lists and a regular
expression denial of service from malformed attribute selectors.

The official [changelog](https://facelessuser.github.io/soupsieve/about/changelog/)
records both fixes in 2.8.4. It records that 2.9 drops Python 3.9, lazily
compiles selector branches, and fixes selector behavior; 2.9.2 further corrects
empty-selector accounting and `:has()` behavior. The
[2.9.2 metadata](https://raw.githubusercontent.com/facelessuser/soupsieve/2.9.2/pyproject.toml)
requires Python `>=3.10` and has no runtime dependencies.

The project constraint is `soupsieve>=2.8.4`; BeautifulSoup 4.14.3 brings it
into the lock at 2.9.2. ProxyWhirl's `HTMLTableParser` passes the configured
`table_selector` to BeautifulSoup's `select_one`. Remote HTML does not choose
that selector, but any caller accepting an untrusted selector can expose the
parser boundary. Python 3.10 is the exact upstream floor. Runtime risk is
selector compatibility and newly bounded pathological input.

Focused gates:

- run HTML-table parser and proxy-fetching tests with normal selectors,
  malformed unterminated attribute selectors, deep `:has()` selectors, and
  a selector list around the upstream limit;
- assert invalid or excessive selectors fail quickly and through the documented
  parser error without unbounded CPU or memory use.

## Transitive and Python-floor conclusion

The lock-level relevant edges are:

```text
beautifulsoup4 4.14.3 -> soupsieve 2.9.2
authlib 1.7.2 -> cryptography 50.0.0, joserfc 1.7.4
joserfc 1.7.4 -> cryptography 50.0.0
mcp 1.29.0 -> pydantic-settings 2.15.0, PyJWT[crypto] 2.13.0
PyJWT[crypto] 2.13.0 -> cryptography 50.0.0
fastmcp-slim 3.4.7 -> pydantic-settings 2.15.0
fastmcp-slim 3.4.7 server/client extras -> authlib, joserfc, mcp, starlette, httpx
```

There is one important compatibility boundary: joserfc 1.7.4,
pydantic-settings 2.15.0, and SoupSieve 2.9.2 now require Python 3.10. This
matches the project floor exactly, so it is compatible but leaves no margin for
an accidental Python 3.9 build. cryptography 50.0.0 and PyJWT 2.13.0 retain a
Python 3.9 floor. No transitive constraint in the current lock forces a Python
floor above 3.10.

## FastMCP 3.4.7 to 4.0.0b1 audit

### Upstream status and dependency boundary

The official [FastMCP 3.4.7 release](https://github.com/PrefectHQ/fastmcp/releases/tag/v3.4.7)
is the current stable line and includes a security backport for CIMD audience
validation. The official [FastMCP 4.0.0b1 release](https://github.com/PrefectHQ/fastmcp/releases/tag/v4.0.0b1)
describes itself as a beta ahead of 4.0, recommends an exact prerelease pin, and
warns adopters to expect sharp edges. “Latest” therefore does not mean
release-stable for this RC.

The official [v3-to-v4 upgrade guide](https://gofastmcp.com/getting-started/upgrading/from-fastmcp-3)
and package metadata establish the dependency delta:

| Boundary | Locked v3 candidate | v4.0.0b1 | Assessment |
| --- | --- | --- | --- |
| Python | FastMCP `>=3.10`; project `>=3.10` | `>=3.10` | Compatible |
| FastMCP constraint | `fastmcp>=3.4.7,<4` | Exact beta pin recommended | Direct conflict |
| MCP SDK | `mcp>=1.28.1,<2`, locked 1.29.0 | `mcp>=2,<3` | Hard major-version conflict |
| Protocol types | MCP SDK 1 types | `mcp-types>=2,<3` | New package and type boundary |
| HTTP client | `httpx>=0.28.1,<1`, locked 0.28.1 | internal `httpx2>=2.5` | Major runtime/exception/trust-store change |
| Pydantic | locked 2.13.3 | `>=2.12` | Satisfies v4 |
| Starlette | locked 1.3.1 | `>=1.0.1` | Satisfies v4 |
| FastAPI | locked 0.136.1 | guide requires `>=0.133` with Starlette 1 | Satisfies v4 |

Primary package metadata:

- [FastMCP 3.4.7 slim metadata](https://raw.githubusercontent.com/PrefectHQ/fastmcp/v3.4.7/fastmcp_slim/pyproject.toml)
  declares MCP SDK 1 and httpx 0.28 constraints;
- [FastMCP 4.0.0b1 wrapper metadata](https://raw.githubusercontent.com/PrefectHQ/fastmcp/v4.0.0b1/pyproject.toml)
  requires Python 3.10 and pins its matching slim package;
- [FastMCP 4.0.0b1 slim metadata](https://raw.githubusercontent.com/PrefectHQ/fastmcp/v4.0.0b1/fastmcp_slim/pyproject.toml)
  declares MCP SDK 2, `mcp-types`, httpx2, Pydantic, Starlette, Authlib, and
  joserfc requirements.

The current ProxyWhirl surface is intentionally small but security-sensitive:

- `FastMCP("ProxyWhirl", lifespan=_mcp_lifespan)` and one middleware instance;
- `Context`, `Middleware`, and `MiddlewareContext` imports;
- one unified dict-returning tool, two JSON-string resources, and two prompts;
- API-key authorization in `on_call_tool` and `on_read_resource`;
- `stdio`, `http`, `sse`, and `streamable-http` transport selections;
- no native FastMCP OAuth provider, task API, roots/sampling/elicitation calls,
  mounted servers, custom FastMCP HTTP client, or direct raw SDK type import.

That reduces application rewrite cost, but not protocol, lock, auth, or
assurance cost.

### API and protocol types

FastMCP 4 moves to MCP SDK 2 and the standalone `mcp-types` package. The upgrade
guide says Python protocol fields are now snake_case while JSON wire fields
remain camelCase; compatibility attribute reads warn and can be disabled. It
also removes v3 compatibility shims and legacy methods/parameters. ProxyWhirl
does not use the guide's listed removed helper methods, so ordinary
server/decorator imports appear low-cost. That source-level similarity is not
proof of protocol compatibility: schema snapshots, errors, and third-party
clients must be exercised with compatibility mode disabled and warnings fatal.

### Authentication and middleware

ProxyWhirl uses custom API-key middleware rather than native FastMCP OAuth, so
v4 native OAuth issuer/resource changes are not immediately reachable. The
custom boundary still needs adaptation proof:

- the official [v4 middleware documentation](https://gofastmcp.com/servers/middleware)
  preserves `fastmcp.server.middleware` and operation hooks such as
  `on_call_tool` and `on_read_resource`;
- the v4 hook contract types call-tool messages as request parameters and hook
  results as `ToolResult`/`ResourceResult`. ProxyWhirl's authorization guard
  currently reads nested `context.message.params.arguments` and returns plain
  dictionaries for denials. The v4 documented shape is direct
  `context.message.arguments`, so the guard cannot be declared v4-compatible
  from static imports alone;
- v4 generic middleware hooks observe a broader set of protocol traffic, while
  operation-specific hooks remain the correct place for exactly-once policy.

The action-extraction and typed-denial boundaries are high impact: a shape
mismatch can misclassify a write, bypass a narrow test double, or turn an
authorization failure into an internal error. A real v4 client must prove valid,
invalid, missing, read-only, known-write, and unknown-write behavior. The RC
must not grow a speculative `.params`/direct dual-shape adapter.

### Lifespan

The official [lifespan documentation](https://gofastmcp.com/servers/lifespan)
continues to support an async context manager passed to the `FastMCP` constructor
and exposes its yielded state through `Context`. ProxyWhirl's construction
therefore looks source-compatible. The v4 protocol also supports modern
sessionless operation alongside legacy sessions, so setup/cleanup must still be
proved exactly once per server process across normal shutdown, cancellation,
and transport errors. Source compatibility is a medium runtime risk, not a
waiver of lifecycle tests.

### Transports and HTTP behavior

The official [running-server documentation](https://gofastmcp.com/deployment/running-server)
documents `stdio`, recommended HTTP, and legacy SSE. The
[settings reference](https://gofastmcp.com/more/settings) continues to list the
`streamable-http` alias. ProxyWhirl's transport vocabulary is therefore
plausibly compatible.

The implementation beneath HTTP is materially different. FastMCP 4 replaces
its internal httpx dependency with httpx2. The guide calls out changed client
APIs, exception classes, logging namespaces, and operating-system trust-store
behavior rather than certifi-only defaults. ProxyWhirl does not customize
FastMCP's client, but live HTTP/SSE error mapping, TLS behavior, cancellation,
and logs are observable surfaces. It also remains necessary to test project
code that directly uses httpx 0.28 beside FastMCP's httpx2 dependency.

### Structured tool results

The official [tool documentation](https://gofastmcp.com/servers/tools)
specifies that dictionaries, dataclasses, and Pydantic models produce both text
content and `structuredContent`, while primitive results are wrapped into an
object matching the advertised output schema; explicit `ToolResult` remains
available for full control. ProxyWhirl's unified tool returns dictionaries, so
v4 can change the observed schema/content envelope even if its Python return
value is unchanged. Resources currently return serialized JSON strings and
must remain resource content rather than silently becoming structured tool
results. List-tools schemas, call-tool content, MIME types, prompts, and
contract snapshots require direct comparison.

### Cost and risk matrix

| Workstream | Estimated implementation cost | Runtime/security risk | Why / required proof |
| --- | --- | --- | --- |
| Manifest and lock | High | High | Remove `fastmcp<4` and `mcp<2` together; add SDK 2, mcp-types, and httpx2 closure; inspect every transitive change |
| Imports and decorators | Low | Medium | Familiar names remain, but removed shims and warning-backed protocol fields need tests |
| API-key middleware | Medium | High | Request parameter shape and typed denial result are authorization boundaries |
| Native OAuth | Low now | Low now | Not configured by ProxyWhirl; must be reevaluated before enabling it |
| Lifespan | Low | Medium | Constructor form remains; sessionless/legacy teardown and cancellation still need live proof |
| stdio/HTTP/SSE transport | Medium | High | MCP SDK 2 negotiation, aliases, errors, and cancellation are externally observable |
| Structured tool output | Medium | High | Dict results can alter content/output-schema snapshots and downstream clients |
| Internal HTTP/TLS | Medium | High | httpx2 exceptions, trust store, logging, and coexistence with direct httpx 0.28 |
| Client/protocol compatibility | High | High | Modern sessionless and legacy modes, snake_case types, and compatibility warnings need a matrix |

### Supported defer and future upgrade gate

The supported RC action is to retain exact FastMCP 3.4.7 compatibility and the
MCP SDK 1 constraint, then open a post-`0.4.0` change once FastMCP 4 is stable.
This is a stability decision, not a claim that v4 is unsuitable. The current
stable FastMCP line already carries the relevant security backport; no official
v4-only security fix was identified that justifies accepting beta and protocol
major risk for this candidate.

The future change should be atomic and stop on the first unresolved fail-closed
auth or schema regression:

1. Pin the stable FastMCP 4 wrapper/slim pair, remove `mcp<2` in the same lock
   transaction, and inspect all MCP SDK 2, mcp-types, httpx2, Authlib, joserfc,
   Starlette, and Pydantic changes.
2. Build and install the all-extras wheel in disposable Python 3.10, 3.11, and
   current-supported environments; prove imports without relying on the base
   sync.
3. Exercise real FastMCP clients in auto/modern and legacy modes over stdio and
   HTTP, plus the supported SSE/`streamable-http` compatibility surface.
4. Prove missing, invalid, and valid API keys; reads; every known write action;
   unknown actions failing closed; direct action extraction; typed denial
   results; and absence of API-key material from schemas, logs, and errors.
5. Snapshot list-tools and call-tool output schemas, text content,
   `structuredContent`, resources/MIME types, and prompts against the 0.4
   contract.
6. Prove lifespan initialization and cleanup exactly once on normal shutdown,
   cancellation, client disconnect, and transport failure.
7. Probe HTTP/TLS trust-store behavior, exception mapping, logging names, and
   coexistence with ProxyWhirl's direct httpx clients.
8. Disable protocol compatibility reads, make warnings fatal, and run the
   focused MCP unit/integration/contract suites before full quality, security,
   build, and isolated-install gates.

Primary local suites for that change are
`tests/unit/test_mcp_server.py`, `tests/unit/test_mcp_coverage_wave4.py`,
`tests/integration/test_mcp_integration.py`, and
`tests/contract/test_restructure_contract_snapshots.py`.

## Research completion record

- **Task 2.22 / F6.2:** complete as research. Fixed floors, current lock,
  transitive constraints, Python impact, upstream change evidence, runtime
  risks, and focused gates are recorded for all five packages.
- **Task 5.7 / M4.1:** complete as research. The v3.4.7-to-v4.0.0b1 API, auth,
  lifespan, transport, structured-result, Python, and dependency boundaries are
  compared with a cost/risk matrix.
- **Mutation boundary:** this artifact is the only file created by this lane.
  No product file, manifest, lock, existing OpenSpec file, generated docs, or
  dependency environment was changed.
