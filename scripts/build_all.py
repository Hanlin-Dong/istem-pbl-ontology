#!/usr/bin/env python3
"""
build_all.py — Unified build entry point for the complete IE-PBL Ontology.

Builds all 5 TBox modules from the single source in tbox.py,
validates with Pellet, and exports per-module Turtle files.

Usage:
    python scripts/build_all.py          # Build, validate, export
    python scripts/build_all.py --check  # Build and validate only (no export)
"""

import sys
import os

# Ensure we can import from scripts/
sys.path.insert(0, os.path.dirname(__file__))

from tbox import build_all_tbox, export_modules, export_ie_pbl_master, validate_with_pellet
from owlready2 import default_world


def main():
    export = "--check" not in sys.argv

    # 1. Build TBox
    classes = build_all_tbox()

    # 2. Validate
    ok = validate_with_pellet()
    if not ok:
        print("\n❌ VALIDATION FAILED — aborting export")
        sys.exit(1)

    # 3. Export
    if export:
        print("\n" + "=" * 60)
        print("Exporting per-module Turtle files...")
        print("=" * 60)
        export_modules()
        export_ie_pbl_master()
        print("\n✅ BUILD COMPLETE — All 6 ontology files exported")

    # 4. Stats
    world = default_world
    n_cls = len(list(world.classes()))
    n_op  = len(list(world.object_properties()))
    n_dp  = len(list(world.data_properties()))
    n_ind = len(list(world.individuals()))

    print("\n" + "=" * 60)
    print("IE-PBL ONTOLOGY — COMPLETE TBOX")
    print("=" * 60)
    print(f"  Classes:            {n_cls}")
    print(f"  Object Properties:  {n_op}")
    print(f"  Data Properties:    {n_dp}")
    print(f"  Individuals:        {n_ind}")
    print(f"  Reasoner:           Pellet (via owlready2)")
    print(f"  Consistency:        VERIFIED — 0 inconsistencies")

    return classes


if __name__ == "__main__":
    main()
