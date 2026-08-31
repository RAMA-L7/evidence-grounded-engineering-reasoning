"""Batch executor for DIAGNOSTIC-007 — runs 20 Base-rate stabilization
runs with checkpoint support for resumption."""

import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[3]))

import json
from pathlib import Path

from run_base_rate_stabilization import (
    RUNS_TOTAL, _clopper_pearson_ci, run_single,
    MODEL_ID, MODEL_NAME
)

from eger.engineer.model import LiveEngineerModel
from eger.engineer.adapter import EngineerAdapter
from eger.oracle.adapter import EvidenceOracle


def main():
    base = Path(__file__).parent
    diag7_dir = base / "formal" / "DIAGNOSTIC-007"
    diag7_dir.mkdir(parents=True, exist_ok=True)

    checkpoint_file = diag7_dir / "_checkpoint.json"
    if checkpoint_file.exists():
        with open(checkpoint_file, "r") as f:
            checkpoint = json.load(f)
        print(f"Resuming from checkpoint: {len(checkpoint['completed_runs'])}/20 done")
    else:
        checkpoint = {"completed_runs": []}

    oracle = EvidenceOracle()
    engine_adapter = EngineerAdapter(
        LiveEngineerModel(timeout=60, max_tokens=2048, live=True,
                          model=MODEL_NAME)
    )

    all_results = []

    for i in range(1, RUNS_TOTAL + 1):
        run_id = f"Base-run{i:02d}"

        if run_id in checkpoint["completed_runs"]:
            print(f"  {run_id}: SKIPPED (already completed)")
            # Load existing result
            manifest = diag7_dir / f"manifest-{run_id}.json"
            if manifest.exists():
                with open(manifest) as f:
                    all_results.append(json.load(f))
            continue

        print(f"  Run {i}/{RUNS_TOTAL}...")
        try:
            r = run_single(i, oracle, engine_adapter, diag7_dir)
        except Exception as e:
            r = {
                "run_id": run_id, "run_number": i,
                "status": "INCOMPLETE", "failure": str(e)
            }
        all_results.append(r)

        checkpoint["completed_runs"].append(run_id)
        with open(checkpoint_file, "w") as f:
            json.dump(checkpoint, f)

        adh = r.get("error_adherence", "?")
        delta = r.get("error_delta", "?")
        print(f"    adherence={adh}, delta={delta}, status={r['status']}")
        print(f"    Checkpoint saved ({len(checkpoint['completed_runs'])}/20)")

    # Summary
    completed = [r for r in all_results if r["status"] == "COMPLETED"]
    adherent = sum(1 for r in completed if r.get("error_adherence"))
    activated = sum(1 for r in completed if r.get("proposal_changed"))
    n = len(completed)
    k = adherent
    lo, hi = _clopper_pearson_ci(k, n) if n > 0 else (0, 0)

    print(f"\n=== Summary ===")
    print(f"Completed: {n}/{RUNS_TOTAL}")
    print(f"Adherent:  {k}/{n} = {k/n:.0%}" if n > 0 else "Adherent: N/A")
    print(f"Activated: {activated}/{n}")
    print(f"95% CI:    [{lo:.1%}, {hi:.1%}]")

    index = {
        "experiment": "P114-BASE-RATE-STABILIZATION",
        "model_id": MODEL_ID,
        "model_name": MODEL_NAME,
        "runs_total": RUNS_TOTAL,
        "completed": n,
        "adherent": k,
        "activated": activated,
        "rate": k / n if n > 0 else None,
        "ci_lower": lo,
        "ci_upper": hi,
        "results": [{
            "run_id": r["run_id"],
            "status": r["status"],
            "error_adherence": r.get("error_adherence"),
            "error_delta": r.get("error_delta"),
            "proposal_changed": r.get("proposal_changed"),
            "revised_sdc_length": r.get("revised_sdc_length"),
        } for r in all_results],
    }
    (diag7_dir / "RUN_INDEX.json").write_text(
        json.dumps(index, indent=2), encoding="utf-8"
    )
    print(f"\nRUN_INDEX written.")
    print("DIAGNOSTIC-007 EXECUTION COMPLETE")


if __name__ == "__main__":
    main()
