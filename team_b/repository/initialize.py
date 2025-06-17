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

                              StringValue("Hello World!"),

                              tooltip="This is the message you want to send")



        self.setattr_argument("pulse_len_us",

                              NumberValue(2e-6, unit="us", precision=6),

                              tooltip="This is a number argument")

        

        self.setattr_argument("num_executions",

                           NumberValue(2, scale=1, step=1, precision=0, type="int"),

                           tooltip="This is the number of times you want to send the message")

        

        #self.num_executions = 10 # figure out how to int in dashboard

        

    def prepare(self):



        self.message += " "

        #self.num_executions = int(self.num_executions)



        #print(os.getcwd())

        #print(os.listdir("../../../.")) # figure out why path is incorrect



        with open("../../../morse_code.json", "r") as f: # reading json file as loading into self.morse_code

            self.morse_code = json.load(f)



        self.duration = self.encode_message()

        

        self.t0 = np.int64(0)

        self.timestamps = [np.int64(0) for _ in range(len(self.duration))]

        



    def encode_message(self):



        duration = []

        self.message = self.message.lower() # ensures all lowercase letters



        for char in self.message:

            if char in self.morse_code:

                code = self.morse_code[char]

                for signal in code:

                    if signal == ".":

                        duration.append(1)

                    elif signal == "-":

                        duration.append(3) 

                    duration.append(1)

                duration[-1] += 2 # intercharacter pause is 1+2=3 pulse lengths

            elif char == " ":

                duration.append(7) # "space" means a pause of 1+1+3=5 pulse lengths

                duration.append(3) # intercharacter pause



        return duration 



    def decode_message(self):



        time_values_us = []

        for tstmp in self.timestamps:

            if tstmp != -1: # if tstmp == -1, there was a timeout before an input event was received.

                t = self.core.mu_to_seconds(tstmp - self.t0)*self.pulse_len_us*1e6

                time_values_us.append(t)



        self.time_transmission_us = (time_values_us[-1]-time_values_us[0])

        signal_units = [round((time_values_us[i+1]-time_values_us[i])/self.pulse_len_us) for i in range(len(time_values_us)-1)] # getting back 1, 3 or 7

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



            if i%5==0:

                self.core.break_realtime()

            if i % 2 == 0:

                self.ttl1.pulse(self.duration[i]*us)

            else:

                delay(self.duration[i]*us) 



        # Finding rising and falling edge timestamps

        at_mu(self.t0)

        self.core.break_realtime()



        gate_end_mu = self.ttl5.gate_both(len(self.duration)*10*self.pulse_len_us) 

        

        i = 0

        

        while i < len(self.timestamps): # acquiring timestamps

            self.timestamps[i] = self.ttl5.timestamp_mu(gate_end_mu)

            i = i + 1



    def run(self): 



        self.set_dataset("error_rate", np.full(self.num_executions, np.nan), broadcast=True, persist=True) 

        self.set_dataset("speed_of_transmission", np.full(self.num_executions, np.nan), broadcast=True, persist=True)

         

        list_speed = []

        list_errors = []



        for i in range(self.num_executions):

             

            self.run_rt()

            decoded_message = self.decode_message()



            char_errors = []  # 0 = correct, 1 = incorrect

            for j in range(len(decoded_message)):

                if self.message[j] == decoded_message[j]:

                    char_errors.append(0)

                else:

                    char_errors.append(1)
            for j in range(len(self.message) - 1 - len(decoded_message) ):
                char_errors.append(1) # accounting for missing characters near end of message

    

            current_error_rate = sum(char_errors) / (len(self.message) -1)

            list_errors.append(current_error_rate)

            self.mutate_dataset("error_rate", i, current_error_rate)



            sps = (len(self.message) - 1) / self.time_transmission_us # symbols per second

            list_speed.append(sps)

            self.mutate_dataset("speed_of_transmission", i, sps)



            print(f"------Iteration #{i+1}------")

            print(f"Original message: {self.message}")

            print(f"Decoded message:  {decoded_message}")

            print(f"Speed of transmission: {sps} [symbols/s]; Error rate: {current_error_rate}\n")

    

        print(f"Worse error rate: {max(list_errors)}")

        print(f"Avg symbols per second achieved: {sum(list_speed)/len(list_speed):.2f} [symbols/s]")