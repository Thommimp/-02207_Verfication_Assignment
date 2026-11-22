import cocotb
from cocotb.queue import Queue
from pyuvm import ConfigDB, uvm_env

from cl_marb_tb_reg_model import cl_marb_tb_reg_model
from cl_marb_tb_virtual_sequencer import cl_marb_tb_virtual_sequencer
from uvc.apb import cl_apb_agent, if_apb_assert_check
from uvc.sdt import cl_sdt_agent
from uvc.ssdt import cl_ssdt_agent


class cl_marb_tb_env(uvm_env):
    def __init__(self, name, parent):
        super().__init__(name, parent)

        # Configuration object handle
        self.cfg = None

        # Virtual sequencer
        self.virtual_sequencer = None

        self.reg_model = None

        self.uvc_sdt_prod0 = None
        self.uvc_sdt_prod1 = None
        self.uvc_sdt_prod2 = None
        
        self.prod0_rd_data_queue = None
        self.prod0_wr_data_queue = None
        self.prod1_rd_data_queue = None
        self.prod1_wr_data_queue = None
        self.prod2_rd_data_queue = None
        self.prod2_wr_data_queue = None
        
        self.cons_rd_data_queue = None
        self.cons_wr_data_queue = None

        self.uvc_sdt_cons = None
        self.uvc_ssdt = None

        self.apb_agent = None

    def build_phase(self):
        self.logger.info("Start build_phase() -> MARB env")
        super().build_phase()

        # Get the configuration object
        self.cfg = ConfigDB().get(
            context    = self,
            inst_name  = "",
            field_name = "cfg",
        )

        # Create virtual_sequencer and pass handler to cfg
        ConfigDB().set(
            context    = self,
            inst_name  = "virtual_sequencer",
            field_name = "cfg",
            value      = self.cfg,
        )
        self.virtual_sequencer = cl_marb_tb_virtual_sequencer.create(
            name   = "virtual_sequencer",
            parent = self,
        )
        self.reg_model = cl_marb_tb_reg_model("reg_model")


        # Instantiate the APB UVC and pass handler to cfg
        ConfigDB().set(
            context    = self,
            inst_name  = "apb_agent",
            field_name = "cfg",
            value      = self.cfg.apb_cfg,
        )
        self.apb_agent = cl_apb_agent.create(
            parent = self,
            name = "apb_agent",
        )

        # producer quees
        self.prod0_rd_data_queue = Queue()
        self.prod0_wr_data_queue = Queue()
        self.prod1_rd_data_queue = Queue()
        self.prod1_wr_data_queue = Queue()
        self.prod2_rd_data_queue = Queue()
        self.prod2_wr_data_queue = Queue()

        # --- sdt producers ---
        # Create the consumer agent using the factory.
        self.uvc_sdt_prod0 = cl_sdt_agent.create("uvc_sdt_prod0_agent", self)
        self.uvc_sdt_prod1 = cl_sdt_agent.create("uvc_sdt_prod1_agent", self)
        self.uvc_sdt_prod2 = cl_sdt_agent.create("uvc_sdt_prod2_agent", self)

        ConfigDB().set(
            context = self,
            inst_name = "uvc_sdt_prod0_agent",
            field_name = "cfg",
            value = self.cfg.sdt_prod0_cfg,
        )

        ConfigDB().set(
            context=self,
            inst_name="uvc_sdt_prod0_agent.driver",
            field_name="rd_data_queue",
            value=self.prod0_rd_data_queue,
        )

        ConfigDB().set(
            context=self,
            inst_name="uvc_sdt_prod0_agent.driver",
            field_name="wr_data_queue",
            value=self.prod0_wr_data_queue,
        )

        ConfigDB().set(
            context = self,
            inst_name = "uvc_sdt_prod1_agent",
            field_name = "cfg",
            value = self.cfg.sdt_prod1_cfg,
        )

        ConfigDB().set(
            context=self,
            inst_name="uvc_sdt_prod1_agent.driver",
            field_name="rd_data_queue",
            value=self.prod1_rd_data_queue,
        )

        ConfigDB().set(
            context=self,
            inst_name="uvc_sdt_prod1_agent.driver",
            field_name="wr_data_queue",
            value=self.prod1_wr_data_queue,
        )

        ConfigDB().set(
            context = self,
            inst_name = "uvc_sdt_prod2_agent",
            field_name = "cfg",
            value = self.cfg.sdt_prod2_cfg,
        )

        ConfigDB().set(
            context=self,
            inst_name="uvc_sdt_prod2_agent.driver",
            field_name="rd_data_queue",
            value=self.prod2_rd_data_queue,
        )

        ConfigDB().set(
            context=self,
            inst_name="uvc_sdt_prod2_agent.driver",
            field_name="wr_data_queue",
            value=self.prod2_wr_data_queue,
        )

        # sdt consumer
        self.cons_rd_data_queue = Queue()
        self.cons_wr_data_queue = Queue()
        self.uvc_sdt_cons = cl_sdt_agent.create("uvc_sdt_cons_agent", self)
        
        ConfigDB().set(
            context = self,
            inst_name = "uvc_sdt_cons_agent",
            field_name = "cfg",
            value = self.cfg.sdt_cons_cfg,
        )

        ConfigDB().set(
            context = self,
            inst_name = "uvc_sdt_cons_agent.driver",
            field_name = "rd_data_queue",
            value = self.cons_rd_data_queue,
        )

        ConfigDB().set(
            context = self,
            inst_name = "uvc_sdt_cons_agent.driver",
            field_name = "wr_data_queue",
            value = self.cons_wr_data_queue, 
        )

        # ssdt - crc
        self.uvc_ssdt = cl_ssdt_agent.create("uvc_ssdt_agent", self)
        ConfigDB().set(
            context    = self,
            inst_name  = "uvc_ssdt_agent",
            field_name = "cfg",
            value      = self.cfg.ssdt_cfg,
        )

        # Assertions checkers

        self.assert_check_apb = if_apb_assert_check(
            vif = self.cfg.apb_cfg.vif,
        )
        self.assert_check_apb.cfg = self.cfg.apb_cfg


        self.logger.info("End build_phase() -> MARB env")

    def connect_phase(self):
        self.logger.info("Start connect_phase() -> MARB env")
        super().connect_phase()

        self.virtual_sequencer.apb_agent_sequencer = self.apb_agent.sequencer
        self.virtual_sequencer.reg_model = self.reg_model

        # connect sdt agents
        self.virtual_sequencer.sdt_prod0_agent_sequencer = self.uvc_sdt_prod0.sequencer
        self.virtual_sequencer.sdt_prod1_agent_sequencer = self.uvc_sdt_prod1.sequencer
        self.virtual_sequencer.sdt_prod2_agent_sequencer = self.uvc_sdt_prod2.sequencer

        self.virtual_sequencer.sdt_cons_agent_sequencer = self.uvc_sdt_cons.sequencer

        self.logger.info("End connect_phase() -> MARB env")

    async def run_phase(self):

        # Start APB IF assertion checker
        cocotb.start_soon(self.assert_check_apb.check_assertions())

    def check_phase(self):
        assert self.assert_check_apb.passed, "APB IF assertions failed"
