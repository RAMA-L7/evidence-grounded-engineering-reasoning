"""Batch executor for DIAGNOSTIC-008 — cross-task E3a replication.
Runs 60 cells with checkpoint support for resumption."""

import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[3]))

import json
from pathlib import Path

from run_cross_task_e3a_replication import (
    TASKS, CONDITIONS, RUNS_PER_CELL, _clopper_pearson_ci, run_single,
    MODEL_ID, MODEL_NAME
)

from eger.engineer.model import LiveEngineerModel
from eger.engineer.adapter import EngineerAdapter
from eger.oracle.adapter import EvidenceOracle


def main():
    base = Path(__file__).parent
    diag8_dir = base / "formal" / "DIAGNOSTIC-008"
    diag8_dir.mkdir(parents=True, exist_ok=True)

    checkpoint_file = diag8_dir / "_checkpoint.json"
    if checkpoint_file.exists():
        with open(checkpoint_file, "r") as f:
            checkpoint = json.load(f)
        print(f"Resuming: {len(checkpoint['completed_runs'])}/60 done")
    else:
        checkpoint = {"completed_runs": []}

    oracle = EvidenceOracle()
    engine_adapter = EngineerAdapter(
        LiveEngineerModel(timeout=60, max_tokens=2048, live=True,
                          model=MODEL_NAME)
    )

    all_results = []

    for task_id in ["BENCH2-002", "BENCH2-004", "BENCH2-005"]:
        for cond_key in ["BASE", "E3a"]:
            print(f"\n=== {task_id} / {cond_key} ===")
            for i in range(1, RUNS_PER_CELL + 1):
                run_id = f"{task_id}-{cond_key}-run{i:02d}"

                if run_id in checkpoint["completed_runs"]:
                    print(f"  {run_id}: SKIPPED")
                    manifest = diag8_dir / task_id / cond_key / f"manifest-{run_id}.json"
                    if manifest.exists():
                        with open(manifest) as f:
                            all_results.append(json.load(f))
                    continue

                print(f"  Run {i}/{RUNS_PER_CELL}...")
                try:
                    r = run_single(task_id, cond_key, i, oracle, engine_adapter, diag8_dir)
                except Exception as e:
                    r = {
                        "run_id": run_id, "task_id": task_id,
                        "condition": cond_key, "run_number": i,
                        "status": "INCOMPLETE", "failure": str(e)
                    }
                all_results.append(r)

                checkpoint["completed_runs"].append(run_id)
                with open(checkpoint_file, "w") as f:
                    json.dump(checkpoint, f)

                adh = r.get("error_adherence", "?")
                delta = r.get("error_delta", "?")
                print(f"    adh={adh}, delta={delta}, status={r['status']}")
                print(f"    Checkpoint ({len(checkpoint['completed_runs'])}/60)")

    # Summary
    print("\n=== Summary ===")
    cell_results = {}
    for r in all_results:
        key = f"{r.get('task_id','?')}-{r.get('condition','?')}"
        cell_results.setdefault(key, []).append(r)

    for key in sorted(cell_results.keys()):
        runs = cell_results[key]
        completed = [r for r in runs if r["status"] == "COMPLETED"]
        adherent = sum(1 for r in completed if r.get("error_adherence"))
        n = len(completed)
        lo, hi = _clopper_pearson_ci(adherent, n) if n > 0 else (0, 0)
        rate = f"{adherent/n:.0%}" if n > 0 else "N/A"
        print(f"  {key:30s} {adherent}/{n} = {rate}  CI=[{lo:.1%},{hi:.1%}]")

    # Write index
    completed_all = [r for r in all_results if r["status"] == "COMPLETED"]
    index = {
        "experiment": "P120-CROSS-TASK-E3A-REPLICATION",
        "model_id": MODEL_ID, "model_name": MODEL_NAME,
        "total_attempted": len(all_results),
        "total_completed": len(completed_all),
        "total_incomplete": len(all_results) - len(completed_all),
        "cells": {k: {
            "completed": len([r for r in v if r["status"]=="COMPLETED"]),
            "adherent": sum(1 for r in v if r["status"]=="COMPLETED" and r.get("error_adherence")),
        } for k, v in cell_results.items()},
        "results": [{
            "run_id": r["run_id"], "task_id": r.get("task_id"),
            "condition": r["condition"], "status": r["status"],
            "error_adherence": r.get("error_adherence"),
            "error_delta": r.get("error_delta"),
            "proposal_changed": r.get("proposal_changed"),
        } for r in all_results],
    }
    (diag8_dir / "RUN_INDEX.json").write_text(
        json.dumps(index, indent=2), encoding="utf-8"
    )
    print(f"\nRUN_INDEX written. DIAGNOSTIC-008 EXECUTION COMPLETE.")


if __name__ == "__main__":
    main()
