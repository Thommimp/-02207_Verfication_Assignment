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

