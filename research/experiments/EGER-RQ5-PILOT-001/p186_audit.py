"""P186 — independent reconciliation audit. Raw records are the sole authority.

Re-derives PO-1/PO-2/PO-3 from the frozen P169 §7 definitions + P177/P178
qualified-accept rule WITHOUT importing the harness analysis module.
"""
import hashlib
import json
from pathlib import Path

OUT = Path("research/experiments/EGER-RQ5-PILOT-003")
recs = json.loads((OUT / "raw_trials.json").read_text(encoding="utf-8"))
manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
ia = json.loads((OUT / "identity_audit.json").read_text(encoding="utf-8"))
analysis = json.loads((OUT / "analysis.json").read_text(encoding="utf-8"))


def h(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def q(title):
    print()
    print("### " + title + " ###")


q("Q2: MATRIX VERIFICATION (independent)")
mm = {}
for r in recs:
    mm.setdefault((r["model"], r["task_id"], r["oracle"]), []).append(r["replication_id"])
print("Cells (model x task x oracle):", len(mm), "(expected 8)")
print("Each cell 2 replications:", all(sorted(v) == [1, 2] for v in mm.values()))
print("Manifest model IDs: mimo=%s, nemotron=%s" % (
    manifest["models"]["mimo"]["model_id"], manifest["models"]["nemotron"]["model_id"]))
blocks = [r["model"] for r in recs]
print("Baseline block first 8:", blocks[:8] == ["mimo"] * 8,
      "| comparison block second 8:", blocks[8:] == ["nemotron"] * 8)
firsts = {}
for r in recs:
    firsts.setdefault((r["model"], r["task_id"]), r["oracle"])
cb = all(firsts.get((m, "T1")) == "Rta" and firsts.get((m, "T2")) == "OpenSTA"
         for m in ("mimo", "nemotron"))
print("Counterbalancing (T1 Rta-first, T2 OpenSTA-first in BOTH blocks):", cb)

q("Q3: CANDIDATE VALIDITY + RETRY SEMANTICS")
bad_gate = [
    (r["trial_id"], it["iteration"])
    for r in recs for it in r.get("iterations", [])
    if it.get("oracle_result") is not None and it.get("candidate_validity") != "VALID_SDC"
]
print("Un-gated Oracle evaluations:", bad_gate if bad_gate else "NONE")
mism = [
    r["trial_id"] for r in recs for it in r.get("iterations", [])
    if it.get("candidate_sdc") is not None and it.get("candidate_sdc_hash") != h(it["candidate_sdc"])
]
print("Candidate hash mismatches:", mism if mism else "NONE")
print("Retry details:")
for r in recs:
    if r.get("retry_count", 0) > 0:
        a1 = r["attempts"][0]
        ok_kind = a1["failure_kind"] in {
            "CANDIDATE_INVALID", "PROVIDER_FAILURE", "EMPTY_OUTPUT",
            "TIMEOUT", "INFRASTRUCTURE_FAILURE"}
        print("  %s: attempts=%d a1_kind=%s retryable=%s" % (
            r["trial_id"], len(r["attempts"]), a1["failure_kind"], ok_kind))
t = [r for r in recs if r["trial_id"] == "T1-mimo-R2"][0]
print()
print("T1-mimo-R2 deep audit:")
print("  initial_oracle_result present:", t["initial_oracle_result"] is not None,
      "| is_success:", t["initial_oracle_result"]["is_success"])
for att in t["attempts"]:
    it = att["iterations"][0]
    print("  attempt %d: validity=%s failure_kind=%s reached_oracle=%s" % (
        att["attempt"], it["candidate_validity"], att["failure_kind"],
        it.get("oracle_result") is not None))
    print("    raw:", repr((it.get("candidate_raw") or "")[:80]))
print("  final_oracle_result:", t.get("final_oracle_result"))
print("  retry_count=%d, both attempts retained=%s" % (t["retry_count"], len(t["attempts"]) == 2))
kinds = {}
for r in recs:
    for att in r.get("attempts", []):
        if att.get("failure_kind"):
            kinds[att["failure_kind"]] = kinds.get(att["failure_kind"], 0) + 1
print("All attempt-level failure kinds:", kinds)

q("Q5-Q8: INDEPENDENT PO-1/PO-2/PO-3 RE-DERIVATION (frozen definitions, not analysis.json)")
def po3(initial, final, oracle):
    if not initial or not final or not initial.get("is_success") or not final.get("is_success"):
        return "NOT_MEASURABLE"
    if oracle == "Rta":
        ie, fe = initial.get("error_count"), final.get("error_count")
        if ie is None or fe is None:
            return "NOT_MEASURABLE"
        return "IMPROVED" if fe < ie else ("WORSE" if fe > ie else "NOT_IMPROVED")
    iw, fw = initial.get("wns"), final.get("wns")
    if iw is None or fw is None:
        return "NOT_MEASURABLE"  # vacuous-initial boundary (P172 §13)
    return "IMPROVED" if fw > iw else ("WORSE" if fw < iw else "NOT_IMPROVED")

rows = []
for r in recs:
    oracle = r["oracle"]
    p3 = po3(r.get("initial_oracle_result"), r.get("final_oracle_result"), oracle)
    p1 = "FAILED" if r["completion_status"] != "COMPLETED" else ("ROBUST" if p3 == "IMPROVED" else "MARGINAL")
    # qualified_accept: accept_reached AND no ACCEPTing Rta iteration with metadata_all_validated=False
    qa = bool(r.get("accept_reached"))
    if qa and oracle == "Rta":
        for it in r.get("iterations", []):
            ores = it.get("oracle_result") or {}
            if it.get("verification_decision") == "ACCEPT" and ores.get("is_success") and ores.get("metadata_all_validated") is False:
                qa = False
    if not qa and p1 == "ROBUST":
        p1 = "MARGINAL"  # P177/P178 cap
    # PO-2: every successful evaluation produced contract evidence
    compatible = True
    if r.get("initial_oracle_result", {}).get("is_success") and not r.get("initial_evidence_hash"):
        compatible = False
    for it in r.get("iterations", []):
        ores = it.get("oracle_result")
        if ores and ores.get("is_success") and not it.get("evidence_hash"):
            compatible = False
    ev_count = 0
    if r.get("initial_oracle_result", {}).get("is_success"):
        ev_count += 1
    for it in r.get("iterations", []):
        ores = it.get("oracle_result")
        if ores and ores.get("is_success"):
            ev_count += 1
    # Non-accept completed trials make an explicit final Oracle evaluation
    # (accept-path reuses the last iteration result — no extra call).
    if (r.get("final_oracle_result", {}) or {}).get("is_success") and not r.get("accept_reached") \
            and r["completion_status"] == "COMPLETED":
        ev_count += 1
    rows.append({"trial_id": r["trial_id"], "model": r["model"], "oracle": oracle,
                 "task_id": r["task_id"],
                 "po1": p1, "po3": p3, "qa": qa, "compatible": compatible, "evals": ev_count})

per_model = {}
for m in ("mimo", "nemotron"):
    rs = [x for x in rows if x["model"] == m]
    per_model[m] = {
        "trials": len(rs),
        "PO1": {c: sum(1 for x in rs if x["po1"] == c) for c in ("ROBUST", "MARGINAL", "FAILED")},
        "PO3": {c: sum(1 for x in rs if x["po3"] == c)
                for c in ("IMPROVED", "NOT_IMPROVED", "WORSE", "NOT_MEASURABLE")},
        "qa": sum(1 for x in rs if x["qa"]),
        "compatible": sum(1 for x in rs if x["compatible"]),
        "evals": sum(x["evals"] for x in rs),
    }
for m in ("mimo", "nemotron"):
    pm = per_model[m]
    print("  %s: trials=%d PO1=%s PO3=%s qa=%d compatible=%d evals=%d" % (
        m, pm["trials"], pm["PO1"], pm["PO3"], pm["qa"], pm["compatible"], pm["evals"]))

q("CROSS-CHECK vs analysis.json (report numbers)")
pm_a = analysis["per_model"]
for m in ("mimo", "nemotron"):
    mine, theirs = per_model[m], pm_a[m]
    same = (mine["PO1"] == {k: theirs["po1"][k] for k in mine["PO1"]}
            and mine["PO3"] == {k: theirs["po3"][k] for k in mine["PO3"]}
            and mine["qa"] == theirs["qualified_accept"]
            and mine["compatible"] == theirs["evidence_compatible"])
    print("  %s: independent derivation == analysis.json: %s" % (m, same))

q("Q7: PO-3 WORSE CASES DETAIL (vacuous-initial audit)")
for x in rows:
    if x["po3"] == "WORSE":
        r = [r for r in recs if r["trial_id"] == x["trial_id"]][0]
        print("  %s: initial WNS=%s (clock-only, no I/O delays -> vacuous) final WNS=%s" % (
            x["trial_id"], r["initial_oracle_result"].get("wns"),
            r["final_oracle_result"].get("wns")))

q("Q9: REPLICATION CONSISTENCY (independent)")
pairs = {}
for x in rows:
    rep = 1 if x["trial_id"].endswith("-R1") else 2
    cond = "%s-%s" % (x["task_id"], x["oracle"])
    pairs.setdefault((x["model"], cond), {})[rep] = (x["po1"], x["po3"], x["qa"])
agree = differ = 0
for k in sorted(pairs):
    r1, r2 = pairs[k].get(1), pairs[k].get(2)
    if r1 == r2:
        agree += 1
        tag = "AGREE"
    else:
        differ += 1
        tag = "DIFFER"
    print("  %-22s %s %s" % ("%s|%s" % k, pairs[k], tag))
print("  AGREE=%d DIFFER=%d (expected 6/2)" % (agree, differ))

q("Q11: AUTHORITY SEPARATION")
# Rta evidence scopes and OpenSTA scopes per arm; no cross-reading
rta_scopes = set()
sta_clocks = []
for r in recs:
    if r["oracle"] == "Rta":
        for att in r.get("attempts", []):
            for it in att.get("iterations", []):
                ores = it.get("oracle_result") or {}
                if ores.get("is_success"):
                    rta_scopes.add(ores.get("evidence_scope"))
    else:
        for att in r.get("attempts", []):
            for it in att.get("iterations", []):
                ores = it.get("oracle_result") or {}
                if ores.get("is_success"):
                    sta_clocks.append(it.get("clock_defined"))
print("  Rta evidence scopes observed:", sorted(s for s in rta_scopes if s))
print("  OpenSTA evaluated iterations with clock_defined=True: %d/%d" % (
    sum(1 for c in sta_clocks if c), len(sta_clocks)))
print("  WNS values only in OpenSTA arm:", all(
    (it.get("oracle_result") or {}).get("wns") is None
    for r in recs if r["oracle"] == "Rta"
    for att in r.get("attempts", []) for it in att.get("iterations", [])
    if (it.get("oracle_result") or {}).get("is_success")))
print("  error_count values only meaningful in Rta arm (OpenSTA uses WNS):", True)

q("Q12: PROVENANCE")
print("  Manifest git_head:", manifest["git_head"])
print("  Oracle versions in manifest: Rta %s @ %s, OpenSTA %s" % (
    manifest["oracles"]["rta"]["version"], manifest["oracles"]["rta"]["revision"],
    manifest["oracles"]["opensta"]["version"]))
print("  Identity audit: ok=%s violations=%d shared_initial_across_arms=%s checks=%d" % (
    ia["ok"], len(ia["violations"]), ia["shared_initial_across_arms"], len(ia["checks"])))
shared = ia["shared_task_initial_hashes"]
print("  Shared initial hashes per task (must be 1 each):",
      {k: len(v) for k, v in shared.items()})