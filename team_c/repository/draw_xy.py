
from artiq.experiment import *
import numpy
import csv
import os

class DrawXY(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.ttl = self.get_device("ttl1") # As a trigger
        self.fastino = self.get_device("fastino0")

        sample_num = 48
        phase= numpy.pi/12
        
        # self.samples_x=[Amplitude * numpy.sin(2*numpy.pi*i / sample_num * 2 - phase) for i in range(sample_num)]
        # self.samples_y=[Amplitude * numpy.cos(2*numpy.pi*i / sample_num * 2) for i in range(sample_num)]

    def prepare(self):
        amplitude = 1* V
        samples_x = []
        samples_y = []
        print(os.getcwd())

        with open('../../../repository/converted_arrays.csv') as fp: #../../../repository/
            reader=csv.reader(fp)
            next(reader)
            for i, row in enumerate(reader):
                if i % 1000 ==0:
                    samples_x.append(float(row[0]))
                    samples_y.append(float(row[1]))
        
        self.samples_x = numpy.array(samples_x)*amplitude
        self.samples_y = numpy.array(samples_y)*amplitude


    @kernel
    def run(self):
        # Reset our system after previous experiment
        self.core.reset()
        self.fastino.init()

        # Set SYSTEM time pointer in future
        self.core.break_realtime()

        # Trigger for the oscilloscope
        
        self.ttl.pulse(50*ns)
        # Rewind timeline - Fastino takes around 1.2 us to output a sample
        at_mu(now_mu()-self.core.seconds_to_mu(1.2 * us)) 

        # Calculate and output a sine waveform using numpy.sin

        # Use these parameters
        self.fastino.set_dac(dac=0, voltage=self.samples_x[0])
        delay(392*ns * 1)
        self.fastino.set_dac(dac=1, voltage=self.samples_y[0])
        delay(392*ns * 1)

        # try:
        sample_num = len(self.samples_x)
        assert(len(self.samples_x) == len(self.samples_y))
        for i in range(sample_num):
            sample_x = self.samples_x[i]
            sample_y = self.samples_y[i]
            
            self.fastino.set_dac(dac=0, voltage=sample_x)
            delay(392*ns * 2)
            self.fastino.set_dac(dac=1, voltage=sample_y)
            delay(392*ns * 2)
            # Try to change the multiplier; leave 392*ns unchanged
            # (or don't and see what happens, it may be subtle :) )
                

# ---------------------------------------------------------------------

        # except RTIOUnderflow:
        #     # Catch RTIO Underflow to leave system in known state
        #     print("Rtio underflow, cleaning up")
        #     self.core.break_realtime()

        # finally:
        #     # Clean up even if RTIO Underflow happens
        #     delay(40*us)
        #     self.fastino.set_dac(dac=0, voltage=0.0*V)
        #     delay(392*ns*1)
        #     self.fastino.set_dac(dac=1, voltage=0.0*V)


