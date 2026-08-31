"""Batch executor for DIAGNOSTIC-006 — runs conditions in small batches,
saves progress after each run, and can resume from checkpoint."""

import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[3]))

import json
from pathlib import Path

# Import the actual runner logic
from run_mechanism_investigation import (
    CONDITIONS, RUNS_PER_CONDITION, _clopper_pearson_ci,
    run_single, _load_design_metadata, MODEL_ID, MODEL_NAME, TASK_ID
)

from eger.engineer.model import LiveEngineerModel
from eger.engineer.adapter import EngineerAdapter
from eger.oracle.adapter import EvidenceOracle


def main():
    base = Path(__file__).parent
    diag6_dir = base / "formal" / "DIAGNOSTIC-006"
    diag6_dir.mkdir(parents=True, exist_ok=True)

    # Checkpoint file
    checkpoint_file = diag6_dir / "_checkpoint.json"
    if checkpoint_file.exists():
        with open(checkpoint_file, "r") as f:
            checkpoint = json.load(f)
        print(f"Resuming from checkpoint: {checkpoint}")
    else:
        checkpoint = {"completed_runs": [], "next_condition": "Base", "next_run": 1}

    oracle = EvidenceOracle()
    engine_adapter = EngineerAdapter(
        LiveEngineerModel(timeout=60, max_tokens=2048, live=True,
                          model=MODEL_NAME)
    )

    condition_order = ["Base", "E2b", "E3a", "E4a"]
    all_results = []

    for key in condition_order:
        cond = CONDITIONS[key]
        print(f"\n=== Condition {key}: {cond['name']} ===")
        for i in range(1, RUNS_PER_CONDITION + 1):
            run_id = f"{key}-run{i:02d}"

            # Skip if already completed
            if run_id in checkpoint["completed_runs"]:
                print(f"  {run_id}: SKIPPED (already completed)")
                continue

            print(f"  Run {i}/{RUNS_PER_CONDITION}...")
            try:
                r = run_single(key, cond, i, oracle, engine_adapter, diag6_dir)
            except Exception as e:
                r = {
                    "run_id": run_id, "condition": key,
                    "run_number": i, "status": "INCOMPLETE",
                    "failure": str(e)
                }
            all_results.append(r)

            # Update checkpoint
            checkpoint["completed_runs"].append(run_id)
            checkpoint["next_condition"] = key
            checkpoint["next_run"] = i + 1
            with open(checkpoint_file, "w") as f:
                json.dump(checkpoint, f)

            adh = r.get("error_adherence", "?")
            delta = r.get("error_delta", "?")
            print(f"    adherence={adh}, delta={delta}, status={r['status']}")
            print(f"    Checkpoint saved ({len(checkpoint['completed_runs'])}/40)")

    # Generate summary
    print("\n=== Summary ===")
    condition_results = {k: [] for k in condition_order}
    for r in all_results:
        condition_results[r["condition"]].append(r)

    summary = {}
    for key in condition_order:
        runs = condition_results[key]
        completed = [r for r in runs if r["status"] == "COMPLETED"]
        adherent = sum(1 for r in completed if r.get("error_adherence"))
        activated = sum(1 for r in completed if r.get("proposal_changed"))
        n = len(completed)
        lo, hi = _clopper_pearson_ci(adherent, n) if n > 0 else (0, 0)
        summary[key] = {
            "condition": CONDITIONS[key]["name"],
            "completed": n,
            "adherent": adherent,
            "activated": activated,
            "rate": adherent / n if n > 0 else None,
            "ci_lower": lo,
            "ci_upper": hi,
        }
        print(f"  {key}: {adherent}/{n} = {adherent/n:.0%}" if n > 0 else f"  {key}: N/A")
        print(f"       CI: [{lo:.1%}, {hi:.1%}]")

    index = {
        "experiment": "P107-ADHERENCE-MECHANISM-INVESTIGATION",
        "model_id": MODEL_ID,
        "model_name": MODEL_NAME,
        "runs_per_condition": RUNS_PER_CONDITION,
        "conditions": summary,
        "results": [{
            "run_id": r["run_id"],
            "condition": r["condition"],
            "status": r["status"],
            "error_adherence": r.get("error_adherence"),
            "error_delta": r.get("error_delta"),
            "proposal_changed": r.get("proposal_changed"),
        } for r in all_results],
    }
    (diag6_dir / "RUN_INDEX.json").write_text(
        json.dumps(index, indent=2), encoding="utf-8"
    )
    print(f"\nRUN_INDEX written to {diag6_dir / 'RUN_INDEX.json'}")
    print("DIAGNOSTIC-006 EXECUTION COMPLETE")


if __name__ == "__main__":
    main()
