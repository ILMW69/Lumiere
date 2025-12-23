#!/bin/bash
# Lumiere Repository Cleanup Script
# Run this before deployment to remove unnecessary files

echo "🧹 Starting Lumiere Repository Cleanup..."
echo ""

# Navigate to project root
cd "$(dirname "$0")"

echo "📍 Working directory: $(pwd)"
echo ""

# ============================================
# 1. Remove Test Files
# ============================================
echo "❌ Removing test files..."
rm -f test_langfuse.py
rm -f test_langsmith.py
rm -f visualize_graph.py
rm -f show_graph.py
rm -f pytest.ini
echo "   ✅ Test files removed"

# ============================================
# 2. Remove Test Directory
# ============================================
echo "❌ Removing tests/ directory..."
rm -rf tests/
echo "   ✅ tests/ directory removed"

# ============================================
# 3. Remove Development Documentation
# ============================================
echo "❌ Removing development docs..."
rm -f docs/TEST_FIX_SUMMARY.md
rm -f docs/TEST_SETUP_SUMMARY.md
rm -f docs/DOCUMENTATION_REVISION_SUMMARY.md
echo "   ✅ Development docs removed"

# ============================================
# 4. Remove Cache Directories
# ============================================
echo "❌ Removing cache directories..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
rm -rf .pytest_cache/
echo "   ✅ Cache directories removed"

# ============================================
# 5. Remove Legacy Code
# ============================================
echo "❌ Removing legacy code..."
rm -f observability/langfuse_client.py
echo "   ✅ Legacy code removed"

# ============================================
# 6. Remove Empty Directories
# ============================================
echo "❌ Removing empty directories..."
rm -rf docker/
echo "   ✅ Empty directories removed"

# ============================================
# 7. Remove Development Databases
# ============================================
echo "⚠️  Checking development databases..."
if [ -d "databases" ]; then
    DB_COUNT=$(ls -1 databases/*.db 2>/dev/null | wc -l)
    if [ $DB_COUNT -gt 0 ]; then
        echo "   Found $DB_COUNT user databases in databases/"
        read -p "   Do you want to remove them? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -f databases/*.db
            echo "   ✅ Database files removed"
        else
            echo "   ⏭️  Keeping database files"
        fi
    fi
fi

if [ -f "lumiere.db" ]; then
    read -p "   Remove root lumiere.db? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f lumiere.db
        echo "   ✅ lumiere.db removed"
    else
        echo "   ⏭️  Keeping lumiere.db"
    fi
fi

# ============================================
# 8. Remove Script Duplicates
# ============================================
echo "❌ Removing script duplicates..."
rm -f scripts/visualize_graph.py
rm -rf scripts/__pycache__/
echo "   ✅ Script duplicates removed"

# ============================================
# 9. Optional: Remove Dev Container
# ============================================
read -p "Remove .devcontainer/? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf .devcontainer/
    echo "   ✅ .devcontainer/ removed"
else
    echo "   ⏭️  Keeping .devcontainer/"
fi

# ============================================
# 10. Optional: Remove Legacy Visualizations
# ============================================
read -p "Remove legacy docs visualizations? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f docs/graph_visualization.png
    rm -f docs/graph_visualization.mmd
    echo "   ✅ Legacy visualizations removed"
else
    echo "   ⏭️  Keeping legacy visualizations"
fi

# ============================================
# Summary
# ============================================
echo ""
echo "✅ Cleanup Complete!"
echo ""
echo "📊 Repository Status:"
echo "   - Test files: Removed"
echo "   - Cache directories: Removed"
echo "   - Legacy code: Removed"
echo "   - Development docs: Removed"
echo ""
echo "🎯 Next Steps:"
echo "   1. Review .gitignore to ensure patterns are covered"
echo "   2. Commit changes: git add -A && git commit -m 'Clean repository for deployment'"
echo "   3. Push to GitHub: git push origin main"
echo "   4. Deploy to Streamlit Cloud"
echo ""
echo "🚀 Your repository is now deployment-ready!"
