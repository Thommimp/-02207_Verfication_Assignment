import vsc

from cl_marb_common import MarbMode

@vsc.covergroup
class covergroup_register:
    def __init__(self, name):
        self.options.name = name
        self.options.per_instance = True

        self.with_sample(
            enable=vsc.bit_t(1),
            mode=vsc.bit_t(2), # 2nd bit is reserved but unused
            prio0=vsc.bit_t(8),
            prio1=vsc.bit_t(8),
            prio2=vsc.bit_t(8),
        )

        self.cp_enable = vsc.coverpoint(self.enable, bins={
            "disabled": vsc.bin(0),
            "enabled": vsc.bin(1),
        })

        # Sample only when enabled
        self.cp_mode = vsc.coverpoint(self.mode, iff=lambda: int(self.enable) == 1, bins={
                "static": vsc.bin(0),
                "dynamic": vsc.bin(1),
        })

        def dynamic_mode():
            return int(self.enable) == 1 and int(self.mode) == MarbMode.DYNAMIC

        priority_bins = {
            "zero": vsc.bin(0),
            "low": vsc.bin([1, 127]),
            "high": vsc.bin([128, 254]),
            "max": vsc.bin(255),
        }

        self.cp_prio0 = vsc.coverpoint(
            self.prio0,
            iff=dynamic_mode,
            bins=priority_bins,
        )
        self.cp_prio1 = vsc.coverpoint(
            self.prio1,
            iff=dynamic_mode,
            bins=priority_bins,
        )
        self.cp_prio2 = vsc.coverpoint(
            self.prio2,
            iff=dynamic_mode,
            bins=priority_bins,
        )

        self.cross_enable_mode = vsc.cross(
            [self.cp_enable, self.cp_mode],
        )
