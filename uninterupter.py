class interrupt_controller:
    def __init__(self, bus, cpu):
        self.bus = bus
        self.cpu = cpu
        self.irq_pending = False
        self.nmi_pending = False
        self.irq_enabled = True
        self.irq_count = 0
        self.nmi_count = 0

    def request_irq(self): #asks for the IQR
        if self.irq_enabled:
            self.irq_pending = True

    def request_nmi(self): #asks for NMI
        self.nmi_pending = True

    def process_interrupts(self): #tells a function to maybe do something about that interupt
        if self.nmi_pending:
            self.nmi_pending = False
            self.nmi_count += 1
            self._trigger_nmi()
            return True
        if self.irq_pending and not (self.cpu.flag & 0x04):  # FLAG_I
            self.irq_pending = False
            self.irq_count += 1
            self._trigger_irq()
            return True
        return False

    def _trigger_nmi(self): #actually tries to fix the problem (NMI)
        self.cpu.SP = (self.cpu.SP - 1) & 0xFF
        self.bus.write(0x0100 + self.cpu.SP, (self.cpu.PC >> 8) & 0xFF)
        self.cpu.SP = (self.cpu.SP - 1) & 0xFF
        self.bus.write(0x0100 + self.cpu.SP, self.cpu.PC & 0xFF)
        self.cpu.SP = (self.cpu.SP - 1) & 0xFF
        flags = self.cpu.flag | 0x20 | 0x10
        self.bus.write(0x0100 + self.cpu.SP, flags)
        self.cpu.set_flag(0x04, True)
        self.cpu.PC = self.bus.read_word(0xFFFA)
        print(f"NMI triggered -> ${self.cpu.PC:04X}")

    def _trigger_irq(self): #again just does something about an IQR
        self.cpu.SP = (self.cpu.SP - 1) & 0xFF
        self.bus.write(0x0100 + self.cpu.SP, (self.cpu.PC >> 8) & 0xFF)
        self.cpu.SP = (self.cpu.SP - 1) & 0xFF
        self.bus.write(0x0100 + self.cpu.SP, self.cpu.PC & 0xFF)
        self.cpu.SP = (self.cpu.SP - 1) & 0xFF
        flags = self.cpu.flag | 0x20 | 0x10
        self.bus.write(0x0100 + self.cpu.SP, flags)
        self.cpu.set_flag(0x04, True)
        self.cpu.PC = self.bus.read_word(0xFFFE)
        print(f"IRQ triggered -> ${self.cpu.PC:04X}")

    def enable_irq(self): #lets the computer complain about IQRs
        self.irq_enabled = True

    def disable_irq(self): #shuts up the IQR whining
        self.irq_enabled = False

    def are_irqs_enabled(self): #checks if computer can whine
        return self.irq_enabled

    def get_irq_count(self): #has a look how many have been sorted
        return self.irq_count

    def get_nmi_count(self): #same thing as last but with NMIs
        return self.nmi_count
