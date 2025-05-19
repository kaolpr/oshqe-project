# Team B - Morse code loopback - measure top speed

## Objectives

- Use 2 DIO channels to implement Morse code communication. Determine maximum possible speed measured in symbols / second. Use International Morse Code.
- Optionally implement alternative method, better suited to the Sinara/ARTIQ processing capabilities and supporting the same symbols (but with different coding)

## Deliverable

- Setup description with connections drawing (DrawIO?)
- Experiment with arguments:
  - message length (number)
  - repetitions (number)
  - speed (number)
  - (optionally) communication mode (enumerate: Morse / your method)
- Experiment should store transmission statistics (error rate) in dataset
- Describe your implementation in your team's README.md
