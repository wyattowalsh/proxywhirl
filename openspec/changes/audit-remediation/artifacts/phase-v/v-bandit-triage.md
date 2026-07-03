# V-006: RV-008 / RV-009 Bandit Triage

## RV-008 — B311 `random.choices`/`random.choice` (blacklist: non-cryptographic PRNG)

`uvx bandit -r proxywhirl/ -q` reports **6** B311 hits, all in `proxywhirl/strategies.py`, all in
rotation-strategy proxy selection (`RandomStrategy`, `WeightedStrategy`, `PerformanceBasedStrategy`
exploration/fallback paths):

| Line | Context |
| ---- | ------- |
| 595 | `RandomStrategy.select` — uniform random proxy choice |
| 777 | `WeightedStrategy.select` — weighted random proxy choice |
| 1098 | `PerformanceBasedStrategy` — exploration path (equal-opportunity random choice) |
| 1103 | `PerformanceBasedStrategy` — exploitation path (weighted random choice) |
| 1108 | `PerformanceBasedStrategy` — fallback random choice |
| 1894 | Weighted-cost strategy — weighted random proxy choice |

**Triage:** All six are non-cryptographic load-balancing / traffic-shaping decisions (which proxy to use
next). None influence security tokens, session IDs, encryption keys, or any secret material — confirmed
by cross-referencing `proxywhirl/cache/crypto.py` and `proxywhirl/utils.py` key/token generation, which
already use `secrets`/`cryptography` (not `random`). **False positive for this call site's use case.**

## RV-009 — B105 `hardcoded_password_string` (`proxywhirl/utils.py:453`)

```python
if (username is None) != (password is None) or username == "" or password == "":
```

Bandit's B105 heuristic flags any comparison of a variable literally named `password` against a string
literal, regardless of value. Here `password == ""` is a **validation check** (rejecting proxy URLs with
an empty-string password component), not a hardcoded credential. **Confirmed false positive.**

## Remediation

- RV-008: add `# nosec B311` with an inline rationale comment to each of the 6 call sites in
  `strategies.py` (F-015).
- RV-009: restructure the emptiness check in `utils.py` to avoid the `password == ""` literal-comparison
  pattern bandit flags, without an inline suppression comment (F-016).

**Status:** `fixed` (suppressed with rationale / restructured) — see F-015, F-016.
