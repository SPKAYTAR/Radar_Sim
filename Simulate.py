import numpy as np
import matplotlib.pyplot as plt
import math

def simulate(radar, targets, num_chirps: int):
    time = 0.0
    data = []
   
    for sample_index in range(radar.samples_size):
        amplitude = 0
        for distance, velocity, rcs in targets:

            current_distance = distance + velocity * time
            incoming_frequency = radar.frequency + radar.chirp_slope * time
            delay = 2 * current_distance / 3e8
            if time >= delay:
                doppler_shift = 2 * velocity * incoming_frequency / c
                return_frequency = incoming_frequency + doppler_shift
                current_amplitude = math.sqrt(rcs) / (current_distance ** 2)
                phase_shift = 2*math.pi*delay*return_frequency
                amplitude += current_amplitude * math.cos(2*math.pi * return_frequency * time - phase_shift)
        time += 1/radar.sample_rate
        
        data.append({time: amplitude})
        