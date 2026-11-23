import pyuvm
from cocotb.triggers import ClockCycles
from pyuvm import uvm_factory

from cl_marb_tb_base_seq import cl_marb_tb_base_seq
from cl_marb_tb_base_test import cl_marb_tb_base_test
from vseqs.cl_marb_tb_basic_seq import cl_marb_tb_basic_seq


@pyuvm.test()
class cl_marb_tb_basic_test(cl_marb_tb_base_test):
    # Minimal test for A2. Includes read and write with static and dynamic priority

    def start_of_simulation_phase(self):
        super().start_of_simulation_phase()
        uvm_factory().set_type_override_by_type(
            original_type=cl_marb_tb_base_seq,
            override_type=cl_marb_tb_basic_seq,
        )

    async def run_phase(self):
        self.raise_objection()
        await super().run_phase()

        await self.virtual_sequence.start(seqr=self.marb_tb_env.virtual_sequencer)

        await ClockCycles(self.dut.clk, 20)  # let the last transfer show in waves
        self.drop_objection()