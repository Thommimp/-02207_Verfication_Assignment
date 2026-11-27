import pyuvm
from cocotb.triggers import ClockCycles, FallingEdge

from cl_marb_tb_base_test import cl_marb_tb_base_test


@pyuvm.test()
class cl_marb_tb_assert_test(cl_marb_tb_base_test):

    async def run_phase(self):
        self.raise_objection()
        await super().run_phase()

        # PR1: Asserting rd and wr simultaneously is illegal
        await FallingEdge(self.dut.clk)

        self.sdt_prod0_if.wr.value = 1
        self.sdt_prod0_if.rd.value = 1

        await ClockCycles(self.dut.clk, 5)

        await FallingEdge(self.dut.clk)

        self.sdt_prod0_if.wr.value = 0
        self.sdt_prod0_if.rd.value = 0

        self.drop_objection()