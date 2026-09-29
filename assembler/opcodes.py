MODE_IMMEDIATE = 0
MODE_ZERO_PAGE = 1
MODE_ZERO_PAGE_X = 2
MODE_ZERO_PAGE_Y = 3
MODE_ABSOLUTE = 4
MODE_ABSOLUTE_X = 5
MODE_ABSOLUTE_Y = 6
MODE_INDIRECT_X = 7
MODE_INDIRECT_Y = 8
MODE_INDIRECT = 9
MODE_ACCUMULATOR = 10

opcodes = { #all pneumonics to make the OS and kernel making easier
    ("LDA", MODE_IMMEDIATE): 0xA9,
    ("LDA", MODE_ZERO_PAGE): 0xA5,
    ("LDA", MODE_ZERO_PAGE_X): 0xB5,
    ("LDA", MODE_ABSOLUTE): 0xAD,
    ("LDA", MODE_ABSOLUTE_X): 0xBD,
    ("LDA", MODE_ABSOLUTE_Y): 0xB9,
    ("LDA", MODE_INDIRECT_X): 0xA1,
    ("LDA", MODE_INDIRECT_Y): 0xB1,

    ("LDX", MODE_IMMEDIATE): 0xA2,
    ("LDX", MODE_ZERO_PAGE): 0xA6,
    ("LDX", MODE_ZERO_PAGE_Y): 0xB6,
    ("LDX", MODE_ABSOLUTE): 0xAE,
    ("LDX", MODE_INDIRECT_Y): 0xBE,

    ("LDY", MODE_IMMEDIATE): 0xA0,
    ("LDY", MODE_ZERO_PAGE): 0xA4,
    ("LDY", MODE_ZERO_PAGE_X): 0xB4,
    ("LDY", MODE_ABSOLUTE): 0xAC,
    ("LDY", MODE_INDIRECT_X): 0xBC,

    ("STA", MODE_ZERO_PAGE): 0x85,
    ("STA", MODE_ZERO_PAGE_X): 0x95,
    ("STA", MODE_ABSOLUTE): 0x8D,
    ("STA", MODE_ABSOLUTE_X): 0x9D,
    ("STA", MODE_ABSOLUTE_Y): 0x99,
    ("STA", MODE_INDIRECT_X): 0x81,
    ("STA", MODE_INDIRECT_Y): 0x91,

    ("STX", MODE_ZERO_PAGE): 0x86,
    ("STX", MODE_ZERO_PAGE_Y): 0x8E,
    ("STX", MODE_ABSOLUTE): 0x84,

    ("STY", MODE_ZERO_PAGE): 0x84,
    ("STY", MODE_ZERO_PAGE_X): 0x94,
    ("STY", MODE_ABSOLUTE): 0x8C,

    ("TAX"): 0xAA,
    ("TAY"): 0xA8,
    ("TXA"): 0x8A,
    ("TYA"): 0x98,
    ("TSX"): 0xBA,
    ("TXS"): 0x9A,

    ("PHA"): 0x48,
    ("PHP"): 0x08,
    ("PLA"): 0x68,
    ("PLP"): 0x28,

    ("AND", MODE_IMMEDIATE): 0x29,
    ("AND", MODE_ZERO_PAGE): 0x25,
    ("AND", MODE_ZERO_PAGE_X): 0x35,
    ("AND", MODE_ABSOLUTE): 0x2D,
    ("AND", MODE_ABSOLUTE_X): 0x3D,
    ("AND", MODE_ABSOLUTE_Y): 0x39,
    ("AND", MODE_INDIRECT_X): 0x21,
    ("AND", MODE_INDIRECT_Y): 0x31,

    ("EOR", MODE_IMMEDIATE): 0x49,
    ("EOR", MODE_ZERO_PAGE): 0x45,
    ("EOR", MODE_ZERO_PAGE_X): 0x55,
    ("EOR", MODE_ABSOLUTE): 0x4D,
    ("EOR", MODE_ABSOLUTE_X): 0x5D,
    ("EOR", MODE_ABSOLUTE_Y): 0x59,
    ("EOR", MODE_INDIRECT_X): 0x41,
    ("EOR", MODE_INDIRECT_Y): 0x51,

    ("ORA", MODE_IMMEDIATE): 0x09,
    ("ORA", MODE_ZERO_PAGE): 0x05,
    ("ORA", MODE_ZERO_PAGE_X): 0x15,
    ("ORA", MODE_ABSOLUTE): 0x0D,
    ("ORA", MODE_ABSOLUTE_X): 0x1D,
    ("ORA", MODE_ABSOLUTE_Y): 0x19,
    ("ORA", MODE_INDIRECT_X): 0x01,
    ("ORA", MODE_INDIRECT_Y): 0x11,

    ("BIT", MODE_ZERO_PAGE): 0x24,
    ("BIT", MODE_ABSOLUTE): 0x2C,

    ("ADC", MODE_IMMEDIATE): 0x69,
    ("ADC", MODE_ZERO_PAGE): 0x65,
    ("ADC", MODE_ZERO_PAGE_X): 0x75,
    ("ADC", MODE_ABSOLUTE): 0x6D,
    ("ADC", MODE_ABSOLUTE_X): 0x7D,
    ("ADC", MODE_ABSOLUTE_Y): 0x79,
    ("ADC", MODE_INDIRECT_X): 0x61,
    ("ADC", MODE_INDIRECT_Y): 0x71,

    ("SBC", MODE_IMMEDIATE): 0xE9,
    ("SBC", MODE_ZERO_PAGE): 0xE5,
    ("SBC", MODE_ZERO_PAGE_X): 0xF5,
    ("SBC", MODE_ABSOLUTE): 0xED,
    ("SBC", MODE_ABSOLUTE_X): 0xFD,
    ("SBC", MODE_ABSOLUTE_Y): 0xF9,
    ("SBC", MODE_INDIRECT_X): 0xE1,
    ("SBC", MODE_INDIRECT_Y): 0xF1,

    ("CMP", MODE_IMMEDIATE): 0xC9,
    ("CMP", MODE_ZERO_PAGE): 0xC5,
    ("CMP", MODE_ZERO_PAGE_X): 0xD5,
    ("CMP", MODE_ABSOLUTE): 0xCD,
    ("MPC", MODE_ABSOLUTE_X): 0xDD,
    ("CMP", MODE_ABSOLUTE_Y): 0xD9,
    ("CMP", MODE_INDIRECT_X): 0xC1,
    ("CMP", MODE_INDIRECT_Y): 0xD1,

    ("CPX", MODE_IMMEDIATE): 0xE0,
    ("CPX", MODE_ZERO_PAGE): 0xE4,
    ("CPX", MODE_ABSOLUTE): 0xEC,

    ("CPY", MODE_IMMEDIATE): 0xC0,
    ("CPY", MODE_ZERO_PAGE): 0xC4,
    ("CPY", MODE_ABSOLUTE): 0xCC,

    ("INC", MODE_ZERO_PAGE): 0xE6,
    ("INC", MODE_ZERO_PAGE_X): 0xF6,
    ("INC", MODE_ABSOLUTE): 0xEE,
    ("INC", MODE_ABSOLUTE_X): 0xFE,

    ("INX"): 0xE8,
    ("INY"): 0xC8,

    ("DEC", MODE_ZERO_PAGE): 0xC6,
    ("DEC", MODE_ZERO_PAGE_X): 0xD6,
    ("DEC", MODE_ABSOLUTE): 0xCE,
    ("DEC", MODE_ABSOLUTE_X): 0xDE,

    ("DEX"): 0xCA,
    ("DEY"): 0x88,

    ("ASL", MODE_ACCUMULATOR): 0x0A,
    ("ASL", MODE_ZERO_PAGE): 0x06,
    ("ASL", MODE_ZERO_PAGE_X): 0x16,
    ("ASL", MODE_ABSOLUTE): 0x0E,
    ("ASL", MODE_ABSOLUTE_X): 0x1E,

    ("LSR", MODE_ACCUMULATOR): 0x4A,
    ("LSR", MODE_ZERO_PAGE): 0x46,
    ("LSR", MODE_ZERO_PAGE_X): 0x56,
    ("LSR", MODE_ABSOLUTE): 0x4E,
    ("LSR", MODE_ABSOLUTE_X): 0x5E,

    ("ROL", MODE_ACCUMULATOR): 0x2A,
    ("ROL", MODE_ZERO_PAGE): 0x26,
    ("ROL", MODE_ZERO_PAGE_X): 0x36,
    ("ROL", MODE_ABSOLUTE): 0x2E,
    ("ROL", MODE_ABSOLUTE_X): 0x3E,

    ("ROR", MODE_ACCUMULATOR): 0x6A,
    ("ROR", MODE_ZERO_PAGE): 0x66,
    ("ROR", MODE_ZERO_PAGE_X): 0x76,
    ("ROR", MODE_ABSOLUTE): 0x6E,
    ("ROR", MODE_ABSOLUTE_X): 0x7E,

    ("JMP", MODE_ABSOLUTE): 0x4C,
    ("JMP", MODE_INDIRECT): 0x6C,
    ("JSR", MODE_ABSOLUTE): 0x20,

    ("RTS"): 0x60,

    ("BCC"): 0x90,
    ("BCS"): 0xB0,
    ("BEQ"): 0xF0,
    ("BMI"): 0x30,
    ("BNE"): 0xD0,
    ("BPL"): 0x10,
    ("BVC"): 0x50,
    ("BVS"): 0x80,

    ("CLC"): 0x18,
    ("CLD"): 0xD8,
    ("CLI"): 0x58,
    ("CLV"): 0xB8,
    ("SEC"): 0x38,
    ("SED"): 0xF8,
    ("SEI"): 0x78,

    ("BRK"): 0x00,
    ("RTI"): 0x40,
    ("NOP"): 0xEA
}
