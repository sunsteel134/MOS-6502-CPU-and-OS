class timer:
    def __init__(self, base_address=0x0310, clock_hz=1000000):
        self.base_address = base_address
        self.clock_hz = clock_hz
        self.counter = 0xFFFF
        self.reload_value = 0xFFFF
        self.enabled = False
        self.interrupt_enabled = False
        self.counter_running = False
        self.timeout_flag = False
        self.tick_count = 0

    def contains(self, address):
        return self.base_address <= address < self.base_address + 8

    def read(self, address):
        offset = address - self.base_address
        if offset == 0:
            return self.counter & 0xFF
        elif offset == 1:
            return (self.counter >> 8) & 0xFF
        elif offset == 2:
            return self.reload_value & 0xFF
        elif offset == 3:
            return (self.reload_value >> 8) & 0xFF
        elif offset == 4:
            control = 0x00
            if self.enabled:
                control |= 0x01
            if self.interrupt_enabled:
                control |= 0x02
            if self.counter_running:
                control |= 0x04
            return control
        elif offset == 5:
            status = 0x00
            if self.timeout_flag:
                status |= 0x01
            return status
        return 0x00

    def write(self, address, value):
        offset = address - self.base_address
        if offset == 0:
            self.counter = (self.counter & 0xFF00) | value
        elif offset == 1:
            self.counter = (self.counter & 0x00FF) | (value << 8)
        elif offset == 2:
            self.reload_value = (self.reload_value & 0xFF00) | value
        elif offset == 3:
            self.reload_value = (self.reload_value & 0x00FF) | (value << 8)
        elif offset == 4:
            self.enabled = bool(value & 0x01)
            self.interrupt_enabled = bool(value & 0x02)
            if value & 0x04:
                self.counter_running = True
                self.counter = self.reload_value
                self.timeout_flag = False
            else:
                self.counter_running = False
        elif offset == 5:
            if value & 0x01:
                self.timeout_flag = False

    def tick(self, cycles=1): #do a tick
        self.tick_count += cycles
        if self.counter_running and self.enabled:
            self.counter -= cycles
            if self.counter <= 0:
                self.counter = self.reload_value
                self.timeout_flag = True
                return True
        return False

    def get_elapsed_us(self): #look at time elapsed
        return (self.tick_count * 1000000) // self.clock_hz

    def reset(self): #reset the timer
        self.counter = 0xFFFF
        self.reload_value = 0xFFFF
        self.enabled = False
        self.interrupt_enabled = False
        self.counter_running = False
        self.timeout_flag = False
        self.tick_count = 0
