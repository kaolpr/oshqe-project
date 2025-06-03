import time
import json
import os
import numpy as np

from artiq.experiment import *


class Initialize(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("core_dma")

        self.setattr_device("ttl1")
        self.setattr_device("ttl5")
        
        self.setattr_argument("message",
                              StringValue("ABC123"),
                              tooltip="This is the message you want to send")

        self.setattr_argument("pulse_len_us",
                              NumberValue(2e-6, unit="us", precision=4),tooltip="This is a number argument")
        
        #self.setattr_argument("num_executions",
        #                   NumberValue(2, type='int', scale=1, precision=0), tooltip="Number of times you want to send the message")
        
        self.num_executions = 2 #figure out how to int in dashboard
        self.symbol_count=0
        
    def prepare(self):

        #self.message = "ABC" 
        #self.num_executions = 1 #number of repetitions
        #self.pulse_len_us = 2 #pulse length in us

        print(os.getcwd())
        print(os.listdir("../../../.")) #figure out why path is incorrect

        with open("../../../morse_code.json", "r") as f: #reading json file as loading into self.morse_code
            self.morse_code = json.load(f)

        self.duration = self.encode_message()
        
        self.t0 = np.int64(0)
        self.timestamps = [np.int64(0) for _ in range(len(self.duration))]
        

    def encode_message(self):

        duration = []
        self.message = self.message.lower() #ensures all lowercase letters, like in the morse code json file
        self.message += " "
        for char in self.message:

            if char in self.morse_code:

                code = self.morse_code[char]

                for signal in code:

                    if signal == ".":
                        duration.append(1)
                    elif signal == "-":
                        duration.append(3) 
                    
                    duration.append(1)

                duration[-1] += 2 #intracharacter pause is 1+1=2 pulse lengths

            elif char == " ":

                duration.append(7) #"space" means a pause of 1+1+3=5 pulse lengths
                duration.append(3) #intercharacter pause

        return duration 

    def decode_message(self):

        time_values_us = []
        for tstmp in self.timestamps:
            if tstmp != -1: # if tstmp == -1, there was a timeout before an input event was received.
                t = self.core.mu_to_seconds(tstmp - self.t0)*self.pulse_len_us*1e6
                time_values_us.append(t)

        print("timestamp-t0 [us]: ", " ".join([f"{tstmp:.2f}" for tstmp in time_values_us]))

        signal_units = [round((time_values_us[i+1]-time_values_us[i])/self.pulse_len_us) for i in range(len(time_values_us)-1)] 
        print(f"sigmnalunits={signal_units}")
        symbols = ''
        decoded_message= ''
        for i, unit in enumerate(signal_units):
            if i%2==0:
                if unit == 1:
                    symbols += '.'
                elif unit == 3:
                    symbols += '-'
                elif unit == 7:
                    decoded_message += ' '
                    #symbols = ''
            else:
                if unit == 1:
                    pass
                elif unit == 3:
                    decoded_message += next((key for key, value in self.morse_code.items() if symbols == value), '')
                    symbols = ''
                

        return decoded_message


    @kernel
    def run_rt(self):
        self.core.reset()

        self.ttl1.output()
        self.ttl5.input()

        delay(1* ms)

        self.t0 = now_mu()

        # Sending encoded message
        for i in range(len(self.duration)):
            if i % 2 == 0:
                self.ttl1.pulse(self.duration[i]*us)
            else:
                delay(self.duration[i]*us) 


        # Finding rising and falling edge timestamps
        at_mu(self.t0)

        gate_end_mu = self.ttl5.gate_both(len(self.duration)*5*self.pulse_len_us) #maximum duration assuming all characters are spaces - 5 pulse lens?
        
        i = 0
        
        while i < len(self.timestamps):
            self.timestamps[i] = self.ttl5.timestamp_mu(gate_end_mu)
            i = i + 1

    def run(self): 
        #print(len(self.message))

        self.set_dataset("error_rate", np.full(self.num_executions, np.nan), broadcast=True, persist=True) 
        self.set_dataset("speed_of_transmission", np.full(self.num_executions, np.nan), broadcast=True, persist=True)
         
        total_time = 0

        list_speed = []

        for i in range(self.num_executions):
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

            decoded_message = self.decode_message()

            char_errors = []  # 0 = correct, 1 = incorrect
            for j in range(len(decoded_message)):
                if self.message[j]== decoded_message[j]:
                    char_errors.append(0)
                else:
                    char_errors.append(1)
    
            current_error_rate = sum(char_errors) / (len(decoded_message) + 1)

            
            self.set_dataset("error_rate", np.full(self.num_executions, np.nan), broadcast = True)
            for k in range(self.num_executions):
                self.mutate_dataset("error_rate", k, current_error_rate)
                time.sleep(0.5)


            if run_rt_time > 0:
                sps = self.symbol_count / run_rt_time
            else:
                sps = 0
            #self.set_dataset(f"symbols_per_second[{i}]", i, sps)  

            #list_speed.append(sps)  # <-- dodajemy wynik do listy
            #self.set_dataset(f"symbols_per_second[{i}]", sps)

            print(f"Execution {i + 1}:")
            print(f"  scope.setup() time: {setup_time:.6f} seconds")
            print(f"  run_rt() time: {run_rt_time:.6f} seconds")
            print(f"  scope.store_waveform() time: {store_time:.6f} seconds")
            print(f"  Total loop time: {loop_time:.6f} seconds")

    
        average_time = total_time / self.num_executions
        print(f"Average execution time: {average_time:.6f} seconds")
        print(self.duration)

        print(f"Original message: {self.message}")
        print(f"Decoded message:  {decoded_message}")

        print(current_error_rate)
              
        #max_sps = max(list_speed) if list_speed else 0
        #print(f"Maximum symbols per second achieved: {max_sps:.2f}")

        