"""Frozen task definitions (P169 §12 / P172 §10). Do not modify.

Both tasks use the P163 3-cell substrate. Both Oracles evaluate the SAME
candidate SDC for a trial. No Oracle-specific candidates.
"""

from __future__ import annotations

from typing import Dict, Any

TASKS: Dict[str, Dict[str, Any]] = {
    "T1": {
        "task_id": "T1",
        "name": "Incomplete clock constraints",
        "design_substrate": "P163 3-cell netlist (INVX1 -> AND2X1 -> DFFX1) + synthetic simple_cells.lib",
        "initial_sdc": "create_clock -name clk -period 10.0 [get_ports clk]",
        "required_construct": "create_clock",
        "expected_construct_property": "Missing set_input_delay / set_output_delay (incomplete I/O constraints)",
        "expected_rta_relevance": "Incomplete-constraint findings (missing I/O delays)",
        "expected_opensta_relevance": "With 10.0 ns clock, internal path is met -> likely clean (WNS >= 0)",
        "expected_behavior": "T1-Rta expected REJECT (incomplete); T1-OpenSTA expected ACCEPT (clean timing) - asymmetry by design",
        "design_context": (
            "Design: simple_path (3-cell gate-level netlist)\n"
            "Cells: INVX1 (inverter), AND2X1 (2-input AND), DFFX1 (D flip-flop)\n"
            "Ports: clk (input), data_in (input), data_out (output)\n"
            "Liberty: synthetic simple_cells.lib\n"
            "Objective: Produce a complete SDC with clock, input delay, and output delay constraints."
        ),
    },
    "T2": {
        "task_id": "T2",
        "name": "Aggressive clock + missing constraints",
        "design_substrate": "P163 3-cell netlist (INVX1 -> AND2X1 -> DFFX1) + synthetic simple_cells.lib",
        "initial_sdc": "create_clock -name clk -period 0.05 [get_ports clk]",
        "required_construct": "create_clock",
        "expected_construct_property": "Aggressive clock period (0.05 ns) + missing output delay",
        "expected_rta_relevance": "Incomplete-constraint findings; syntactically valid clock",
        "expected_opensta_relevance": "0.05 ns period -> setup VIOLATION (P163: slack -0.10 ns)",
        "expected_behavior": "T2-Rta expected REJECT (incomplete); T2-OpenSTA expected REJECT (violation) unless candidate relaxes period",
        "design_context": (
            "Design: simple_path (3-cell gate-level netlist)\n"
            "Cells: INVX1 (inverter), AND2X1 (2-input AND), DFFX1 (D flip-flop)\n"
            "Ports: clk (input), data_in (input), data_out (output)\n"
            "Liberty: synthetic simple_cells.lib\n"
            "Objective: Produce a timing-correct SDC with appropriate clock period and I/O delays."
        ),
    },
}


def get_task(task_id: str) -> Dict[str, Any]:
    if task_id not in TASKS:
        raise ValueError(f"unknown task_id: {task_id}")
    return dict(TASKS[task_id])