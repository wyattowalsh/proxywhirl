# Raise Python Floor for Security Gates

## Summary

Raise ProxyWhirl's supported runtime floor from Python 3.9 to Python 3.10 and
modernize package license metadata so production-readiness security and package
build gates no longer emit actionable warnings.

## Motivation

The production-readiness security gate found Safety advisories in the Python
`<3.10` branches of `uv.lock` for `requests`, `python-multipart`,
`python-dotenv`, and `filelock`. The current Python 3.13 environment resolves
safe versions, but the package metadata still advertises Python 3.9 support and
therefore keeps vulnerable Python 3.9-compatible branches in the lock export.
The package build gate also emitted Setuptools deprecation warnings for the
legacy license table and license classifier metadata.

## Scope

- Update package metadata and classifiers to support Python 3.10+.
- Publish license metadata as an SPDX expression and remove deprecated license
  classifier metadata.
- Refresh only the vulnerable dependency lock branches to current safe versions.
- Keep runtime code, REST API, CLI command shape, and database schema unchanged.
- Validate security, type, test, packaging, and docs gates after the metadata
  floor change.

## Non-Goals

- No new third-party dependencies.
- No compatibility shim for Python 3.9.
- No runtime behavior change beyond the published Python support matrix.
