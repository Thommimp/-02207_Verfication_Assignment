import pyuvm
from cocotb.triggers import ClockCycles

from cl_marb_tb_base_test import cl_marb_tb_base_test
from vseqs.cl_marb_tb_basic_seq import cl_marb_tb_basic_seq


@pyuvm.test()
class cl_marb_tb_basic_test(cl_marb_tb_base_test):
    # Minimal test for A2. Includes read and write with static and dynamic priority

    async def run_phase(self):
        self.raise_objection()
        await super().run_phase()

        # Start SDT IF assertions chekers for producers and consumer
        self.virtual_sequence = cl_marb_tb_basic_seq.create(name="cl_mark_tb_base_test")
        await self.virtual_sequence.start(seqr=self.marb_tb_env.virtual_sequencer)

        await ClockCycles(self.dut.clk, 20)  # let the last transfer show in waves
        self.drop_objection()