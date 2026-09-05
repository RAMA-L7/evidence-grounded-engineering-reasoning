"""Pytest conftest for harness tests.

Adds the repository root (for `eger.*` imports) and the pilot directory
(so `harness.*` imports resolve) to sys.path. The pilot directory name
contains hyphens, so it cannot be imported as a dotted package path.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PILOT_DIR = Path(__file__).resolve().parents[1]

for p in (str(PROJECT_ROOT), str(PILOT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)