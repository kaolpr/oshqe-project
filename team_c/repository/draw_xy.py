from artiq.experiment import *
# from common import Scope
import numpy as np

class DrawXY(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.ttl = self.get_device("ttl1") # trigger

        self.fastino = self.get_device("fastino0")

        self.setattr_argument(
            f"Scope_horizontal_scale", EnumerationValue(
                ["1 us", "2 us", "4 us", "10 us", "20 us", "40 us", "100 us", "200 us", "400 us"],
                default="10 us"
            )
        )

        self.setattr_argument(
            f"Delay_multiplier", NumberValue(
                default = 8,
                precision = 0,
                unit = "",
                type = "int",
                step = 1,
                min = 1,
                max = 256,
                scale=1
            ),
            tooltip="Samples are send every 392 ns times this multiplier."
        )


    def prepare(self):
        # Use these parameters
        self.Amplitude = 2 * V
        self.sample_num = 200

        t = np.linspace(0,2*np.pi, self.sample_num)
        self.circle_x = np.sin(t)
        self.circle_y = np.cos(t)

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()
        t0=now_mu()
        # while True:
        #     self.ttl.pulse(1*ms)
        #     delay(1*ms)
        self.ttl.pulse(50*ns)
        # at_mu(t0-self.core.seconds_to_mu(1.2*us)) 
        at_mu(now_mu()-self.core.seconds_to_mu(1.6*us)) 
        try:
            for i in range(len(self.circle_x)):
                sample_x = self.circle_x[i]
                sample_y = self.circle_y[i]
                self.fastino.set_dac(dac=0, voltage=sample_x*V)
                self.fastino.set_dac(dac=1, voltage=sample_y*V)
                delay(392 * ns)
                # delay(392 * self.Delay_multiplier * ns)

#---------------------------------------------------------------------

        except RTIOUnderflow:
            print("Rtio underflow, cleaning up")
            self.core.break_realtime()
