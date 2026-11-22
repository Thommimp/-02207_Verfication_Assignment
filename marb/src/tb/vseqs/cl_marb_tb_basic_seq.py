import cocotb
from cocotb.triggers import ClockCycles, Combine, with_timeout
from pyuvm import uvm_sequence

from cl_marb_common import MarbMode
from uvc.sdt import AccessType, cl_sdt_single_zd_seq
from cl_marb_tb_base_seq import cl_marb_tb_base_seq


class cl_marb_tb_basic_seq(cl_marb_tb_base_seq):

    async def body(self):
        await self.run_static()
        await self.run_dynamic()

    async def run_static(self):
        # TODO: We currently have a lot of duplication across static and dynamic methods
        # We can refactor if we have time
        clk = self.sequencer.cfg.sdt_cons_cfg.vif.clk

        # Disable arbitration until producers are setup
        await self.sequencer.write_ctrl_reg(enabled=False, mode=MarbMode.STATIC)

        # Producer 0 writes 0x11 to address 0x10.
        prod0_seq = self.setup_prod_seq(
            name="prod0_seq",
            access=AccessType.WR,
            addr=0x10,
            data=0x11
        )

        # Producer 1 writes 0x22 to address 0x20.
        prod1_seq = self.setup_prod_seq(
            name="prod1_seq",
            access=AccessType.WR,
            addr=0x20,
            data=0x22
        )

        # Producer 2 writes 0x33 to address 0x30.
        prod2_seq = self.setup_prod_seq(
            name="prod2_seq",
            access=AccessType.WR,
            addr=0x30,
            data=0x33
        )

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
            mode=MarbMode.STATIC,
        )

        # Producer 0 should be serviced first, highest default priority.
        await with_timeout(cons_task, 10, "us")
        rsp = await cons_seq.get_response()

        assert rsp.access == AccessType.WR
        assert int(rsp.addr) == 0x10, "Expected producer 0 first"
        assert int(rsp.data) == 0x11

        # Producer 1 should be serviced second, middle default priority.
        await with_timeout(
            cons_seq.start(
                self.sequencer.sdt_cons_agent_sequencer
            ),
            10,
            "us",
        )
        rsp = await cons_seq.get_response()

        assert rsp.access == AccessType.WR
        assert int(rsp.addr) == 0x20, "Expected producer 1 second"
        assert int(rsp.data) == 0x22

        # Producer 2 should be serviced last, lowest default priority.
        await with_timeout(
            cons_seq.start(
                self.sequencer.sdt_cons_agent_sequencer
            ),
            10,
            "us",
        )
        rsp = await cons_seq.get_response()

        assert rsp.access == AccessType.WR
        assert int(rsp.addr) == 0x30, "Expected producer 2 last"
        assert int(rsp.data) == 0x33

        # Check that all producer transfers complete.
        await with_timeout(
            Combine(prod0_task, prod1_task, prod2_task),
            10,
            "us",
        )

        await prod0_seq.get_response()
        await prod1_seq.get_response()
        await prod2_seq.get_response()
        self.sample_register_coverage()

        self.sequencer.logger.info(
            "Static priority write test passed"
        )

    async def run_dynamic(self):
        clk = self.sequencer.cfg.sdt_cons_cfg.vif.clk

        await self.configure_dynamic(prio0=0x10, prio1=0xFF, prio2=0xFD)

        # Producer 0 writes 0x11 to address 0x10.
        prod0_seq = self.setup_prod_seq(
            name="prod0_seq",
            access=AccessType.WR,
            addr=0x10,
            data=0x11
        )

        # Producer 1 writes 0x22 to address 0x20.
        prod1_seq = self.setup_prod_seq(
            name="prod1_seq",
            access=AccessType.WR,
            addr=0x20,
            data=0x22
        )

        # Producer 2 writes 0x33 to address 0x30.
        prod2_seq = self.setup_prod_seq(
            name="prod2_seq",
            access=AccessType.WR,
            addr=0x30,
            data=0x33
        )

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

        # Producer 1 should be serviced first, priority FF.
        await with_timeout(cons_task, 10, "us")
        rsp = await cons_seq.get_response()

        assert rsp.access == AccessType.WR
        assert int(rsp.addr) == 0x20, "Expected producer 1 first"
        assert int(rsp.data) == 0x22

        # Producer 2 should be serviced second, priority FD.
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
        self.sample_register_coverage()

        self.sequencer.logger.info(
            "Dynamic priority write test passed"
        )