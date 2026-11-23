import cocotb
import vsc
from cocotb.triggers import ClockCycles, Combine, ReadOnly, RisingEdge, with_timeout

from cl_marb_common import MarbMode
from cl_marb_tb_base_seq import cl_marb_tb_base_seq
from uvc.sdt import AccessType, cl_sdt_single_zd_seq


@vsc.randobj
class cl_marb_random_config:
    def __init__(self):
        self.order0 = vsc.rand_uint32_t()
        self.order1 = vsc.rand_uint32_t()
        self.order2 = vsc.rand_uint32_t()

        self.delay0 = vsc.rand_uint32_t()
        self.delay1 = vsc.rand_uint32_t()
        self.delay2 = vsc.rand_uint32_t()

        self.addr0 = vsc.rand_uint32_t()
        self.addr1 = vsc.rand_uint32_t()
        self.addr2 = vsc.rand_uint32_t()

        self.data0 = vsc.rand_uint32_t()
        self.data1 = vsc.rand_uint32_t()
        self.data2 = vsc.rand_uint32_t()

        self.prio0 = vsc.rand_uint32_t()
        self.prio1 = vsc.rand_uint32_t()
        self.prio2 = vsc.rand_uint32_t()

    @vsc.constraint
    def c_start_order(self):
        vsc.unique(self.order0, self.order1, self.order2)
        self.order0 in vsc.rangelist(vsc.rng(0, 2))
        self.order1 in vsc.rangelist(vsc.rng(0, 2))
        self.order2 in vsc.rangelist(vsc.rng(0, 2))

    @vsc.constraint
    def c_start_delays(self):
        self.delay0 in vsc.rangelist(vsc.rng(0, 4))
        self.delay1 in vsc.rangelist(vsc.rng(0, 4))
        self.delay2 in vsc.rangelist(vsc.rng(0, 4))

    @vsc.constraint
    def c_write_addresses(self):
        self.addr0 in vsc.rangelist(vsc.rng(0, 255))
        self.addr1 in vsc.rangelist(vsc.rng(0, 255))
        self.addr2 in vsc.rangelist(vsc.rng(0, 255))

    @vsc.constraint
    def c_write_data(self):
        self.data0 in vsc.rangelist(vsc.rng(0, 255))
        self.data1 in vsc.rangelist(vsc.rng(0, 255))
        self.data2 in vsc.rangelist(vsc.rng(0, 255))

    @vsc.constraint
    def c_dynamic_priorities(self):
        self.prio0 in vsc.rangelist(vsc.rng(0, 255))
        self.prio1 in vsc.rangelist(vsc.rng(0, 255))
        self.prio2 in vsc.rangelist(vsc.rng(0, 255))


class cl_marb_tb_random_seq(cl_marb_tb_base_seq):
    def __init__(self, name="cl_marb_tb_random_seq"):
        super().__init__(name)
        self.random_config = cl_marb_random_config()
        self.producer_responses = []

    async def body(self):
        self.random_config.randomize()

        prio0 = int(self.random_config.prio0)
        prio1 = int(self.random_config.prio1)
        prio2 = int(self.random_config.prio2)
        await self.configure_dynamic(prio0, prio1, prio2)

        clk = self.sequencer.cfg.sdt_cons_cfg.vif.clk
        addresses = [
            int(self.random_config.addr0),
            int(self.random_config.addr1),
            int(self.random_config.addr2),
        ]
        data = [
            int(self.random_config.data0),
            int(self.random_config.data1),
            int(self.random_config.data2),
        ]
        delays = [
            int(self.random_config.delay0),
            int(self.random_config.delay1),
            int(self.random_config.delay2),
        ]
        start_order = [
            int(self.random_config.order0),
            int(self.random_config.order1),
            int(self.random_config.order2),
        ]

        producer_sequencers = [
            self.sequencer.sdt_prod0_agent_sequencer,
            self.sequencer.sdt_prod1_agent_sequencer,
            self.sequencer.sdt_prod2_agent_sequencer,
        ]

        producer_sequences = []
        producer_tasks = []
        for producer in start_order:
            await ClockCycles(clk, delays[producer])

            prod_seq = self.setup_prod_seq(
                name=f"prod{producer}_random_seq",
                access=AccessType.WR,
                addr=addresses[producer],
                data=data[producer],
            )
            producer_sequences.append(prod_seq)
            producer_tasks.append(cocotb.start_soon(
                prod_seq.start(producer_sequencers[producer])
            ))

        await ClockCycles(clk, 2)

        await self.sequencer.write_ctrl_reg(
            enabled=True,
            mode=MarbMode.DYNAMIC,
        )

        cons_sequences = []
        responses = []
        for _ in range(3):
            while True:
                # This block is added because we were getting issues where the consumer seq was running,
                # even when no producer had created a request in that clock cycle. This scenario comes in
                # because of the random delays added between producer requests.
                await RisingEdge(clk)
                await ReadOnly()
                if str(cocotb.top.m_wr.value) == "1" or str(cocotb.top.m_rd.value) == "1":
                    break

            cons_seq = cl_sdt_single_zd_seq("cons_random_seq")
            cons_seq.randomize()
            cons_sequences.append(cons_seq)
            cons_task = cocotb.start_soon(
                cons_seq.start(
                    self.sequencer.sdt_cons_agent_sequencer
                )
            )
            await with_timeout(cons_task, 10, "us")
            rsp = await cons_seq.get_response()
            responses.append(rsp)
            self.producer_responses.append(int(rsp.data))

        await with_timeout(
            Combine(*producer_tasks),
            10,
            "us",
        )
        for prod_seq in producer_sequences:
            await prod_seq.get_response()

        self.sample_register_coverage()

        self.sequencer.logger.info(
            f"Random dynamic write test passed: "
            f"order={start_order}, delays={delays}, "
            f"priority=({prio0}, {prio1}, {prio2})"
        )
