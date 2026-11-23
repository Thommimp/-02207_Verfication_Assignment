import pyuvm
from pyuvm import uvm_factory

from cl_marb_tb_base_seq import cl_marb_tb_base_seq
from vseqs.cl_marb_tb_random_seq import cl_marb_tb_random_seq

from cl_marb_tb_base_test import cl_marb_tb_base_test
from cl_marb_tb_histogram import render_histogram


@pyuvm.test()
class cl_marb_tb_random_test(cl_marb_tb_base_test):

    def __init__(self, name="cl_marb_tb_random_test", parent=None):
        super().__init__(name, parent)

    def start_of_simulation_phase(self):
        super().start_of_simulation_phase()
        uvm_factory().set_type_override_by_type(
            original_type=cl_marb_tb_base_seq,
            override_type=cl_marb_tb_random_seq,
        )

    async def run_phase(self):
        self.raise_objection()
        await super().run_phase()
        # Start the virtual sequence on the virtual sequencer
        self.virtual_sequence.randomize()
        await self.virtual_sequence.start(seqr=self.tb_env.virtual_sequencer)
        render_histogram(self.virtual_sequence.producer_responses, "cl_marb_tb_random_histogram.pdf")
        self.drop_objection()
