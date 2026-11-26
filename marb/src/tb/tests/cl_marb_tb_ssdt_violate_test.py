import cocotb
import pyuvm
from cocotb.handle import Force, Release
from cocotb.triggers import FallingEdge

from cl_marb_tb_base_test import cl_marb_tb_base_test
from uvc.ssdt.ssdt_if_assertions import if_ssdt_assert_check


@pyuvm.test()
class cl_marb_tb_ssdt_assert_test(cl_marb_tb_base_test):

    async def run_phase(self):
        self.raise_objection()
        await super().run_phase()

        vif = self.ssdt_cons_if
        checker = if_ssdt_assert_check(vif=vif)
        await FallingEdge(vif.clk)
        cocotb.start_soon(checker.check_assertions())

        # SSDT PR3: data must be zero when valid is low.
        vif.valid.value = 0
        vif.data.value = 1
        try:
            await FallingEdge(vif.clk)
        finally:
            vif.data.value = Release()
            vif.valid.value = Release()

        assert checker.passed, "SSDT PR3 violation on CRC output: data must be zero when valid is low"
        self.drop_objection()
