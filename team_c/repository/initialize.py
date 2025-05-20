import time

from artiq.experiment import *
from common import Scope
from user import user_id


class Initialize(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("core_dma")

        self.setattr_device("ttl1")
        self.setattr_device("ttl3")
        self.setattr_device("urukul0_cpld")
        self.setattr_device("urukul0_ch0")
        self.urukul_channels = [
            self.urukul0_ch0
        ]
        self.setattr_device("fastino0")


    @kernel
    def init(self):
        self.core.reset()

        self.urukul0_cpld.init()
        for urukul_ch in self.urukul_channels:
            urukul_ch.init()
            urukul_ch.sw.off()
            urukul_ch.set_att(31.5)

        self.fastino0.init()
        delay(8*ns)
        self.fastino0.set_continuous(1)
        delay(8*ns)
        self.fastino0.set_dac(dac=0, voltage=0*V)

    @kernel
    def run_rt(self):
        self.init()

        # First setup Urukuls
        self.urukul0_ch0.set(frequency=1 * MHz)
        self.urukul0_ch0.set_att(5.0)
        self.urukul0_ch0.sw.on()

        delay(1 * ms)

        # Starting TTL sequence will trigger the scope
        self.ttl1.pulse(1 * us)
        self.ttl3.pulse(1 * us)
        # TODO: Add ttl5 input
        self.fastino0.set_dac(dac=0, voltage=0.5*V)
        delay(2 * us)
        self.fastino0.set_dac(dac=0, voltage=0*V)
        delay(1 * us)

    def run(self):        
        total_time = 0
        num_executions = 1

        for _ in range(num_executions):
            start_time = time.time()
            
            # Profile scope.setup()
            setup_start = time.time()
            setup_end = time.time()
            setup_time = setup_end - setup_start
            
            # Profile run_rt()
            run_rt_start = time.time()
            self.run_rt()
            run_rt_end = time.time()
            run_rt_time = run_rt_end - run_rt_start
            
            # Profile scope.store_waveform()
            store_start = time.time()
            store_end = time.time()
            store_time = store_end - store_start
            
            end_time = time.time()
            loop_time = end_time - start_time
            total_time += loop_time

            print(f"Execution {_ + 1}:")
            print(f"  scope.setup() time: {setup_time:.6f} seconds")
            print(f"  run_rt() time: {run_rt_time:.6f} seconds")
            print(f"  scope.store_waveform() time: {store_time:.6f} seconds")
            print(f"  Total loop time: {loop_time:.6f} seconds")

        average_time = total_time / num_executions
        print(f"Average execution time: {average_time:.6f} seconds")
