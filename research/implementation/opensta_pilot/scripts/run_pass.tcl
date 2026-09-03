# EGER P163 — OpenSTA Tcl script for PASS case
# Clock period = 10.0 ns (generous — should pass timing)

set script_dir [file dirname [file normalize [info script]]]
set lib_file $script_dir/../liberty/simple_cells.lib
set netlist_file $script_dir/../design/simple_path.v
set sdc_file $script_dir/../sdc/pass_case.sdc

read_liberty $lib_file
read_verilog $netlist_file
link_design simple_path
read_sdc $sdc_file

report_wns
report_tns
report_checks

exit
