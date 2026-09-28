from control import CPU
from busses import bus
from clock import clock
from reseter import reset_controller
from uninterupter import interrupt_controller

class computer:
    def __init__(self, clock_frequency=1000000):
        self.bus = bus()
        self.cpu = CPU(self.bus)
        self.clock = clock(hz=clock_frequency)
        self.reset_controller = reset_controller(self.bus, self.cpu)
        self.interrupt_controller = interrupt_controller(self.bus, self.cpu)
        self.running = False
        self.halted = False
        self.cycles_executed = 0

    def initialize(self): #I cant describe it just read what it does im sure you can guess
        from rom import install
        install(self.bus)

    def reset(self): #reset everything
        self.reset_controller.trigger_reset()
        self.clock.reset()
        self.cycles_executed = 0
        self.halted = False

    def run(self, max_cycles=None): #actually start the computer
        self.running = True
        start_cycles = self.cycles_executed
        while self.running and not self.halted:
            if max_cycles and (self.cycles_executed - start_cycles) >= max_cycles:
                break
            if self.reset_controller.is_reset_pending():
                self.reset_controller.process_reset()
            self.interrupt_controller.process_interrupts()
            start_pc = self.cpu.PC
            try:
                self.cpu.tick()
                self.clock.tick(1)
                self.cycles_executed += 1
            except Exception as e:
                print(f"CPU error at ${start_pc:04X}: {e}")
                self._dump_state()
                self.halted = True

    def step(self): #do one thing
        if self.reset_controller.is_reset_pending():
            self.reset_controller.process_reset()
        self.interrupt_controller.process_interrupts()
        self.cpu.tick()
        self.clock.tick(1)
        self.cycles_executed += 1

    def stop(self): #stop, but why you do that
        self.running = False

    def _dump_state(self): #print all info for debug
        print(f"PC: ${self.cpu.PC:04X}")
        print(f"SP: ${self.cpu.SP:02X}")
        print(f"A:  ${self.cpu.A:02X}")
        print(f"X:  ${self.cpu.X:02X}")
        print(f"Y:  ${self.cpu.Y:02X}")
        print(f"P:  ${self.cpu.flag:02X}")

    def dump_memory(self, start, end): #print the memory range
        print(self.bus.dump(start, end))

    def get_time_elapsed(self): #find how long youve been on
        return self.cycles_executed / self.clock.frequency
