"""Batch executor for DIAGNOSTIC-009 — E3a wording deconfounding.
Runs 96 cells with checkpoint support for resumption."""

import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[3]))

import json
from pathlib import Path

from run_e3a_wording_deconfounding import (
    TASKS, CONDITIONS, RUNS_PER_CELL, _clopper_pearson_ci, run_single,
    MODEL_ID, MODEL_NAME
)

from eger.engineer.model import LiveEngineerModel
from eger.engineer.adapter import EngineerAdapter
from eger.oracle.adapter import EvidenceOracle


def main():
    base = Path(__file__).parent
    diag9_dir = base / "formal" / "DIAGNOSTIC-009"
    diag9_dir.mkdir(parents=True, exist_ok=True)

    checkpoint_file = diag9_dir / "_checkpoint.json"
    if checkpoint_file.exists():
        with open(checkpoint_file, "r") as f:
            checkpoint = json.load(f)
        print(f"Resuming: {len(checkpoint['completed_runs'])}/96 done")
    else:
        checkpoint = {"completed_runs": []}

    oracle = EvidenceOracle()
    engine_adapter = EngineerAdapter(
        LiveEngineerModel(timeout=60, max_tokens=2048, live=True,
                          model=MODEL_NAME))

    all_results = []

    for task_id in ["BENCH2-002", "BENCH2-004", "BENCH2-005"]:
        for cond in CONDITIONS:
            print(f"\n=== {task_id} / {cond} ===")
            for i in range(1, RUNS_PER_CELL + 1):
                run_id = f"{task_id}-{cond}-run{i:02d}"

                if run_id in checkpoint["completed_runs"]:
                    print(f"  {run_id}: SKIPPED")
                    manifest = diag9_dir / task_id / cond / f"manifest-{run_id}.json"
                    if manifest.exists():
                        with open(manifest) as f:
                            all_results.append(json.load(f))
                    continue

                print(f"  Run {i}/{RUNS_PER_CELL}...")
                try:
                    r = run_single(task_id, cond, i, oracle, engine_adapter, diag9_dir)
                except Exception as e:
                    r = {"run_id": run_id, "task_id": task_id, "condition": cond,
                         "run_number": i, "status": "INCOMPLETE", "failure": str(e)}
                all_results.append(r)

                checkpoint["completed_runs"].append(run_id)
                with open(checkpoint_file, "w") as f:
                    json.dump(checkpoint, f)

                adh = r.get("error_adherence", "?")
                print(f"    adh={adh}, status={r['status']}")
                print(f"    Checkpoint ({len(checkpoint['completed_runs'])}/96)")

    # Summary
    print("\n=== Summary ===")
    cells = {}
    for r in all_results:
        key = f"{r.get('task_id','?')}-{r.get('condition','?')}"
        cells.setdefault(key, []).append(r)

    for key in sorted(cells.keys()):
        runs = cells[key]
        comp = [r for r in runs if r["status"] == "COMPLETED"]
        adh = sum(1 for r in comp if r.get("error_adherence"))
        n = len(comp)
        lo, hi = _clopper_pearson_ci(adh, n) if n > 0 else (0, 0)
        print(f"  {key:30s} {adh}/{n} = {adh/n:.0%} CI=[{lo:.1%},{hi:.1%}]" if n > 0
              else f"  {key:30s} N/A")

    index = {
        "experiment": "P126-E3A-WORDING-DECONFOUNDING",
        "model_id": MODEL_ID, "model_name": MODEL_NAME,
        "runs_per_cell": RUNS_PER_CELL,
        "total_attempted": len(all_results),
        "total_completed": sum(1 for r in all_results if r["status"]=="COMPLETED"),
        "total_incomplete": sum(1 for r in all_results if r["status"]!="COMPLETED"),
        "cells": {k: {
            "completed": len([r for r in v if r["status"]=="COMPLETED"]),
            "adherent": sum(1 for r in v if r["status"]=="COMPLETED" and r.get("error_adherence")),
        } for k, v in cells.items()},
        "results": [{
            "run_id": r["run_id"], "task_id": r.get("task_id"),
            "condition": r["condition"], "status": r["status"],
            "error_adherence": r.get("error_adherence"),
            "error_delta": r.get("error_delta"),
            "proposal_changed": r.get("proposal_changed"),
        } for r in all_results],
    }
    (diag9_dir / "RUN_INDEX.json").write_text(
        json.dumps(index, indent=2), encoding="utf-8")
    print("\nRUN_INDEX written. DIAGNOSTIC-009 EXECUTION COMPLETE.")


if __name__ == "__main__":
    main()
