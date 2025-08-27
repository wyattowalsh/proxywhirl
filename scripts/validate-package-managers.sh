#!/bin/bash
# validate-package-managers.sh
# Validates that the correct package managers are being used consistently

set -e

echo "🔍 Validating package manager consistency..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

errors=0

# Check Python package manager (should be uv)
echo "📦 Checking Python package management..."

# Check for uv.lock existence
if [[ ! -f "uv.lock" ]]; then
    echo -e "${RED}❌ uv.lock not found - should use 'uv' for Python dependencies${NC}"
    ((errors++))
else
    echo -e "${GREEN}✅ uv.lock found${NC}"
fi

# Check for old-style files that shouldn't exist
if [[ -f "requirements.txt" ]] || [[ -f "setup.py" ]] || [[ -f "Pipfile" ]]; then
    echo -e "${YELLOW}⚠️ Found legacy Python dependency files (requirements.txt, setup.py, Pipfile)${NC}"
    echo -e "${YELLOW}   Consider removing them in favor of pyproject.toml + uv${NC}"
fi

# Check Node.js package managers (should be pnpm)
echo "📦 Checking Node.js package management..."

# Check docs directory
if [[ -d "docs" ]]; then
    if [[ ! -f "docs/pnpm-lock.yaml" ]]; then
        echo -e "${RED}❌ docs/pnpm-lock.yaml not found - should use 'pnpm' for Node.js dependencies${NC}"
        ((errors++))
    else
        echo -e "${GREEN}✅ docs/pnpm-lock.yaml found${NC}"
    fi
    
    # Check for wrong lockfiles
    if [[ -f "docs/package-lock.json" ]] || [[ -f "docs/yarn.lock" ]]; then
        echo -e "${RED}❌ Found package-lock.json or yarn.lock in docs/ - should use pnpm only${NC}"
        ((errors++))
    fi
fi

# Check frontend directory
if [[ -d "frontend" ]]; then
    if [[ ! -f "frontend/pnpm-lock.yaml" ]]; then
        echo -e "${RED}❌ frontend/pnpm-lock.yaml not found - should use 'pnpm' for Node.js dependencies${NC}"
        ((errors++))
    else
        echo -e "${GREEN}✅ frontend/pnpm-lock.yaml found${NC}"
    fi
    
    # Check for wrong lockfiles
    if [[ -f "frontend/package-lock.json" ]] || [[ -f "frontend/yarn.lock" ]]; then
        echo -e "${RED}❌ Found package-lock.json or yarn.lock in frontend/ - should use pnpm only${NC}"
        ((errors++))
    fi
fi

# Check GitHub Actions workflows
echo "⚙️ Checking GitHub Actions workflows..."

workflow_files=(.github/workflows/*.yml .github/workflows/*.yaml)
for file in "${workflow_files[@]}"; do
    if [[ -f "$file" ]]; then
        # Check for npm or yarn usage (should be pnpm)
        if grep -q "npm install\|yarn install\|npm ci\|yarn" "$file" 2>/dev/null; then
            echo -e "${YELLOW}⚠️ Found npm/yarn usage in $file - consider using pnpm${NC}"
        fi
        
        # Check for pip usage (should be uv)
        if grep -q "pip install" "$file" 2>/dev/null; then
            echo -e "${YELLOW}⚠️ Found pip usage in $file - consider using uv${NC}"
        fi
    fi
done

# Check Makefile
echo "🔧 Checking Makefile..."
if [[ -f "Makefile" ]]; then
    # Check for pnpm usage
    if grep -q "pnpm" Makefile; then
        echo -e "${GREEN}✅ Makefile uses pnpm for Node.js${NC}"
    else
        echo -e "${YELLOW}⚠️ Makefile doesn't seem to use pnpm${NC}"
    fi
    
    # Check for uv usage
    if grep -q "uv " Makefile; then
        echo -e "${GREEN}✅ Makefile uses uv for Python${NC}"
    else
        echo -e "${YELLOW}⚠️ Makefile doesn't seem to use uv${NC}"
    fi
fi

echo ""
if [[ $errors -eq 0 ]]; then
    echo -e "${GREEN}🎉 Package manager validation passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Found $errors package manager consistency issues${NC}"
    echo -e "${YELLOW}💡 Recommended setup:${NC}"
    echo -e "${YELLOW}   Python: Use 'uv' (modern, fast Python package manager)${NC}"
    echo -e "${YELLOW}   Node.js: Use 'pnpm' (fast, disk-efficient package manager)${NC}"
    exit 1
fi