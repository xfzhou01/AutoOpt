// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2022.2 (64-bit)
// Tool Version Limit: 2019.12
// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// ==============================================================

`timescale 1 ns / 1 ps

module sub_sub_55ns_55ns_55_1_1_AddSub_DSP_0(a, b, s);

input [55 - 1 : 0] a;
input [55 - 1 : 0] b;
(* USE_DSP = "YES" *) output [55 - 1 : 0] s;

assign s = a - b;

endmodule
`timescale 1 ns / 1 ps
module sub_sub_55ns_55ns_55_1_1(
    din0,
    din1,
    dout);

parameter ID = 32'd1;
parameter NUM_STAGE = 32'd1;
parameter din0_WIDTH = 32'd1;
parameter din1_WIDTH = 32'd1;
parameter dout_WIDTH = 32'd1;
input[din0_WIDTH - 1:0] din0;
input[din1_WIDTH - 1:0] din1;
output[dout_WIDTH - 1:0] dout;



sub_sub_55ns_55ns_55_1_1_AddSub_DSP_0 sub_sub_55ns_55ns_55_1_1_AddSub_DSP_0_U(
    .a( din0 ),
    .b( din1 ),
    .s( dout ));

endmodule

