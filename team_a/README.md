# Shaped RF pulse

This project enables the generation of shaped pulses with amplitude envelopes on the channels of the Urukul board (part of the Sinara/ARTIQ control system). The aim is to provide precise control over the amplitude envelope of pulses generated on Urukul channels. Users can load envelopes (rectangular, sine, traingular).

List of values of rectangular envelope:
```ruby
amplitude_val_sq = np.full(self.sample_length, 1.0)
amplitude_val_sq[-1] = 0.0
amplitude_val_sq[0] = 0.0 
```
List of values of sine envelope:
```ruby
time = np.linspace(0, np.pi, self.sample_length)
amplitude_val_sin = np.sin(time)
``` 
List of values of triangular envelope:
```ruby
amplitude_val = np.linspace(0, 1, self.sample_length//2)
amplitude_val = np.append(amplitude_val, np.linspace(1, 0, self.sample_length//2))
```
Values of envelope are used in setting RAM profile of Urukul channel. The step and length of an envelope can be changed as an argument
```ruby
self.urukul_channels[0].set_profile_ram(0, 0+len(self.samples)-1, step=self.steps, profile = 0, mode=1)
```
Sending pulse of an urukul channel, length of a pulse can be changed by either envelope length or step.
```ruby
self.ttl0.pulse(100 * ns)
delay(1 * us)
self.urukul_channels[0].cpld.io_update.pulse_mu(10)
```
Envelope is saved to dataset
```ruby
self.set_dataset("envelope", np.full(len(self.samples), np.nan), persist=True)
        for i in range(len(self.samples)):
            self.mutate_dataset("envelope", i, self.samples[i])
```
## Objectives

- Using on-chip RAM shaped Urukul pulses can be generated in us range. Pulse length can be changed by setting values of step and envelope length. Envelope is saved to dataset.

