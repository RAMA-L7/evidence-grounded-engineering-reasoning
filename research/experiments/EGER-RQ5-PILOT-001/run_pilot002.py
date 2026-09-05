"""EGER P179 — EGER-RQ5-PILOT-002 execution (authorized).

Executes the frozen 8-trial matrix through harness/orchestrator.py with REAL
providers (pinned Ṛta + design_metadata, OpenSTA 2.2.0 in WSL, and the
qualified model opencode/mimo-v2.5-free). This gate is EXPLICITLY authorized
by the user (P179); no methodology decisions are made here — the frozen
matrix, retry policy, PO definitions, and identity audit are all code-frozen
in the harness.

Outputs (written to research/experiments/EGER-RQ5-PILOT-002/):
  manifest.json          — pre-execution frozen manifest
  raw_trials.json        — immutable raw trial records (preserved before analysis)
  analysis.json          — deterministic aggregation derived from raw records
  identity_audit.json    — candidate-identity audit over the raw records

Raw records are preserved exactly as produced by the runner; nothing is
edited after collection. Raw manifest/analysis remain publication-sensitive
and are NOT committed (repository convention since P170).
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
PROJECT_ROOT = Path(__file__).resolve().parents[3]
PILOT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "research" / "experiments" / "EGER-RQ5-PILOT-002"
for p in (str(PROJECT_ROOT), str(PILOT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from harness.orchestrator import run_matrix
from harness.matrix import frozen_matrix
from harness.tasks import TASKS
from harness.providers import (
    build_model_call,
    build_rta_oracle_call,
    build_opensta_oracle_call,
    resolve_opensta_binary_wsl,
    load_simple_path_design_metadata,
)
from harness.trial_runner import sha256_text


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_real_callables(opensta_binary, netlist_path, lib_path):
    """Real provider callables per frozen-matrix row (P179)."""

    def callables(row):
        if row["oracle"] == "Rta":
            oracle_call = build_rta_oracle_call(timeout_seconds=180)
        else:
            oracle_call = build_opensta_oracle_call(
                sta_binary=opensta_binary,
                netlist_path=netlist_path,
                lib_path=lib_path,
                design_name="simple_path",
                timeout_seconds=180,
            )
        # P173-R wiring: cwd = repo root so the agent-mode model writes
        # timing.sdc where the provider reads it back.
        model_call = build_model_call(
            model="opencode/mimo-v2.5-free",
            cwd=PROJECT_ROOT,
            timeout_seconds=180,
        )
        return oracle_call, model_call

    return callables


def build_manifest(opensta_binary) -> dict:
    substrate = PROJECT_ROOT / "research" / "implementation" / "opensta_pilot"
    metadata = load_simple_path_design_metadata()
    return {
        "experiment_id": "EGER-RQ5-PILOT-002",
        "authorization_gate": "P179",
        "protocol": "P169 (frozen) as repaired by P172/P177/P178",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "git_head": subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True,
            encoding="utf-8", errors="replace", cwd=str(PROJECT_ROOT),
        ).stdout.strip(),
        "oracles": {
            "rta": {
                "name": "Rta",
                "version": "1.5.11",
                "revision": "3b5c2f2",
                "invocation": "check --json (netlist-less) + P055 design_metadata",
                "design_metadata_task_id": metadata.task_id,
            },
            "opensta": {
                "name": "OpenSTA",
                "version": "2.2.0",
                "binary_wsl": "/root/opensta_build/OpenSTA/app/sta",
                "windows_resolved": str(opensta_binary),
            },
        },
        "model": {
            "provider": "opencode.cmd run",
            "name": "opencode/mimo-v2.5-free",
            "sampling": "provider default (no temperature flag on opencode run)",
            "timeout_seconds": 180,
            "qualified": "P173-R 6/6 VALID_SDC",
        },
        "matrix": frozen_matrix(),
        "tasks": {
            tid: {
                "initial_sdc": t["initial_sdc"],
                "initial_sdc_hash": sha256_text(t["initial_sdc"]),
            }
            for tid, t in TASKS.items()
        },
        "substrate": {
            "netlist": {
                "path": str(substrate / "design" / "simple_path.v"),
                "sha256": _sha256_file(substrate / "design" / "simple_path.v"),
            },
            "liberty": {
                "path": str(substrate / "liberty" / "simple_cells.lib"),
                "sha256": _sha256_file(substrate / "liberty" / "simple_cells.lib"),
            },
        },
        "retry_policy": "1 bounded retry per trial; both attempts retained",
        "max_iterations": 3,
        "po_definitions": "P169 §7: PO-1 ROBUST/MARGINAL/FAILED, PO-2 evidence "
        "compatibility, PO-3 Oracle-specific improvement; P177/P178 "
        "qualified_accept rule",
    }


def main() -> int:
    print("=" * 60)
    print("EGER-RQ5-PILOT-002 — AUTHORIZED EXECUTION (P179)")
    print("=" * 60)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Frozen manifest BEFORE trial 1.
    opensta_binary = resolve_opensta_binary_wsl()
    manifest = build_manifest(opensta_binary)
    (OUTPUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Manifest written: {OUTPUT_DIR / 'manifest.json'}")

    # 2. Execute the frozen matrix with real providers.
    netlist = PROJECT_ROOT / "research/implementation/opensta_pilot/design/simple_path.v"
    lib = PROJECT_ROOT / "research/implementation/opensta_pilot/liberty/simple_cells.lib"
    normalizer, gate = __import__(
        "harness.fixtures", fromlist=["build_pipeline"]
    ).build_pipeline()

    t0 = time.time()
    result = run_matrix(
        build_real_callables(opensta_binary, netlist, lib),
        normalizer,
        gate,
    )
    elapsed = round(time.time() - t0, 1)

    records = result["records"]
    analysis = result["analysis"]
    identity_audit = result["identity_audit"]

    # 3. Preserve immutable raw records FIRST, then derived artifacts.
    assert len(records) == 8
    (OUTPUT_DIR / "raw_trials.json").write_text(
        json.dumps(records, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"Raw records preserved: {OUTPUT_DIR / 'raw_trials.json'} "
          f"({len(records)} trials, elapsed {elapsed}s)")
    (OUTPUT_DIR / "analysis.json").write_text(
        json.dumps(analysis, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    (OUTPUT_DIR / "identity_audit.json").write_text(
        json.dumps(identity_audit, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )

    # Clean up any model-file residue in the repo root.
    stray = PROJECT_ROOT / "timing.sdc"
    if stray.exists():
        stray.unlink()

    print(f"\nRaw/analysis/identity_audit written under {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
