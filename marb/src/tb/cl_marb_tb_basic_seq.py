import cocotb
from cocotb.triggers import ClockCycles, Combine, with_timeout
from pyuvm import uvm_sequence

from cl_marb_common import MarbMode
from uvc.sdt import AccessType, cl_sdt_single_zd_seq


class cl_marb_tb_basic_seq(uvm_sequence):
    async def body(self):
        clk = self.sequencer.cfg.sdt_cons_cfg.vif.clk

        # Disable arbitration while preparing the requests.
        await self.sequencer.write_ctrl_reg(
            enabled=False,
            mode=MarbMode.DYNAMIC,
        )

        # Highest number has highest priority.
        await self.sequencer.write_dprio_reg(
            prio0=0x10,
            prio1=0xFF,
            prio2=0xFD,
        )

        # Allow the priority sorter to finish.
        await ClockCycles(
            clk,
            self.sequencer.cfg.dprio_reg_write_delay,
        )

        # Producer 0 writes 0x11 to address 0x10.
        prod0_seq = cl_sdt_single_zd_seq("prod0_seq")
        prod0_seq.randomize()
        prod0_seq.s_item.access = AccessType.WR
        prod0_seq.s_item.addr = 0x10
        prod0_seq.s_item.data = 0x11

        # Producer 1 writes 0x22 to address 0x20.
        prod1_seq = cl_sdt_single_zd_seq("prod1_seq")
        prod1_seq.randomize()
        prod1_seq.s_item.access = AccessType.WR
        prod1_seq.s_item.addr = 0x20
        prod1_seq.s_item.data = 0x22

        # Producer 2 writes 0x33 to address 0x30.
        prod2_seq = cl_sdt_single_zd_seq("prod2_seq")
        prod2_seq.randomize()
        prod2_seq.s_item.access = AccessType.WR
        prod2_seq.s_item.addr = 0x30
        prod2_seq.s_item.data = 0x33

        # Consumer responds to one request per sequence start.
        cons_seq = cl_sdt_single_zd_seq("cons_seq")
        cons_seq.randomize()

        # Start all three producers together.
        prod0_task = cocotb.start_soon(
            prod0_seq.start(
                self.sequencer.sdt_prod0_agent_sequencer
            )
        )
        prod1_task = cocotb.start_soon(
            prod1_seq.start(
                self.sequencer.sdt_prod1_agent_sequencer
            )
        )
        prod2_task = cocotb.start_soon(
            prod2_seq.start(
                self.sequencer.sdt_prod2_agent_sequencer
            )
        )

        cons_task = cocotb.start_soon(
            cons_seq.start(
                self.sequencer.sdt_cons_agent_sequencer
            )
        )

        # Wait until all three requests are pending.
        await ClockCycles(clk, 2)

        assert self.sequencer.cfg.sdt_prod0_cfg.vif.wr.value == 1
        assert self.sequencer.cfg.sdt_prod1_cfg.vif.wr.value == 1
        assert self.sequencer.cfg.sdt_prod2_cfg.vif.wr.value == 1

        # Enable arbitration.
        await self.sequencer.write_ctrl_reg(
            enabled=True,
            mode=MarbMode.DYNAMIC,
        )

        # Producer 1 should be serviced first, priority 30.
        await with_timeout(cons_task, 10, "us")
        rsp = await cons_seq.get_response()

        assert rsp.access == AccessType.WR
        assert int(rsp.addr) == 0x20, "Expected producer 1 first"
        assert int(rsp.data) == 0x22

        # Producer 2 should be serviced second, priority 20.
        await with_timeout(
            cons_seq.start(
                self.sequencer.sdt_cons_agent_sequencer
            ),
            10,
            "us",
        )
        rsp = await cons_seq.get_response()

        assert rsp.access == AccessType.WR
        assert int(rsp.addr) == 0x30, "Expected producer 2 second"
        assert int(rsp.data) == 0x33

        # Producer 0 should be serviced last, priority 10.
        await with_timeout(
            cons_seq.start(
                self.sequencer.sdt_cons_agent_sequencer
            ),
            10,
            "us",
        )
        rsp = await cons_seq.get_response()

        assert rsp.access == AccessType.WR
        assert int(rsp.addr) == 0x10, "Expected producer 0 last"
        assert int(rsp.data) == 0x11

        # Check that all producer transfers complete.
        await with_timeout(
            Combine(prod0_task, prod1_task, prod2_task),
            10,
            "us",
        )

        await prod0_seq.get_response()
        await prod1_seq.get_response()
        await prod2_seq.get_response()

        self.sequencer.logger.info(
            "Dynamic priority write test passed"
        )