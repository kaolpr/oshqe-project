
from artiq.experiment import *
import numpy
import csv
import os


class DrawXY(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.ttl = self.get_device("ttl1")  # As a trigger
        self.fastino = self.get_device("fastino0")
        self.file_path = '../../../repository/converted_arrays.csv'

    def prepare(self):
        amplitude = 1 * V
        samples_x = []
        samples_y = []
        print(os.getcwd())

        with open(self.file_path) as fp:  
            reader = csv.reader(fp)
            next(reader)
            for i, row in enumerate(reader):
                # Read one every N points, picoscope likes 1 in 80 because can't take too many points at 10 us div
                if i % 80 == 0:
                    samples_x.append(float(row[0]))
                    samples_y.append(float(row[1]))

        self.samples_x = numpy.array(samples_x)*amplitude
        self.samples_y = numpy.array(samples_y)*amplitude

    @kernel
    def run(self):
        # Reset system after previous experiment
        self.core.reset()
        self.fastino.init()

        # Set system time pointer in future
        self.core.break_realtime()

        # Trigger for the oscilloscope
        self.ttl.pulse(50*ns)

        at_mu(now_mu()-self.core.seconds_to_mu(1.2 * us))

        DELAY_ns = 392*ns*3

        self.fastino.set_dac(dac=0, voltage=self.samples_x[0])
        delay(DELAY_ns)
        self.fastino.set_dac(dac=1, voltage=self.samples_y[0])
        delay(DELAY_ns)

        sample_num = len(self.samples_x)
        assert (len(self.samples_x) == len(self.samples_y))
        for i in range(sample_num):
            sample_x = self.samples_x[i]
            sample_y = self.samples_y[i]

            self.fastino.set_dac(dac=0, voltage=sample_x)
            delay(DELAY_ns)
            self.fastino.set_dac(dac=1, voltage=sample_y)
            delay(DELAY_ns)
