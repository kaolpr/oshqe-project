from artiq.experiment import *


class Initialize(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("ttl0")
        self.urukul = self.get_device("urukul0_cpld")
        self.urukul_channels = [
            self.get_device(f"urukul0_ch0")
        ]
    
    def prepare(self):
        envelope=np.array([])
        for i in range (100):
            envelope=np.append(envelope, np.exp(-i**2))


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
        self.urukul_channels[0].sw.off()
        self.urukul_channels[0].set_att(0.0)
        self.urukul_channels[0].set(frequency=25*MHz, phase=0.0, amplitude=1.0)
        # Wait for channel to be fully operational
        delay(10*ms)

        # SOLUTION -------------------------------------------------------------       
        self.ttl0.pulse(100 * ns)
        self.urukul_channels[0].sw.pulse(400 * ns)
        
        # self.urukul_channels[0].set_profile_ram(0, 100)
        # self.core.break_realtime()

        # self.urukul.set_profile(0)
        # delay(100 * us)
