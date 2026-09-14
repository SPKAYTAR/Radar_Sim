import numpy as np
import matplotlib.pyplot as plt
import math

from radar import FMCW_Radar
from target import targets
from Simulate import simulate_chirp
from process import fourier_transform, get_sorted_peaks, find_target, successive_interference_cancelation


radar = FMCW_Radar(
    frequency=77e9,
    bandwidth=2e9,
    chirp_time=1e-3,
    sample_rate=2000000
)
radar.limits()
data1 = simulate_chirp(radar, targets, 1)

decoded1 = fourier_transform(data1, radar)

radar.chirp_slope *= -1
data2 = simulate_chirp(radar, targets, 1)

decoded2 = fourier_transform(data2, radar)
radar.chirp_slope *= -1
peaks1 = get_sorted_peaks(decoded1)
peaks2 = get_sorted_peaks(decoded2)

target_values = find_target(peaks1,peaks2,radar)
frequencys = decoded1[:,0]
amplitudes = decoded1[:,1]
plt.title("Original")
plt.plot(frequencys,amplitudes)
frequencys = decoded2[:,0]
amplitudes = decoded2[:,1]
plt.plot(frequencys,amplitudes)
plt.show(block=False)
plt.pause(0.1)

successive_interference_cancelation(decoded1,decoded2,radar)
for x in targets:
    print(x)
plt.show()

