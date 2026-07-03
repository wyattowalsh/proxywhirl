# R-007: Bandit Suppression Policy

## Policy

- Prefer restructuring code to eliminate a false positive (e.g., B105 hardcoded-password heuristics on
  empty-string comparisons) over adding a suppression comment, when a low-risk restructure is available.
- When a finding is a confirmed false positive for the call site's actual use case (e.g., B311 on
  non-cryptographic `random` calls used for load-balancing, not security tokens), suppress with
  `# nosec <CODE>` directly on the flagged line and place a concise rationale comment next to the
  call site. Never use a blanket `# nosec` without a rule code, never put rationale prose after the
  Bandit code where the scanner parses it as extra test IDs, and never suppress at the file/module
  level.
- Do not suppress B-series findings related to `subprocess`, `eval`, `exec`, deserialization
  (`pickle`, `yaml.load`), or hardcoded real secrets — those require an actual code fix, not suppression.

## Applied in this remediation

- `proxywhirl/strategies.py` — 6× `# nosec B311` with adjacent rationale comments for random
  proxy rotation load-balancing selection.
- `proxywhirl/retry.py` — 2× `# nosec B311` with adjacent rationale comments for retry jitter
  backoff.
- `proxywhirl/rotator/_bootstrap.py` — 1× `# nosec B311` with an adjacent rationale comment for
  source sampling.
- `proxywhirl/strategies.py` — replaced the session-persistence `except Exception: pass` fallback
  with a narrow invalid-session-ID guard instead of suppressing B110.
- `proxywhirl/utils.py:453` — restructured the credential-emptiness check to avoid the `password == ""`
  literal-comparison pattern instead of suppressing (see F-016).
