// EGER P163 — Gate-level netlist for OpenSTA substrate validation
// Synthetic research substrate — NOT a real design
// Cells: INVX1, AND2X1, DFFX1

module simple_path (
    input  wire clk,
    input  wire data_in,
    output wire data_out
);

    // Internal nets
    wire n1;  // output of INVX1
    wire n2;  // output of AND2X1

    // Inverter: data_in -> n1
    INVX1 u_inv (
        .A(data_in),
        .Y(n1)
    );

    // AND2: n1 & data_in -> n2
    AND2X1 u_and (
        .A(n1),
        .B(data_in),
        .Y(n2)
    );

    // D flip-flop: clk, n2 -> data_out
    DFFX1 u_ff (
        .CK(clk),
        .D(n2),
        .Q(data_out)
    );

endmodule
