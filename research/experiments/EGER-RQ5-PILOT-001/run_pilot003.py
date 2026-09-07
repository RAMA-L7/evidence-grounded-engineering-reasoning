"""EGER P185 — EGER-RQ5-PILOT-003 model-comparison execution (authorized).

Executes the frozen 16-trial model-comparison matrix
(2 models × 2 tasks × 2 Oracles × 2 replications) through
harness/orchestrator.run_model_matrix with REAL providers:

- Baseline model:  opencode/mimo-v2.5-free        (timeout 180s, P184 §3)
- Comparison model: opencode/nemotron-3.5-lightning-free (timeout 300s, P184 §3)
- Ṛta 1.5.11 @ 3b5c2f2 (netlist-less + frozen P055 DesignMetadata)
- OpenSTA 2.2.0 @ WSL (valid-clock guard enabled)

Frozen protocol: P183 (design) as executed under P184 READY — P169/P172/
P177/P178 harness semantics unchanged. The pre-run matrix-order assertion
must pass BEFORE trial 1 (P185 §2). No reordering after results.

Outputs (written to research/experiments/EGER-RQ5-PILOT-003/):
  manifest.json       — pre-execution frozen manifest (written before trial 1)
  raw_trials.json     — immutable raw trial records (preserved before analysis)
  analysis.json       — deterministic aggregation (incl. per_model)
  identity_audit.json — candidate-identity audit over the raw records

Raw records are preserved exactly as produced; nothing is edited after
collection. Raw manifest/analysis remain publication-sensitive and are NOT
committed (repository convention since P170).
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
OUTPUT_DIR = PROJECT_ROOT / "research" / "experiments" / "EGER-RQ5-PILOT-003"
for p in (str(PROJECT_ROOT), str(PILOT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from harness.orchestrator import run_model_matrix
from harness.model_matrix import (
    frozen_model_matrix,
    assert_model_matrix_order,
    MODEL_IDS,
    MODEL_TIMEOUTS,
)
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
    """Real provider callables per frozen model-matrix row (P185 §5-§9)."""

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
        # timing.sdc where the provider reads it back. Per-model timeout is
        # the P184-documented infrastructure difference (180s vs 300s).
        model_call = build_model_call(
            model=MODEL_IDS[row["model"]],
            cwd=PROJECT_ROOT,
            timeout_seconds=MODEL_TIMEOUTS[row["model"]],
        )
        return oracle_call, model_call

    return callables


def build_manifest(opensta_binary) -> dict:
    substrate = PROJECT_ROOT / "research" / "implementation" / "opensta_pilot"
    metadata = load_simple_path_design_metadata()
    return {
        "experiment_id": "EGER-RQ5-PILOT-003",
        "authorization_gate": "P185",
        "protocol": "P183 frozen (model-comparison design) on P169/P172/P177/P178 harness",
        "research_question": (
            "To what extent does the evidence-grounded EGER architecture "
            "operate with different large language models under the same "
            "deterministic evaluation authorities and VLSI engineering tasks?"
        ),
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
                "valid_clock_guard": "create_clock required; NO_TIMING_CONSTRAINT flagged",
            },
        },
        "models": {
            label: {
                "model_id": MODEL_IDS[label],
                "timeout_seconds": MODEL_TIMEOUTS[label],
                "sampling": "provider default (no temperature flag on opencode run)",
                "qualified": "P184 6/6 VALID_SDC",
            }
            for label in MODEL_IDS
        },
        "matrix": frozen_model_matrix(),
        "matrix_planned_trials": len(frozen_model_matrix()),
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
        "counterbalancing": "Within each model block: T1 Rta-first, T2 "
        "OpenSTA-first; baseline model block first, comparison second (fixed)",
    }


def main() -> int:
    print("=" * 60)
    print("EGER-RQ5-PILOT-003 — AUTHORIZED EXECUTION (P185)")
    print("=" * 60)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Frozen manifest BEFORE trial 1 (P185 §5).
    opensta_binary = resolve_opensta_binary_wsl()
    manifest = build_manifest(opensta_binary)
    (OUTPUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Manifest written: {OUTPUT_DIR / 'manifest.json'}")
    print(f"Planned trials: {manifest['matrix_planned_trials']} (16)")

    # 2. Pre-run order assertion (P185 §2) — BEFORE trial 1.
    assert_model_matrix_order(frozen_model_matrix())
    print("Pre-run matrix-order assertion: PASS (frozen 16-trial order)")

    # 3. Execute the frozen model matrix with real providers.
    netlist = PROJECT_ROOT / "research/implementation/opensta_pilot/design/simple_path.v"
    lib = PROJECT_ROOT / "research/implementation/opensta_pilot/liberty/simple_cells.lib"
    normalizer, gate = __import__(
        "harness.fixtures", fromlist=["build_pipeline"]
    ).build_pipeline()

    t0 = time.time()
    result = run_model_matrix(
        build_real_callables(opensta_binary, netlist, lib),
        normalizer,
        gate,
    )
    elapsed = round(time.time() - t0, 1)

    records = result["records"]
    analysis = result["analysis"]
    identity_audit = result["identity_audit"]

    # 4. Preserve immutable raw records FIRST, then derived artifacts.
    assert len(records) == 16
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