// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2022.2 (64-bit)
// Tool Version Limit: 2019.12
// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// ==============================================================

`timescale 1 ns / 1 ps

module add_add_4ns_4ns_4_4_1_Adder_0(clk, reset, ce, a, b, s);

// ---- input/output ports list here ----
input   clk;
input   reset;
input   ce;
input  [4 - 1 : 0] a;
input  [4 - 1 : 0] b;
output [4 - 1 : 0] s;

// wire for the primary inputs
wire [4 - 1 : 0] ain_s0 = a;
wire [4 - 1 : 0] bin_s0 = b;

// This AddSub module have totally 4 stages. For each stage the adder's width are:
// 1 1 1 1

// Stage 1 logic
wire [1 - 1 : 0]     fas_s1;
wire                 facout_s1;
reg  [3 - 1 : 0]     ain_s1;
reg  [3 - 1 : 0]     bin_s1;
reg  [1 - 1 : 0]     sum_s1;
reg                  carry_s1;
add_add_4ns_4ns_4_4_1_Adder_0_comb_adder #(
    .N    ( 1 )
) u1 (
    .a    ( ain_s0[1 - 1 : 0] ),
    .b    ( bin_s0[1 - 1 : 0] ),
    .cin  ( 1'b0 ),
    .s    ( fas_s1 ),
    .cout ( facout_s1 )
);

always @ (posedge clk) begin
    if (ce) begin
        sum_s1   <= fas_s1;
        carry_s1 <= facout_s1;
    end
end

always @ (posedge clk) begin
    if (ce) begin
        ain_s1 <= ain_s0[4 - 1 : 1];
    end
end

always @ (posedge clk) begin
    if (ce) begin
        bin_s1 <= bin_s0[4 - 1 : 1];
    end
end

// Stage 2 logic
wire [1 - 1 : 0]     fas_s2;
wire                 facout_s2;
reg  [2 - 1 : 0]     ain_s2;
reg  [2 - 1 : 0]     bin_s2;
reg  [2 - 1 : 0]     sum_s2;
reg                  carry_s2;
add_add_4ns_4ns_4_4_1_Adder_0_comb_adder #(
    .N    ( 1 )
) u2 (
    .a    ( ain_s1[1 - 1 : 0] ),
    .b    ( bin_s1[1 - 1 : 0] ),
    .cin  ( carry_s1 ),
    .s    ( fas_s2 ),
    .cout ( facout_s2 )
);

always @ (posedge clk) begin
    if (ce) begin
        sum_s2   <= {fas_s2, sum_s1};
        carry_s2 <= facout_s2;
    end
end

always @ (posedge clk) begin
    if (ce) begin
        ain_s2 <= ain_s1[3 - 1 : 1];
    end
end

always @ (posedge clk) begin
    if (ce) begin
        bin_s2 <= bin_s1[3 - 1 : 1];
    end
end

// Stage 3 logic
wire [1 - 1 : 0]     fas_s3;
wire                 facout_s3;
reg  [1 - 1 : 0]     ain_s3;
reg  [1 - 1 : 0]     bin_s3;
reg  [3 - 1 : 0]     sum_s3;
reg                  carry_s3;
add_add_4ns_4ns_4_4_1_Adder_0_comb_adder #(
    .N    ( 1 )
) u3 (
    .a    ( ain_s2[1 - 1 : 0] ),
    .b    ( bin_s2[1 - 1 : 0] ),
    .cin  ( carry_s2 ),
    .s    ( fas_s3 ),
    .cout ( facout_s3 )
);

always @ (posedge clk) begin
    if (ce) begin
        sum_s3   <= {fas_s3, sum_s2};
        carry_s3 <= facout_s3;
    end
end

always @ (posedge clk) begin
    if (ce) begin
        ain_s3 <= ain_s2[2 - 1 : 1];
    end
end

always @ (posedge clk) begin
    if (ce) begin
        bin_s3 <= bin_s2[2 - 1 : 1];
    end
end

// Stage 4 logic
wire [1 - 1 : 0]     fas_s4;
wire                 facout_s4;
add_add_4ns_4ns_4_4_1_Adder_0_comb_adder #(
    .N    ( 1 )
) u4 (
    .a    ( ain_s3[1 - 1 : 0] ),
    .b    ( bin_s3[1 - 1 : 0] ),
    .cin  ( carry_s3 ),
    .s    ( fas_s4 ),
    .cout ( facout_s4 )
);

assign s = {fas_s4, sum_s3};

endmodule

// small adder
module add_add_4ns_4ns_4_4_1_Adder_0_comb_adder 
#(parameter
    N = 32
)(
    input  [N-1 : 0]  a,
    input  [N-1 : 0]  b,
    input  wire           cin,
    output [N-1 : 0]  s,
    output wire           cout
);
assign {cout, s} = a + b + cin;

endmodule

`timescale 1 ns / 1 ps
module add_add_4ns_4ns_4_4_1(
    clk,
    reset,
    ce,
    din0,
    din1,
    dout);

parameter ID = 32'd1;
parameter NUM_STAGE = 32'd1;
parameter din0_WIDTH = 32'd1;
parameter din1_WIDTH = 32'd1;
parameter dout_WIDTH = 32'd1;
input clk;
input reset;
input ce;
input[din0_WIDTH - 1:0] din0;
input[din1_WIDTH - 1:0] din1;
output[dout_WIDTH - 1:0] dout;



add_add_4ns_4ns_4_4_1_Adder_0 add_add_4ns_4ns_4_4_1_Adder_0_U(
    .clk( clk ),
    .reset( reset ),
    .ce( ce ),
    .a( din0 ),
    .b( din1 ),
    .s( dout ));

endmodule
