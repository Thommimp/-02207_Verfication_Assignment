from pyuvm import uvm_object

from uvc.apb import cl_apb_config
from uvc.sdt import cl_sdt_config, DriverType

class cl_marb_tb_config(uvm_object):
    def __init__(self, name = "cl_marb_tb_config"):
        super().__init__(name)

        self.apb_cfg = cl_apb_config.create("apb_cfg")

        self.sdt_prod0_cfg = cl_sdt_config.create("sdt_prod0_cfg")
        self.sdt_prod1_cfg = cl_sdt_config.create("sdt_prod1_cfg")
        self.sdt_prod2_cfg = cl_sdt_config.create("sdt_prod2_cfg")

        self.sdt_cons_cfg = cl_sdt_config.create("sdt_cons_cfg")

        # Configure Producer 0
        self.sdt_prod0_cfg.driver = DriverType.PRODUCER
        self.sdt_prod0_cfg.ADDR_WIDTH = 8
        self.sdt_prod0_cfg.DATA_WIDTH = 8

        # Configure Producer 1
        self.sdt_prod1_cfg.driver = DriverType.PRODUCER
        self.sdt_prod1_cfg.ADDR_WIDTH = 8
        self.sdt_prod1_cfg.DATA_WIDTH = 8

        # Configure Producer 2
        self.sdt_prod2_cfg.driver = DriverType.PRODUCER
        self.sdt_prod2_cfg.ADDR_WIDTH = 8
        self.sdt_prod2_cfg.DATA_WIDTH = 8

        # Configure Consumer
        self.sdt_cons_cfg.driver = DriverType.CONSUMER
        self.sdt_cons_cfg.ADDR_WIDTH = 8
        self.sdt_cons_cfg.DATA_WIDTH = 8


        # Delay to avoid a hazard when updating the dynamic priority
        self.dprio_reg_write_delay = 6
