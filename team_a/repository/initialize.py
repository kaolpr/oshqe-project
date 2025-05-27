from artiq.experiment import *
import numpy as np

from artiq.coredevice.ad9910 import RAM_DEST_ASF, RAM_MODE_BIDIR_RAMP



class Initialize(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("ttl0")
        self.urukul = self.get_device("urukul0_cpld")
        self.urukul_channels = [
            self.get_device(f"urukul0_ch0")
        ]
    
    def prepare(self):
        amplitude_val = np.linspace(1, 0, 10)
        time = np.linspace(0, np.pi, 10)
        amplitude_val_sin = np.sin(time)
        asf_ram = np.arange(0, 10, dtype=np.int32)

        self.asf_ram = asf_ram.tolist()
        self.amplitude_val = amplitude_val.tolist()
        self.amplitude_val_sq = [1.0, 1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0]
        self.amplitude_val_sin = amplitude_val_sin.tolist()


        # envelope=np.array([])
        # for i in range (100):
        #     envelope=np.append(envelope, np.exp(-i**2))


    @kernel
    def run(self):  
                # Reset our system after previous experiment
        self.core.reset()

        # Set software (now) counter in the future
        self.core.break_realtime()

        # Intialize Urukul and Urukul channels
        # Note that, although output is disabled, the frequency is set to 25 MHz
        # and DDS is running.
        
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

        # SOLUTION -------------------------------------------------------------       
        #self.ttl0.pulse(100 * ns)
        #self.urukul_channels[0].sw.pulse(400 * ns)


        
        self.urukul_channels[0].set_profile_ram(0, 0+len(self.amplitude_val_sin)-1, step=250, profile = 0, mode=1)
        #self.urukul_channels[0].cpld.io_update.pulse_mu(8)
        self.urukul_channels[0].cpld.set_profile(0)
        
        self.urukul_channels[0].amplitude_to_ram(self.amplitude_val_sin, self.asf_ram)
        self.urukul_channels[0].write_ram(self.asf_ram)
        self.core.break_realtime()

        self.urukul_channels[0].set(frequency=25*MHz, phase=0.0, amplitude=1.0, ram_destination=RAM_DEST_ASF)

        self.urukul_channels[0].set_cfr1(ram_enable = 1, ram_destination = RAM_DEST_ASF)

        self.ttl0.pulse(100 * ns)
        delay(1 * us)
        self.urukul_channels[0].cpld.io_update.pulse_mu(10)
     
        
        #self.urukul_channels[0].sw.pulse(400 * ns)

        # self.core.break_realtime()

        # self.urukul.set_profile(0)
        # delay(100 * us)
