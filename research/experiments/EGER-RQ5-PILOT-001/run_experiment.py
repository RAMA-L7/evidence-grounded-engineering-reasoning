"""P170 — RQ-5 Controlled Oracle-Validation Experiment Execution.

Frozen protocol from P169. No methodology changes after this point.
"""

import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

sys.stdout.reconfigure(encoding="utf-8")
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
EXPERIMENT_DIR = Path(__file__).resolve().parent
SUBSTRATE_BASE = PROJECT_ROOT / "research" / "implementation" / "opensta_pilot"

# Import EGER components
sys.path.insert(0, str(PROJECT_ROOT))
from eger.oracle.adapter import EvidenceOracle, OracleResult
from eger.oracle.opensta_adapter import OpenSTAAdapter
from eger.evidence.normalizer import EvidenceNormalizer
from eger.verification.gate import VerificationGate
from eger.engineer.candidate import build_candidate
from eger.task.definition import TaskDefinition


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Environment setup
# ---------------------------------------------------------------------------

def get_opensta_binary() -> Path:
    """Resolve WSL OpenSTA binary path."""
    r = subprocess.run(
        ["wsl", "-d", "Ubuntu-24.04", "bash", "-c", "echo $HOME"],
        capture_output=True, text=True, timeout=10,
    )
    wsl_home = r.stdout.strip()
    sta_wsl = f"{wsl_home}/opensta_build/OpenSTA/app/sta"
    r = subprocess.run(
        ["wsl", "-d", "Ubuntu-24.04", "wslpath", "-w", sta_wsl],
        capture_output=True, text=True, timeout=10,
    )
    return Path(r.stdout.strip())


