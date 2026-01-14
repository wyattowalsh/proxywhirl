#!/usr/bin/env python3
"""Update test imports to use new subpackage structure."""

import re
from pathlib import Path

# Define replacement patterns
replacements = {
    r'from proxywhirl\.circuit_breaker import': 'from proxywhirl.retry import',
    r'from proxywhirl\.retry_executor import': 'from proxywhirl.retry import',
    r'from proxywhirl\.retry_metrics import': 'from proxywhirl.retry import',
    r'from proxywhirl\.retry_policy import': 'from proxywhirl.retry import',
    r'from proxywhirl\.cache_crypto import': 'from proxywhirl.cache import',
    r'from proxywhirl\.cache_models import': 'from proxywhirl.cache import',
    r'from proxywhirl\.cache_tiers import': 'from proxywhirl.cache import',
}

# Find all test files
test_dir = Path('tests')
updated_files = []

for test_file in test_dir.rglob('*.py'):
    content = test_file.read_text()
    original_content = content
    
    # Apply all replacements
    for pattern, replacement in replacements.items():
        content = re.sub(pattern, replacement, content)
    
    # Only write if changed
    if content != original_content:
        test_file.write_text(content)
        updated_files.append(str(test_file))

print(f"Updated {len(updated_files)} test files:")
for f in sorted(updated_files)[:20]:
    print(f"  - {f}")
if len(updated_files) > 20:
    print(f"  ... and {len(updated_files) - 20} more")
