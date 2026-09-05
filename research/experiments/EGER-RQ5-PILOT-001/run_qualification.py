"""P173 — Model qualification test (P172 §6).

Pre-experiment readiness test: determines whether the chosen model reliably
produces VALID_SDC under the frozen task prompts. NOT experimental data —
its outputs are recorded in the readiness record, never in the experiment
dataset, and cannot be retrofitted into the experiment.

Procedure (P172 §6):
- Run the frozen task prompt (T1 and T2 contexts) K=3 times each (6 total),
  WITHOUT any revision loop.
- Classify each output with the candidate-validity gate.
- Pass criterion: >= 5/6 VALID_SDC, including at least one per task, with
  NO empty/provider failures.

On failure: the model is disqualified for that task set; a different
model/provider must be selected and re-qualified before any experiment.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PILOT_DIR = Path(__file__).resolve().parent
for p in (str(PROJECT_ROOT), str(PILOT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from harness.candidate_validity import classify_candidate, VALID_SDC, EMPTY_OUTPUT, PROVIDER_FAILURE
from harness.tasks import TASKS
from harness.trial_runner import _build_prompt
from harness.providers import build_model_call

K = 3  # invocations per task (frozen)
PASS_THRESHOLD = 5  # >= 5/6 VALID_SDC
REQUIRED_PER_TASK = 1


def run_qualification(model: str = "opencode/mimo-v2.5-free", timeout_seconds: int = 180) -> dict:
    # P173-R: model is a file-writing agent; run it in a scratch dir so it
    # writes timing.sdc there (providers reads the file back).
    workdir = PILOT_DIR / "model_scratch"
    model_call = build_model_call(
        model=model, cwd=PROJECT_ROOT, workdir=workdir, timeout_seconds=timeout_seconds,
    )
    results = []
    for task_id in ("T1", "T2"):
        task = TASKS[task_id]
        for i in range(1, K + 1):
            prompt = _build_prompt(task["design_context"], task["initial_sdc"], [], task_id)
            raw = model_call(prompt)
            validity = classify_candidate(raw, task_id=task_id)
            results.append({
                "task_id": task_id,
                "invocation": i,
                "validity": validity,
                "output_preview": (raw or "")[:120],
                "output_hash": __import__("hashlib").sha256((raw or "").encode("utf-8")).hexdigest(),
            })

    valid = [r for r in results if r["validity"] == VALID_SDC]
    per_task_valid = {t: sum(1 for r in valid if r["task_id"] == t) for t in ("T1", "T2")}
    empty_or_provider = [r for r in results if r["validity"] in (EMPTY_OUTPUT, PROVIDER_FAILURE)]

    passed = (
        len(valid) >= PASS_THRESHOLD
        and all(per_task_valid[t] >= REQUIRED_PER_TASK for t in ("T1", "T2"))
        and len(empty_or_provider) == 0
    )

    return {
        "model": model,
        "invocations": len(results),
        "pass_threshold": PASS_THRESHOLD,
        "required_per_task": REQUIRED_PER_TASK,
        "valid_count": len(valid),
        "per_task_valid": per_task_valid,
        "empty_or_provider_count": len(empty_or_provider),
        "passed": passed,
        "results": results,
    }


def main() -> int:
    print("=" * 60)
    print("P173 — MODEL QUALIFICATION TEST (P172 §6)")
    print("=" * 60)
    print("NOTE: This is a readiness gate. Outputs are NOT experimental data.")
    report = run_qualification()
    print(f"\nModel: {report['model']}")
    print(f"Invocations: {report['invocations']}")
    print(f"VALID_SDC: {report['valid_count']}/{report['invocations']} "
          f"(threshold >= {report['pass_threshold']})")
    print(f"Per-task valid: {report['per_task_valid']}")
    print(f"Empty/provider failures: {report['empty_or_provider_count']}")
    print("\nPer-invocation classification:")
    for r in report["results"]:
        print(f"  {r['task_id']} #{r['invocation']}: {r['validity']:15s} {r['output_preview']!r}")
    print(f"\nRESULT: {'PASS' if report['passed'] else 'FAIL'}")
    if report["passed"]:
        print("Decision: QUALIFIED - may proceed to experiment readiness")
    else:
        print("Decision: DISQUALIFIED - select and re-qualify a different model")

    # Record the readiness record locally (publication-sensitive, not committed
    # as experimental data; stored next to raw experiment artifacts).
    out = PILOT_DIR / "qualification_record.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Record written: {out}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())