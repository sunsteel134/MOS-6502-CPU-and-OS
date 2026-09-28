class clock:
    def __init__(self, hz=1000000):
        self.frequency = hz
        self.cycle_count = 0
        self.total_cycles = 0

    def tick(self, cycles=1): #do a CPU cycle
        self.cycle_count += cycles
        self.total_cycles += cycles

    def get_time_us(self): #find how many cycles have been done
        return (self.total_cycles * 1000000) // self.frequency

    def reset(self): #reset (obviously)
        self.cycle_count = 0
        self.total_cycles = 0

    def get_frequency_mhz(self): #gets frequency in megaHz
        return self.frequency / 1000000.0
