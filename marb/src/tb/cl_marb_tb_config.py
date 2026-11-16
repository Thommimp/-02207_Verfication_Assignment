from pyuvm import uvm_object

from uvc.apb import cl_apb_config
from uvc.sdt import cl_sdt_config



class cl_marb_tb_config(uvm_object):
    def __init__(self, name = "cl_marb_tb_config"):
        super().__init__(name)

        self.apb_cfg             = cl_apb_config.create("apb_cfg")

        self.sdt_prod1_conf      = cl_sdt_config.create("sdt_prod1_cfg")
        self.sdt_prod2_conf      = cl_sdt_config.create("sdt_prod2_cfg")
        self.sdt_prod3_conf      = cl_sdt_config.create("sdt_prod3_cfg")

        self.sdt_cons_conf      = cl_sdt_config.create("sdt_cons_cfg")

        # Configure Producer 1
        self.sdt_prod1_cfg.driver = uvc_ssdt_type_enum.PRODUCER
        self.sdt_prod1_cfg.ADDR_WIDTH = 8
        self.sdt_prod1_cfg.DATA_WIDTH = 8

        # Configure Producer 2
        self.sdt_prod2_cfg.driver = uvc_ssdt_type_enum.PRODUCER
        self.sdt_prod2_cfg.ADDR_WIDTH = 8
        self.sdt_prod2_cfg.DATA_WIDTH = 8

        # Configure Producer 3
        self.sdt_prod3_cfg.driver = uvc_ssdt_type_enum.PRODUCER
        self.sdt_prod3_cfg.ADDR_WIDTH = 8
        self.sdt_prod3_cfg.DATA_WIDTH = 8

        # Configure Consumer
        self.sdt_prod1_cfg.driver = uvc_ssdt_type_enum.CONSUMER
        self.sdt_prod1_cfg.ADDR_WIDTH = 8
        self.sdt_prod1_cfg.DATA_WIDTH = 8


        # Delay to avoid a hazard when updating the dynamic priority
        self.dprio_reg_write_delay = 6
