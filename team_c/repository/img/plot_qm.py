import matplotlib.pyplot as plt
import csv
import numpy

class PlotQM:
    def __init__(self, amplitude=1.0):
        self.amplitude = amplitude
        self.samples_x = None
        self.samples_y = None
        self.file = 'converted_arrays.csv'
        self.load_samples(amplitude)
        # self.plot()

    def plot(self):
        if self.samples_x is None or self.samples_y is None:
            raise ValueError("Samples not loaded. Call load_samples() first.")
        
        plt.plot(self.samples_x, self.samples_y, 'o')
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.title('QM Plot')
        plt.grid(True)
        # plt.show()
        plt.savefig('qm_plot.png', dpi=300, bbox_inches='tight')
    def load_samples(self, amplitude=1.0):
        """
        Load samples from a CSV file and scale them by the given amplitude.
        """
        self.amplitude = amplitude

        with open(self.file, 'r') as fp:
            reader = csv.reader(fp)
            next(reader)
            for i, row in enumerate(reader):
                if i % 1 == 0:
                    if self.samples_x is None:
                        self.samples_x = []
                        self.samples_y = []
                    self.samples_x.append(float(row[0]))
                    self.samples_y.append(float(row[1]))
        self.samples_x = numpy.array(self.samples_x) * amplitude
        self.samples_y = numpy.array(self.samples_y) * amplitude

if __name__ == "__main__":
    import sys
    # check where are you
    print("Current working directory:", sys.path[0])
    if len(sys.argv) > 1:
        amplitude = float(sys.argv[1])
    else:
        amplitude = 1.0
    plot = PlotQM(amplitude)
    plot.plot()
