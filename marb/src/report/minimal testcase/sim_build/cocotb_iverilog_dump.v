module cocotb_iverilog_dump();
initial begin
    $dumpfile("sim_build/mem_arb_wrapper.fst");
    $dumpvars(0, mem_arb_wrapper);
end
endmodule
