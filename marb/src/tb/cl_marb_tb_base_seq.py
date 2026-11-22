import cocotb
from cocotb.triggers import ClockCycles, with_timeout
from pyuvm import uvm_sequence

from cl_marb_common import MarbMode
from uvc.sdt import cl_sdt_single_zd_seq


class cl_marb_tb_base_seq(uvm_sequence):

    def __init__(self, name="cl_marb_tb_base_seq"):
        super().__init__(name)
        self.reg_cg = None

    # register config helper
    async def configure_dynamic(self, prio0, prio1, prio2):
        # Trying to encapsulate the disabling and 6 clock cycle wait as part of the util,
        # to avoid adding it every time we call it
        await self.sequencer.write_ctrl_reg(enabled=False, mode=MarbMode.DYNAMIC)
        await self.sequencer.write_dprio_reg(prio0=prio0, prio1=prio1, prio2=prio2)
        await ClockCycles(cocotb.top.clk, self.sequencer.cfg.dprio_reg_write_delay)

    # stimuli helpers that are used often
    def setup_prod_seq(self, name, access, addr, data=0):
        seq = cl_sdt_single_zd_seq(name)
        seq.randomize()
        seq.s_item.access = access
        seq.s_item.addr   = addr
        seq.s_item.data   = data
        return seq

    async def mif_respond(self):
        cons_seq = cl_sdt_single_zd_seq("cons_seq")
        cons_seq.randomize()
        rd_value = int(cons_seq.s_item.data)
        await with_timeout(cons_seq.start(self.sequencer.sdt_cons_agent_sequencer), 10, "us")
        rsp = await cons_seq.get_response()
        return rsp, rd_value

    # coverage
    def sample_reg_coverage(self):
        rm = self.sequencer.reg_model
        # self.reg_cg.sample(rm.enable, rm.mode, rm.prio0, rm.prio1, rm.prio2)
        pass