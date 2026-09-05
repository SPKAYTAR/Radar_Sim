import numpy as np
import matplotlib.pyplot as plt
import math

def simulate_chirp(radar, targets, num_chirps: int):
    time = 0.0
    data = []
   
    for sample_index in range(radar.samples_size):
        amplitude = 0
        for distance, velocity, rcs in targets:

            current_distance = distance + velocity * time
            dt = 1 / radar.sample_rate
            delay = 2 * current_distance / 3e8
            transmit_time = time - delay
            
            if time >= delay:
                incoming_frequency_start = radar.frequency + radar.chirp_slope * transmit_time
                incoming_frequency_end = radar.frequency + radar.chirp_slope * (transmit_time + dt)
                incoming_frequency = (incoming_frequency_start + incoming_frequency_end) / 2
                doppler_shift = 2 * velocity * incoming_frequency / c
                return_frequency = incoming_frequency + doppler_shift   #Simulated return frequency collected based on incoming frequency sent at time - delay
                current_amplitude = math.sqrt(rcs) / (current_distance ** 2)
                phase_shift = 2*math.pi*delay*return_frequency
                amplitude += current_amplitude * math.cos(2*math.pi * return_frequency * time - phase_shift)
        time += dt
        
        data.append({time: amplitude})
    
    return data
        