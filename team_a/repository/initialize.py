from artiq.experiment import *
import numpy as np

from artiq.coredevice.ad9910 import RAM_DEST_ASF, RAM_MODE_BIDIR_RAMP

import time

class Initialize(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("ttl0")
        self.urukul = self.get_device("urukul0_cpld")
        self.urukul_channels = [
            self.get_device(f"urukul0_ch0")
        ]
        self.setattr_argument(
            f"Shape", EnumerationValue(
                ["sin", "triangle", "square"],
                default="sin"
            )
        )
        self.setattr_argument(
            f"Steps", EnumerationValue(
                ["100", "200", "400", "500", "1000"],
                default="100"
            )
        )
        self.setattr_argument(
            f"Sample_length", EnumerationValue(
                ["10", "100", "200", "400", "500", "1000"],
                default="100"
            )
        )

    
    def prepare(self):
        samples = {"100": 100, "200": 200, "400":400, "500":500, "1000":1000}
        self.steps = samples[self.Steps]
        samples = {"10": 10, "100": 100, "200": 200, "400":400, "500":500, "1000":1000}
        self.sample_length = samples[self.Sample_length]

        amplitude_val = np.linspace(0, 1, self.sample_length//2)
        amplitude_val = np.append(amplitude_val, np.linspace(1, 0, self.sample_length//2))
        time = np.linspace(0, np.pi, self.sample_length)
        amplitude_val_sin = np.sin(time)
        asf_ram = np.arange(0, self.sample_length, dtype=np.int32)

        self.asf_ram = asf_ram.tolist()
        self.amplitude_val = amplitude_val.tolist()

        amplitude_val_sq = np.full(self.sample_length, 1.0)
        amplitude_val_sq[-1] = 0.0
        amplitude_val_sq[0] = 0.0
     
        self.amplitude_val_sq = amplitude_val_sq.tolist()
        self.amplitude_val_sin = amplitude_val_sin.tolist()

        samples = {"sin": self.amplitude_val_sin, "square": self.amplitude_val_sq, "triangle": self.amplitude_val}
        self.samples = samples[self.Shape]


    @kernel
    def run(self):  

        self.core.reset()
        self.core.break_realtime()

        self.urukul.init()
        delay(100*ms)

        self.urukul_channels[0].init()
        delay(1*ms)

        self.urukul_channels[0].cpld.init()
        delay(100*ms)

        self.urukul_channels[0].sw.on()
        self.urukul_channels[0].set_att(0.0)
        self.urukul_channels[0].set(frequency=25*MHz, phase=0.0, amplitude=1.0)
        # Wait for channel to be fully operational
        delay(10*ms)

       
        self.urukul_channels[0].set_profile_ram(0, 0+len(self.samples)-1, step=self.steps, profile = 0, mode=1)
   
        self.urukul_channels[0].cpld.set_profile(0)
        
        self.urukul_channels[0].amplitude_to_ram(self.samples, self.asf_ram)
        self.urukul_channels[0].write_ram(self.asf_ram)
        self.core.break_realtime()

        self.urukul_channels[0].set(frequency=50*MHz, phase=0.0, amplitude=1.0, ram_destination=RAM_DEST_ASF)

        self.urukul_channels[0].set_cfr1(ram_enable = 1, ram_destination = RAM_DEST_ASF)

        self.ttl0.pulse(100 * ns)
        delay(1 * us)
        self.urukul_channels[0].cpld.io_update.pulse_mu(10)

        self.set_dataset("envelope", np.full(len(self.samples), np.nan), persist=True)
        for i in range(len(self.samples)):
            self.mutate_dataset("envelope", i, self.samples[i])