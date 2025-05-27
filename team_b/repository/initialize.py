import time
import json
import os

from artiq.experiment import *


class Initialize(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("core_dma")

        self.setattr_device("ttl1")
        self.setattr_device("ttl5")
        

    def prepare(self):
        #wartosci tutaj narazie sa na sztywno ustawione, moze daloby sie pozniej uwzglednic w dashboard zeby uzytkownik mogl zmienic te parametry?

        self.message = "ABC" 
        self.num_executions = 1 #number of repetitions
        self.pulse_len_us = 2 #pulse length in us

        print(os.getcwd())
        print(os.listdir("../../../.")) #figure out why path is incorrect

        with open("../../../morse_code.json", "r") as f: #reading json file as loading into self.morse_code
            self.morse_code = json.load(f)

        self.amplitude, self.duration = self.encode_message()

    def encode_message(self):

        amplitude = []
        duration = []
        self.message = self.message.lower() #ensures all lowercase letters, like in the morse code json file

        for char in self.message:

            if char in self.morse_code:

                code = self.morse_code[char]

                for signal in code:

                    amplitude.append(0.5)

                    if signal == ".":
                        duration.append(1)
                    elif signal == "-":
                        duration.append(3) 
                    
                    amplitude.append(0) #pause between each signal
                    duration.append(1)

                duration[-1] += 1 #pause between the end of one character?

            elif char == " ":

                amplitude.append(0)
                duration.append(5) #"space" means a pause of 4 pulse lenghts?

        return amplitude, duration 

    #def decode_message(self):
    #tutaj moze finding rising and falling of signals, then converting those times back into message?

    '''
    def decode_message(self):
        self.core.break_realtime()

        self.ttl5.input()
        delay(10 * ms)

        timestamps = [0] * 100
        count = 0

        self.ttl5.gate_rising(1 * s)

        while count < 100:
            ts = self.ttl5.fetch_timestamp()
            if ts == -1:
                break
        timestamps[count] = ts
        count += 1

        if count < 2:
            print("No signal")
            return

        decoded_symbols = []
        for i in range(1, count):
            delta_mu = timestamps[i] - timestamps[i - 1]
            delta_us = self.core.mu_to_seconds(delta_mu) * 1e6

            units = round(delta_us / self.pulse_len_us)

            if units == 1:
                decoded_symbols.append(".")
            elif units == 3:
                decoded_symbols.append("-")
            elif units >= 5:
                decoded_symbols.append(" ")
            else:
                decoded_symbols.append("?")

        morse_string = "".join(decoded_symbols)
        print("Morse text", morse_string)

        morse_reverse = {v: k for k, v in self.morse_code.items()}

        messages = morse_string.split(" ")
        decoded_text = ""
        for l in messages:
            if l in morse_reverse:
                decoded_text += morse_reverse[l]
            else:
                decoded_text += "?"

        print("Decoded message", decoded_text)
    '''
        


    @kernel
    def run_rt(self):
        self.core.reset()

        self.ttl1.output()
        self.ttl5.input()

        # First setup Urukuls
        #self.urukul0_ch0.set(frequency=1 * MHz)
        #self.urukul0_ch0.set_att(5.0)
        #self.urukul0_ch0.sw.on()

        delay(1* ms)


        # Starting TTL sequence will trigger the scope

        ''''while True:
            delay(2*us)
            self.ttl1.on()
            delay(10*us)
            self.ttl1.off()
            delay(2*us)'''

        for i in range(len(self.duration)):
            if i % 2 == 0:
                self.ttl1.pulse(self.duration[i]*us)
            else:
                delay(self.duration[i]*us)
            
        
     
        
        #amplitude = self.encode_message()

        '''for i in range(len(duration)):
            self.fastino0.set_dac(dac=0, voltage=amplitude[i]*V) #czy zadziala amplitude[i]*V?
            delay(duration[i] * self.pulse_len_us * us)'''

    def run(self): 
        #print(len(self.message))

        #self.set_dataset("error_rate", np.full(len(self.message), np.nan), broadcast=True, persist=True)       
        total_time = 0

        for _ in range(self.num_executions):
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

            #gdzies moze tutaj dodac decode_message, after full message has been sent and decoded?

            #changing error_rate dataset here too, it will character by character check if it is good or bad, 0 or 1 maybe? and then normalize by number of characters checked up to that moment to have a in real time updated error rate?

            print(f"Execution {_ + 1}:")
            print(f"  scope.setup() time: {setup_time:.6f} seconds")
            print(f"  run_rt() time: {run_rt_time:.6f} seconds")
            print(f"  scope.store_waveform() time: {store_time:.6f} seconds")
            print(f"  Total loop time: {loop_time:.6f} seconds")

        average_time = total_time / self.num_executions
        print(f"Average execution time: {average_time:.6f} seconds")

        print(self.duration)
        print(self.amplitude)