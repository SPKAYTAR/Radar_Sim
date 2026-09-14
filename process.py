import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import cmath
from Simulate import simulate_chirp

# def DFT(arr,radar):
#      #increments of .5
#      data = np.array(arr, dtype=complex).copy()
#      decode = []
#      for f in np.arange(-radar.sample_rate/2, radar.sample_rate/2, 0.5):
#          total = 0j
#          for time, amplitude in data:
#              total += amplitude * np.exp(-1j * 2*np.pi*f*time)

#          COM = total / len(data)
#          magnitude = np.abs(COM)
#          phase = np.angle(COM)
#          decode.append((f, magnitude, phase))

#      decode = np.array(decode)

#      return decode

     
def fourier_transform(arr, radar):

    data = np.array(arr, dtype=complex).copy()

    amplitudes = data[:, 1]

    frequency_step = 0.5
    n_fft = int(radar.sample_rate / frequency_step)

    total = np.fft.fft(amplitudes, n=n_fft)

    COM = total / len(data)

    # Shift the COMPLEX FFT first
    COM = np.fft.fftshift(COM)

    magnitude = np.abs(COM)
    phase = np.angle(COM)

    frequencies = np.arange(
        -radar.sample_rate / 2,
        radar.sample_rate / 2,
        frequency_step
    )

    decode = np.column_stack(
        (frequencies, magnitude, phase)
    )

    return decode


def get_sorted_peaks(arr):  #returns top down sorted peaks to amplitudes
    peaks,properties = find_peaks(arr[:,1], prominence=0.00005)

    frequencys = arr[peaks, 0]
    magnitudes = arr[peaks,1]
    

    return sorted(zip(frequencys,magnitudes), key=lambda x: x[1], reverse=True)

def find_target(arr1,arr2,radar): #arr1, peak information of chirp 1; arr2, peak information of chirp 2
    target_values = []
    S = radar.chirp_slope
    fc = radar.frequency
    T = radar.chirp_time
    for (f1, m1), (f2, m2) in zip(arr1,arr2):
        #print("f1:", f1, "f2:", f2)
        f1 *= 3e8 /2
        f2 *= 3e8/2
        A = np.array([
            [ S, fc + S*T],
            [-S, fc - S*T]
        ])
        b = np.array([f1, f2])

        R, v = np.linalg.solve(A, b)
        R = float(R)
        v = float(v)
        target_values.append((R, v,float(m1),float(m2)))

    return target_values


def half_hann_window(arr, radar):
    data = np.array(arr, dtype=complex).copy()
    fade_samples = radar.samples_size // 5
    n = np.arange(fade_samples)

    window = 0.5 * (1 + np.cos(np.pi * n / (fade_samples - 1)))

    data[-fade_samples:, 1] *= window

    return data


def successive_interference_cancelation(arr1, arr2, radar): #arrays are decoded, raw f,amplitude unsorted

    a1 = np.array(arr1).copy()
    a2 = np.array(arr2).copy()

    num = 1

    while True:

        peaks1 = get_sorted_peaks(a1)
        peaks2 = get_sorted_peaks(a2)

        if len(peaks1) == 0 or len(peaks2) == 0:
            break
        #Minimum wave amplitude to continue
        if peaks1[0][1] < 0.00001:
            break

        # Targeted beat
        beat1 = peaks1[0][0]
        beat2 = peaks2[0][0]

        # Decode target
        target_values = find_target(peaks1,peaks2,radar)

        if len(target_values) == 0:
            break

        d1, v1, m1, m2 = target_values[0]

        # Test for spectral loss
        test_target = [(d1, v1, 1.0)]

  # Chirp 1 reference magnitude
        simulated_ref1 = simulate_chirp(radar, test_target, 1)
        reference1 = fourier_transform(simulated_ref1, radar)
        ref_mag1 = get_sorted_peaks(reference1)[0][1]

        # Chirp 2 reference magnitude
        radar.chirp_slope *= -1
        simulated_ref2 = simulate_chirp(radar, test_target, 1)
        reference2 = fourier_transform(simulated_ref2, radar)
        ref_mag2 = get_sorted_peaks(reference2)[0][1]
        radar.chirp_slope *= -1

        # Convert each measured magnitude to RCS
        rcs1 = (m1 / ref_mag1) ** 2
        rcs2 = (m2 / ref_mag2) ** 2

       # Average the two power/RCS estimates
        rcs = (rcs1 + rcs2) / 2

        print("Corrected Target ", num, ":", d1, v1, rcs)
        #Corrected Target
        target_estimate = [(d1, v1, rcs)]
        # Cancel +S chirp
        simulated1 = simulate_chirp(radar,target_estimate,1)
        cancel1 = fourier_transform(simulated1,radar)
        a1[:, 1] = np.maximum(a1[:, 1] - cancel1[:, 1],0)

        # Cancel -S chirp
        radar.chirp_slope *= -1
        simulated2 = simulate_chirp(radar,target_estimate,1)
        cancel2 = fourier_transform(simulated2,radar)
        a2[:, 1] = np.maximum(a2[:, 1] - cancel2[:, 1],0)
        radar.chirp_slope *= -1

        # Plot remaining spectrum
        plt.figure()
        plt.title(f"Sequence {num}")
        plt.plot(a1[:, 0],a1[:, 1])
        plt.plot(a2[:, 0],a2[:, 1])
        plt.show(block=False)
        plt.pause(0.1)
        num += 1

    #return a1, a2 
        
def magnitude_to_rcs(measured_mag, radar, target_estimate):
    sim = simulate_chirp(radar, target_estimate, 1)
    reference = fourier_transform(sim, radar)
    reference_mag = get_sorted_peaks(reference)[0][1]

    reference_rcs = target_estimate[0][2]
    rcs = reference_rcs * (measured_mag / reference_mag) ** 2

    return rcs

# def winding_error(frequency, radar, target_estimate):   Does not work due to low beat frequencys not getting to a full cycle
#     frequency = abs(frequency)

#     num_cycles = frequency * radar.chirp_time
#     cutoff_cycles = num_cycles % 1
#     sample_cutoff = cutoff_cycles * radar.sample_rate / frequency
#     cutoff = int(round(radar.samples_size - sample_cutoff))

#     sim = simulate_chirp(radar, target_estimate, 1)

#     imperfect = fourier_transform(sim, radar)
#     perfect = fourier_transform(sim[:cutoff], radar)

#     bad_mag = get_sorted_peaks(imperfect)[0][1]
#     good_mag = get_sorted_peaks(perfect)[0][1]

#     rcs_gain = (good_mag / bad_mag) ** 2

#     return rcs_gain

    

