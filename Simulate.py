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
            
            
            
            if time >= delay:
                transmit_time = time - delay
                incoming_phase = 2 * math.pi * (radar.frequency * transmit_time + 0.5 * radar.chirp_slope * transmit_time**2) #reflected phase at t
                outgoing_phase = 2 * math.pi * (radar.frequency * time + .5 * radar.chirp_slope * time**2)
                current_amplitude = math.sqrt(rcs) / current_distance**2
                beat_amplitude = 0.5 * current_amplitude * np.exp(1j * (outgoing_phase - incoming_phase))  #generate filtered waveform
                #noise = np.random.uniform(-0.00001, 0.00001)
                amplitude += beat_amplitude #+ noise
                
        time += dt
        
        data.append((time , amplitude,))
    
    return data
