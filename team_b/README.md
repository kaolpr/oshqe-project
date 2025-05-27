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


## Ideas
- The user will be able to choose the message, number of repetitions and mode from the dashboard (parametrization for user)
- Attribute morse_code holds characters and their representations in morse code 
- encode_message() function goes character by character, checks if there is a corresponding encoding via morse_code
    - amplitude list holds values for high and low state of voltage
    - duration list holds the length of each signal and pause between signals
        - dot: 1 unit
        - dash: 3 units
        - space: 5 units
        - pause between chars: 2 units 
- run_rt() uses amplitude and duration to send the appropriate encoded signals
- decode_message() function (ttl5 input) will search for the rises and falls of the signal in parallel with encode_message, and after the full message is transmitted it will use morse_code to decode the whole message 
- Maybe a seperate function for finding the times and seperate decode_message function that is run after that? so two functions?
- Testing of maximum speed of transmission -> find the max value
- "error_rate dataset" compares the initial message and output decoded message character by character and holds the current error rate of transmission
- Implementation of alternative code comunication

