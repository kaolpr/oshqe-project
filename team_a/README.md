# Shaped RF pulse

This project enables the generation of shaped pulses with amplitude envelopes on the channels of the Urukul board (part of the Sinara/ARTIQ control system). The aim is to provide precise control over the amplitude envelope of pulses generated on Urukul channels. Users can load envelopes (rectangular, sine, traingular).

<pre lang="markdown"> ```python from envelopes import rectangular profile = rectangular(duration=5e-6, sample_rate=1e6) dds.write_ram(profile) ``` </pre>
## Objectives

- Use Urukul to generate shaped pulse (use on-chip RAM). Try to achieve pulses
  in us length range.
- Optionally initial phase should be given as a parameter.

## Deliverable

- Setup description with connections drawing (DrawIO?)
- Experiment with arguments:
  - shape (enumeration, predefined shape types)
  - pulse length (in us, scales shape)
  - (optionally) pulse initial phase
- Experiment should store shape envelope to dataset
- Describe your implementation in your team's README.md
