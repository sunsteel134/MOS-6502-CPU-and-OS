class reset_controller:
    def __init__(self, bus, cpu):
        self.bus = bus
        self.cpu = cpu
        self.reset_pending = False
        self.reset_count = 0

    def trigger_reset(self): #reset hardware
        self.reset_pending = True
        print("Reset triggered")

    def process_reset(self): #resets everything
        if self.reset_pending:
            self.cpu.reset()
            self.reset_pending = False
            self.reset_count += 1
            print(f"System reset complete (reset #{self.reset_count})")

    def is_reset_pending(self): #check if a reset is needed
        return self.reset_pending

    def get_reset_count(self): #gets how many resets have happened (jesus christ dude just look at the code)
        return self.reset_count