def invoke_opencode(prompt: str, timeout: int = 60) -> str:
    """Invoke OpenCode model to generate SDC."""
    try:
        result = subprocess.run(
            ["opencode.cmd", "run", "--model", "opencode/mimo-v2.5-free", prompt],
            capture_output=True, text=True, timeout=timeout,
            cwd=str(PROJECT_ROOT),
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return ""
    except Exception as e:
        return f"ERROR: {e}"


# ---------------------------------------------------------------------------
# Task definitions (FROZEN from P169)
# ---------------------------------------------------------------------------

# T1: Incomplete clock constraints
T1_INITIAL_SDC = """create_clock -name clk -period 10.0 [get_ports clk]"""

T1_DESIGN_CONTEXT = """Design: simple_path (3-cell gate-level netlist)
Cells: INVX1 (inverter), AND2X1 (2-input AND), DFFX1 (D flip-flop)
Ports: clk (input), data_in (input), data_out (output)
Liberty: synthetic simple_cells.lib
Objective: Produce a complete SDC with clock, input delay, and output delay constraints."""

# T2: Aggressive timing + missing constraints
T2_INITIAL_SDC = """create_clock -name clk -period 0.05 [get_ports clk]"""

T2_DESIGN_CONTEXT = """Design: simple_path (3-cell gate-level netlist)
Cells: INVX1 (inverter), AND2X1 (2-input AND), DFFX1 (D flip-flop)
Ports: clk (input), data_in (input), data_out (output)
Liberty: synthetic simple_cells.lib
Objective: Produce a timing-correct SDC with appropriate clock period and I/O delays."""


# ---------------------------------------------------------------------------
# Trial execution
# ---------------------------------------------------------------------------

def run_trial(
    trial_id: str,
    task_id: str,
    oracle_name: str,
    replicate: int,
    initial_sdc: str,
    design_context: str,
    oracle_adapter,
    normalizer: EvidenceNormalizer,
    gate: VerificationGate,
    max_iterations: int = 3,
) -> Dict[str, Any]:
    """Execute one trial of the RQ-5 experiment."""
    trial = {
        "trial_id": trial_id,
        "task_id": task_id,
        "oracle": oracle_name,
        "replicate": replicate,
        "initial_sdc": initial_sdc,
        "initial_sdc_hash": sha256_text(initial_sdc),
        "iterations": [],
        "completion_status": "IN_PROGRESS",
        "failure_kind": None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    current_sdc = initial_sdc
    oracle_call_count = 0

    for iteration in range(max_iterations):
        iter_record = {"iteration": iteration + 1}

        # Generate candidate using OpenCode
        prompt = f"""You are an SDC constraint author for a VLSI design.

Design context:
{design_context}

Current SDC:
{current_sdc}

Oracle feedback from previous iteration:
{trial["iterations"][-1]["oracle_findings"] if trial["iterations"] else "None (first iteration)"}

Task: Improve the SDC constraints based on the oracle feedback.
Return ONLY the improved SDC text, nothing else. No explanations."""

        candidate_sdc = invoke_opencode(prompt, timeout=60)
        if not candidate_sdc or candidate_sdc.startswith("ERROR:"):
            trial["completion_status"] = "FAILED"
            trial["failure_kind"] = "PROVIDER_FAILURE"
            break

        # Clean up model output (remove markdown fences if present)
        candidate_sdc = candidate_sdc.strip()
        if candidate_sdc.startswith("```"):
            lines = candidate_sdc.split("\n")
            candidate_sdc = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
            candidate_sdc = candidate_sdc.strip()

        iter_record["candidate_sdc"] = candidate_sdc
        iter_record["candidate_sdc_hash"] = sha256_text(candidate_sdc)

        # Invoke Oracle
        oracle_start = time.time()
        try:
            if oracle_name == "Rta":
                result = oracle_adapter.validate(
                    sdc_text=candidate_sdc,
                    input_identity=f"trial-{trial_id}-iter-{iteration+1}",
                )
            else:  # OpenSTA
                netlist = SUBSTRATE_BASE / "design" / "simple_path.v"
                lib = SUBSTRATE_BASE / "liberty" / "simple_cells.lib"
                result = oracle_adapter.validate(
                    sdc_text=candidate_sdc,
                    netlist_path=netlist,
                    lib_path=lib,
                    design_name="simple_path",
                    input_identity=f"trial-{trial_id}-iter-{iteration+1}",
                )
            oracle_call_count += 1
            oracle_runtime = time.time() - oracle_start
        except Exception as e:
            oracle_runtime = time.time() - oracle_start
            trial["completion_status"] = "FAILED"
            trial["failure_kind"] = "ORACLE_FAILURE"
            iter_record["oracle_error"] = str(e)
            trial["iterations"].append(iter_record)
            break

        iter_record["oracle_runtime"] = oracle_runtime
        iter_record["oracle_is_success"] = result.is_success

        if not result.is_success:
            iter_record["oracle_failure_kind"] = result.failure.kind if result.failure else "UNKNOWN"
            iter_record["oracle_findings"] = result.failure.message if result.failure else ""
            trial["iterations"].append(iter_record)
            # Continue to next iteration (revision loop should handle this)
            current_sdc = candidate_sdc
            continue

        # Record Oracle result
        if oracle_name == "Rta":
            iter_record["oracle_status"] = result.evidence.oracle_status
            iter_record["oracle_findings"] = json.dumps([
                {"severity": f.get("severity"), "code": f.get("code"), "message": f.get("message")}
                for f in result.evidence.findings
            ], indent=2)
            iter_record["evidence_scope"] = result.evidence.evidence_scope
            iter_record["finding_count"] = len(result.evidence.findings)
            iter_record["error_count"] = sum(1 for f in result.evidence.findings if f.get("severity") == "error")
        else:  # OpenSTA
            iter_record["oracle_status"] = result.evidence.oracle_status
            iter_record["wns"] = result.evidence.analysis_scope.get("wns")
            iter_record["tns"] = result.evidence.analysis_scope.get("tns")
            iter_record["has_violations"] = result.evidence.analysis_scope.get("has_violations")
            iter_record["oracle_findings"] = json.dumps([
                {"severity": f.get("severity"), "code": f.get("code"), "message": f.get("message")}
                for f in result.evidence.findings
            ], indent=2)
            iter_record["evidence_scope"] = result.evidence.evidence_scope

        iter_record["evidence_hash"] = result.evidence.evidence_hash if result.evidence else None

        # Check verification
        if result.evidence:
            evidence = normalizer.normalize(
                result.evidence,
                task_id=task_id,
                candidate_hash=sha256_text(candidate_sdc)[:12],
            )
            candidate = build_candidate(candidate_sdc)
            verification = gate.evaluate(candidate, evidence)
            iter_record["verification_decision"] = verification.decision

            if verification.decision == "ACCEPT":
                trial["completion_status"] = "COMPLETED"
                trial["final_sdc"] = candidate_sdc
                trial["final_sdc_hash"] = sha256_text(candidate_sdc)
                trial["iterations"].append(iter_record)
                break
        else:
            iter_record["verification_decision"] = "NO_EVIDENCE"

        trial["iterations"].append(iter_record)
        current_sdc = candidate_sdc

    # If loop completed without ACCEPT
    if trial["completion_status"] == "IN_PROGRESS":
        trial["completion_status"] = "COMPLETED"  # Completed all iterations
        trial["final_sdc"] = current_sdc
        trial["final_sdc_hash"] = sha256_text(current_sdc)

    trial["oracle_call_count"] = oracle_call_count
    trial["iteration_count"] = len(trial["iterations"])

    return trial


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def analyze_trials(trials: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Run predefined analysis on completed trials."""
    analysis = {
        "total_trials": len(trials),
        "completed": sum(1 for t in trials if t["completion_status"] == "COMPLETED"),
        "failed": sum(1 for t in trials if t["completion_status"] == "FAILED"),
        "per_condition": {},
        "per_oracle": {},
        "per_task": {},
    }

    # Per-condition
    for task in ["T1", "T2"]:
        for oracle in ["Rta", "OpenSTA"]:
            key = f"{task}-{oracle}"
            condition_trials = [t for t in trials if t["task_id"] == task and t["oracle"] == oracle]
            analysis["per_condition"][key] = {
                "count": len(condition_trials),
                "completed": sum(1 for t in condition_trials if t["completion_status"] == "COMPLETED"),
                "accepted": sum(1 for t in condition_trials
                    for it in t["iterations"]
                    if it.get("verification_decision") == "ACCEPT"),
            }

    # Per-oracle
    for oracle in ["Rta", "OpenSTA"]:
        oracle_trials = [t for t in trials if t["oracle"] == oracle]
        analysis["per_oracle"][oracle] = {
            "count": len(oracle_trials),
            "completed": sum(1 for t in oracle_trials if t["completion_status"] == "COMPLETED"),
        }

    # Per-task
    for task in ["T1", "T2"]:
        task_trials = [t for t in trials if t["task_id"] == task]
        analysis["per_task"][task] = {
            "count": len(task_trials),
            "completed": sum(1 for t in task_trials if t["completion_status"] == "COMPLETED"),
        }

    return analysis


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("P170 — RQ-5 Controlled Oracle-Validation Experiment")
    print("=" * 60)

    # Environment
    opensta_path = get_opensta_binary()
    print(f"OpenSTA binary: {opensta_path}")

    # Create Oracles
    rta_cli = PROJECT_ROOT / "rta-constraint-intelligence" / "cli.py"
    rta_oracle = EvidenceOracle(rta_cli=rta_cli, timeout_seconds=60)
    opensta_oracle = OpenSTAAdapter(sta_binary=opensta_path, timeout_seconds=60)

    normalizer = EvidenceNormalizer()
    gate = VerificationGate()

    # Verify Oracles work
    print("\nVerifying Oracles...")
    r_test = rta_oracle.validate(sdc_text=T1_INITIAL_SDC)
    print(f"  Rta: is_success={r_test.is_success}")
    o_test = opensta_oracle.validate(
        sdc_text=T1_INITIAL_SDC,
        netlist_path=SUBSTRATE_BASE / "design" / "simple_path.v",
        lib_path=SUBSTRATE_BASE / "liberty" / "simple_cells.lib",
        design_name="simple_path",
    )
    print(f"  OpenSTA: is_success={o_test.is_success}")

    # Frozen execution matrix
    trials_spec = [
        ("T1", "Rta", 1, T1_INITIAL_SDC, T1_DESIGN_CONTEXT),
        ("T1", "Rta", 2, T1_INITIAL_SDC, T1_DESIGN_CONTEXT),
        ("T1", "OpenSTA", 1, T1_INITIAL_SDC, T1_DESIGN_CONTEXT),
        ("T1", "OpenSTA", 2, T1_INITIAL_SDC, T1_DESIGN_CONTEXT),
        ("T2", "Rta", 1, T2_INITIAL_SDC, T2_DESIGN_CONTEXT),
        ("T2", "Rta", 2, T2_INITIAL_SDC, T2_DESIGN_CONTEXT),
        ("T2", "OpenSTA", 1, T2_INITIAL_SDC, T2_DESIGN_CONTEXT),
        ("T2", "OpenSTA", 2, T2_INITIAL_SDC, T2_DESIGN_CONTEXT),
    ]

    all_trials = []
    for task_id, oracle_name, rep, init_sdc, design_ctx in trials_spec:
        trial_id = f"{task_id}-{oracle_name}-R{rep}"
        print(f"\n--- Trial {trial_id} ---")

        oracle = rta_oracle if oracle_name == "Rta" else opensta_oracle
        trial = run_trial(
            trial_id=trial_id,
            task_id=task_id,
            oracle_name=oracle_name,
            replicate=rep,
            initial_sdc=init_sdc,
            design_context=design_ctx,
            oracle_adapter=oracle,
            normalizer=normalizer,
            gate=gate,
            max_iterations=3,
        )
        all_trials.append(trial)
        print(f"  Status: {trial['completion_status']}")
        print(f"  Iterations: {trial['iteration_count']}")
        print(f"  Oracle calls: {trial['oracle_call_count']}")

    # Save raw results
    results_path = EXPERIMENT_DIR / "raw_trials.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(all_trials, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nRaw results saved to: {results_path}")

    # Run analysis
    analysis = analyze_trials(all_trials)
    analysis_path = EXPERIMENT_DIR / "analysis.json"
    with open(analysis_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
    print(f"Analysis saved to: {analysis_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Total trials: {analysis['total_trials']}")
    print(f"Completed: {analysis['completed']}")
    print(f"Failed: {analysis['failed']}")
    print("\nPer condition:")
    for key, val in analysis["per_condition"].items():
        print(f"  {key}: {val['count']} trials, {val['completed']} completed")

    return all_trials, analysis


if __name__ == "__main__":
    trials, analysis = main()
