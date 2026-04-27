# Release Process & Version Control

## Version Scheme

SemVer: MAJOR.MINOR.PATCH

- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

## Release Workflow

1. **Code Freeze** (Monday 5 PM UTC)
   - No new features accepted
   - Bug fix phase begins

2. **Testing** (Tuesday-Wednesday)
   - Automated test suite (unit, integration, e2e)
   - Manual regression testing
   - Performance testing
   - Security scanning

3. **Release Candidate** (Wednesday 5 PM UTC)
   - Tag: `v1.2.3-rc.1`
   - Deploy to staging
   - Final validation

4. **Production Release** (Thursday 10 AM UTC)
   - Tag: `v1.2.3`
   - Blue-green deployment
   - Canary monitoring (10% → 50% → 100%)
   - Rollback ready

5. **Post-Release** (Thursday afternoon)
   - Monitor error rates & latency
   - Customer communication
   - Document release notes

## Git Tags

```bash
# Release tag (annotated, signed)
git tag -as v1.2.3 -m "Release v1.2.3"

# Pre-release tag
git tag -as v1.2.3-rc.1 -m "Release candidate 1"

# Push all tags
git push origin --tags
```

## Release Notes Template

```markdown
# v1.2.3 Release Notes

**Release Date:** 2024-01-15

## New Features
- Feature 1 (Issue #123)
- Feature 2 (Issue #124)

## Bug Fixes
- Fixed issue X (Issue #125)
- Fixed issue Y (Issue #126)

## Breaking Changes
- API change: `/old` → `/new`

## Migration Guide
[Step-by-step upgrade instructions]

## Contributors
- @developer1
- @developer2
```
