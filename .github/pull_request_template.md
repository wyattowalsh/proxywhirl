<!--
Thank you for contributing to ProxyWhirl! 🚀

Please fill out this template to help us review your pull request efficiently.
Our CI/CD pipeline will automatically run quality checks, but please complete
the checklist below to ensure a smooth review process.
-->

## Summary

### What does this PR do?
<!-- Provide a clear and concise summary of your changes -->

### Related Issue(s)
<!-- Link to related issues using "Closes #123" or "Related to #456" -->

## Type of Change

<!-- Check all that apply -->
- [ ] 🐛 Bug fix (non-breaking change that fixes an issue)
- [ ] ✨ New feature (non-breaking change that adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 🔧 Configuration change (changes to build, CI, or development tools)
- [ ] 📚 Documentation update (changes to documentation only)
- [ ] 🎨 Code style/refactoring (no functional changes)
- [ ] ⚡ Performance improvement
- [ ] 🧪 Test improvements
- [ ] 🔒 Security improvement

## Detailed Description

### Changes Made
<!-- Describe the changes in detail. What did you add, modify, or remove? -->

### Why These Changes?
<!-- Explain the motivation behind these changes. What problem do they solve? -->

### How Did You Test This?
<!-- Describe how you tested your changes -->

## Breaking Changes

<!-- If this PR introduces breaking changes, describe them here -->
- [ ] This PR introduces no breaking changes
- [ ] This PR introduces breaking changes (describe below):

**Breaking Changes Description:**
<!-- Describe what breaks and how users should adapt -->

## Quality Assurance

### Code Quality Checklist
<!-- Our CI will check these automatically, but please verify locally -->

- [ ] 🔍 **Code Quality**: Ran `make quality` successfully (format + lint + test)
  - [ ] `make format` - Code formatted with black + isort
  - [ ] `make lint` - Passed ruff + pylint + mypy checks
  - [ ] `make test` - All tests pass with good coverage
- [ ] 🧪 **Testing**: Added/updated tests for new functionality
- [ ] 📝 **Documentation**: Updated relevant documentation
- [ ] 🏷️ **Type Hints**: Added proper type hints for new code
- [ ] 🔒 **Security**: Considered security implications of changes

### Testing Checklist

- [ ] **Unit Tests**: Added/updated unit tests
- [ ] **Integration Tests**: Tested integration scenarios (if applicable)
- [ ] **Manual Testing**: Manually tested the changes
- [ ] **Edge Cases**: Considered and tested edge cases
- [ ] **Performance**: Verified no performance regressions

### Documentation Updates

- [ ] Updated relevant `.md` files
- [ ] Updated docstrings and inline comments  
- [ ] Updated CLI help text (if applicable)
- [ ] Updated configuration examples (if applicable)
- [ ] Updated API documentation (if applicable)

## Configuration and Compatibility

### Environment Impact
<!-- Check all that apply -->
- [ ] This change affects Python 3.13+ compatibility
- [ ] This change affects the CLI interface
- [ ] This change affects the Python API
- [ ] This change affects configuration file format
- [ ] This change affects cache backends
- [ ] This change affects proxy loaders
- [ ] This change requires new dependencies

### Dependency Changes
<!-- If you added, updated, or removed dependencies -->
- [ ] No dependency changes
- [ ] Added new dependencies (list them):
- [ ] Updated existing dependencies (list them):
- [ ] Removed dependencies (list them):

## Release Notes

### User-Facing Changes
<!-- Describe changes that users need to know about -->
<!-- This will help with changelog generation -->

**New Features:**
- 

**Bug Fixes:**
- 

**Improvements:**
- 

**Breaking Changes:**
- 

## Review Guidance

### Focus Areas for Review
<!-- Guide reviewers on what to pay special attention to -->
- [ ] Logic correctness
- [ ] Performance implications
- [ ] Security considerations
- [ ] API design
- [ ] Error handling
- [ ] Documentation clarity
- [ ] Test coverage

### Specific Questions
<!-- Any specific questions for reviewers? -->

## Deployment Considerations

- [ ] This change can be deployed without special considerations
- [ ] This change requires coordination (describe below):

**Deployment Notes:**
<!-- Any special deployment instructions or considerations -->

---

## Automated Checks

<!-- These will be automatically verified by our CI/CD pipeline -->

### CI/CD Status
Our automated workflows will check:
- ✅ Code quality pipeline (`make quality`)
- ✅ Security audit (pip-audit)
- ✅ Documentation builds
- ✅ Integration tests (if labeled)

### Pre-merge Requirements
- [ ] All CI checks are passing ✅
- [ ] At least one maintainer approval
- [ ] No conflicts with target branch
- [ ] Linked issues are properly referenced

---

**Additional Notes:**
<!-- Any other information reviewers should know -->

<!-- 
🙏 Thank you for contributing to ProxyWhirl!
Your time and effort help make proxy management better for everyone.
-->
