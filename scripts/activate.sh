# IE-PBL Ontology — Environment setup
# Run: source scripts/activate.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Activate Python virtual environment
source "$PROJECT_DIR/.venv/bin/activate"

# Add Homebrew OpenJDK to PATH for Pellet/HermiT reasoner
export PATH="/opt/homebrew/opt/openjdk/bin:$PATH"

echo "✓ IE-PBL Ontology environment activated"
echo "  Python: $(python3 --version)"
echo "  Java:   $(java -version 2>&1 | head -1)"
echo "  Project: $PROJECT_DIR"
echo ""
echo "  Build & validate: python scripts/build_all.py"
echo "  Run all tests:    pytest tests/ -v"
echo "  Full pipeline:    python scripts/build_all.py && python scripts/build_vignette.py && python scripts/build_swrl.py && pytest tests/ -v"
