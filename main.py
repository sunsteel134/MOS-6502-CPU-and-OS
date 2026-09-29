from big_computer import computer
from assembler.assembler import assembler

def start():
    sys = computer(clock_frequency=1000000)
    asm = assembler()
    with open("kernel.asm", "r") as f:
        source_code = f.read()
    asm.PC = 0x8000
    machine_code = asm.assemble(source_code)
    sys.bus.load_ROM(0x8000, machine_code)
    sys.bus.set_vector(0xFFFC, 0x8000)
    sys.reset()

    def tick():
        sys.run(max_cycles=2000)
        sys.monitor.render()
        sys.monitor.root.after(30, tick)

    sys.monitor.root.after(10, tick)
    sys.monitor.root.mainloop()

if __name__ == "__main__":
    start()
