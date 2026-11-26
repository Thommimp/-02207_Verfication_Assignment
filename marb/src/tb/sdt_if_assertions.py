"""SDT interface asserations wrapper"""

import cocotb
from cocotb.triggers import ReadOnly, RisingEdge
from cocotb.types import LogicArray


class if_sdt_assert_check:

    def __init__(self,vif = None, name = "if_sdt_assert_check"):

        self.name  = name

        self.vif = vif

        # Set as false if any assertion fail
        self.passed = True

    def check_assertions(self):
        cocotb.start_soon(self.single_request_requirement())
        cocotb.start_soon(self.address_validity_requirement())
        cocotb.start_soon(self.write_data_validity_requirement())
        cocotb.start_soon(self.ack_validity_requirement())
        cocotb.start_soon(self.read_data_validity_requirement())

    #PR1 Asserting rd and wr at the same time is illegal
    async def single_request_requirement(self):
        while True:
            await RisingEdge(self.vif.clk)
            await ReadOnly()

            try: 
                assert not (int(self.vif.wr.value) == 1 and int(self.vif.rd.value) == 1), \
                    "WR and RD cannot both be high at the same time"
            except AssertionError as msg:
                self.passed = False
                print(msg)
    #PR2 When rd or wr is asserted, then addr must not be X.
    async def address_validity_requirement(self):
        while True:
            await RisingEdge(self.vif.clk)
            await ReadOnly()

            try: 
                if self.vif.wr.value == 1 or self.vif.rd.value == 1:
                    assert(self.vif.addr.value.is_resolvable,
                           f"When wr or rd is high addr was {self.vif.addr.value}")
            except AssertionError as msg:
                self.passed = False
                print(msg)

    #PR3 When wr is asserted, then wr_data must not be X
    async def write_data_validity_requirement(self):
        while True:
            await RisingEdge(self.vif.clk)
            await ReadOnly()

            try: 
                if (self.vif.wr.value == 1):
                    assert(self.vif.wr_data.value.is_resolvable,
                           f"When wr is high data was {self.vif.wr_data.value}")
            except AssertionError as msg:
                self.passed = False
                print(msg)

    #(PR4): when ack is asserted either wr or rd has to be high.
    async def ack_validity_requirement(self):
        while True:
            await RisingEdge(self.vif.clk)
            await ReadOnly()

            try: 
                if (self.vif.ack.value == 1):
                    assert(self.vif.wr.value == 1 or self.vif.rd.value == 1,
                    f"When ack is high wr was {self.vif.wr.value} and rd was {self.vif.rd.value}")
            except AssertionError as msg:
                self.passed = False
                print(msg)
    #(PR5): rd_data must be valid while ack is high during a read request (rd is high)
    async def read_data_validity_requirement(self):
        while True:
            await RisingEdge(self.vif.clk)
            await ReadOnly()

            try:
                if (self.vif.rd.value == 1 and self.vif.ack.value == 1):
                    assert(self.vif.rd_data.value.is_resolvable,
                        f"ack and rd is high and rd_data had the value {self.vif.rd_data.value}")
                
            except AssertionError as msg:
                self.passed = False
                print(msg)