#!/usr/bin/env python3
"""
config.py — Global constants and paths for the IE-PBL Ontology project.

Single source of truth for IRI, project paths, and environment configuration.
Import from all other scripts instead of hardcoding.
"""

from pathlib import Path

# ── Ontology Identity ──
IRI = "http://www.semanticweb.org/ie-pbl/ontology/1.0/"

# ── Project Paths ──
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ONTO_DIR = PROJECT_ROOT / "ontologies"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
VIGNETTE_DIR = PROJECT_ROOT / "vignette"
RULES_DIR = PROJECT_ROOT / "rules"
QUERIES_DIR = PROJECT_ROOT / "queries"
TESTS_DIR = PROJECT_ROOT / "tests"
DOCS_DIR = PROJECT_ROOT / "docs"

# ── Module IRI suffixes ──
MODULE_IRIS = {
    "core":      IRI + "module-core.ttl",
    "knowledge": IRI + "module-knowledge.ttl",
    "process":   IRI + "module-process.ttl",
    "team":      IRI + "module-team.ttl",
    "anchor":    IRI + "module-anchor.ttl",
}

# ── Export Paths ──
MODULE_PATHS = {
    "core":      ONTO_DIR / "module-core.ttl",
    "knowledge": ONTO_DIR / "module-knowledge.ttl",
    "process":   ONTO_DIR / "module-process.ttl",
    "team":      ONTO_DIR / "module-team.ttl",
    "anchor":    ONTO_DIR / "module-anchor.ttl",
    "ie-pbl":    ONTO_DIR / "ie-pbl.ttl",
}

# ── All .ttl output paths ──
ALL_TTL_PATHS = list(MODULE_PATHS.values())
