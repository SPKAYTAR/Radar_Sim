class FMCW_Radar:
    def __init__(self, frequency, bandwidth, chirp_time, sample_rate):
        self.frequency = frequency
        self.bandwidth = bandwidth
        self.chirp_time = chirp_time
        self.sample_rate = sample_rate
        self.chirp_slope = bandwidth / chirp_time
        self.samples_size = int(sample_rate * chirp_time)
    


#class Pulse_Radar(self,frequency,pulse_width,PRF):