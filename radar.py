class FMCW_Radar:
    def __init__(self, frequency, bandwidth, chirp_time, sample_rate):
        self.frequency = frequency
        self.bandwidth = bandwidth
        self.chirp_time = chirp_time
        self.sample_rate = sample_rate
        self.chirp_slope = bandwidth / chirp_time
        self.samples_size = int(sample_rate * chirp_time)

    def limits(self):
        print("Max Range: ", 3e8 * self.sample_rate / (4*self.chirp_slope) )
        print("Max Chirp Range: ", self.chirp_time *3e8 / 2)
        print("Max Frequency Resolution", 1/self.chirp_time)
        print("Max Space Resolution", 3e8 * (1/self.chirp_time)/ (2*self.chirp_slope))
    


#class Pulse_Radar(self,frequency,pulse_width,PRF):