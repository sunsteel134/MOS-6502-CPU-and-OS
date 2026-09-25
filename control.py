import secondary_memory
RAM = secondary_memory.mems()

FLAG_C = 1 << 0  #carry
FLAG_Z = 1 << 1  #zero
FLAG_I = 1 << 2  #interrupt
FLAG_D = 1 << 3  #decimal mode
FLAG_B = 1 << 4  #break command
FLAG_U = 1 << 5  #unused (always 1)
FLAG_V = 1 << 6  #overflow
FLAG_N = 1 << 7  #negative

MODE_IMMEDIATE = 0 #explained later
MODE_ZERO_PAGE = 1
MODE_ZERO_PAGE_X = 2
MODE_ZERO_PAGE_Y = 3
MODE_ABSOLUTE = 4
MODE_ABSOLUTE_X = 5
MODE_ABSOLUTE_Y = 6
MODE_INDIRECT_X = 7
MODE_INDIRECT_Y = 8

class CPU:
    def __init__(self):
        self.A = 0x00
        self.X = 0x00
        self.Y = 0x00
        self.PC = 0x1000
        self.SP = 0xFD
        self.flag = FLAG_U
        self.P = 0x20

    def set_flag(self, flag_mask, val):
        if val == True:
            self.flag |= flag_mask
        else:
            self.flag &= ~flag_mask

    def update_nz(self, val):
        val &= 0xFF
        self.set_flag(FLAG_Z, val == 0)
        self.set_flag(FLAG_N, (val & 0x80) != 0)

    def update_nvz(self, val, overflow):
        val &= 0xFF
        self.set_flag(FLAG_Z, val == 0)
        self.set_flag(FLAG_N, (val & 0x80) != 0)
        self.set_flag(FLAG_V, overflow)

    def get_operand_address(self, mode):
        if mode == MODE_IMMEDIATE: #byte right after instruction
            address = self.PC
            self.PC += 1
            return address
        elif mode == MODE_ZERO_PAGE: #reads 1 bytes of first 256 bytes of RAM (zero page)
            address = RAM.memory[self.PC]
            self.PC += 1
            return address
        elif mode == MODE_ZERO_PAGE_X: #adds the value in the X register then does that plus address and checks the zero page
            base_zp = RAM.memory[self.PC]
            self.PC += 1
            return (base_zp + self.X) & 0xFF
        elif mode == MODE_ZERO_PAGE_Y: #same as zero page x but adds Y
            base_zp = RAM.memory[self.PC]
            self.PC += 1
            return (base_zp + self.Y) & 0xFF
        elif mode == MODE_ABSOLUTE: #reads full 2 byte address
            least = RAM.memory[self.PC]
            most = RAM.memory[self.PC + 1]
            self.PC += 2
            return (most << 8) | least
        elif mode == MODE_ABSOLUTE_X: #checks the RAM address of the value in X plus the base address given
            least = RAM.memory[self.PC]
            most = RAM.memory[self.PC + 1]
            self.PC += 2
            base_address = (most << 8) | least
            return (base_address + self.X) & 0xFFFF
        elif mode == MODE_ABSOLUTE_Y: #same as absolute X but add the Y instead
            least = RAM.memory[self.PC]
            most = RAM.memory[self.PC + 1]
            self.PC += 2
            base_address = (most << 8) | least
            return (base_address + self.Y) & 0xFFFF
        elif mode == MODE_INDIRECT_X: #adds X value then checks the zero page and uses that as the pointer
            base_zp = RAM.memory[self.PC]
            self.PC += 1
            zp_address = (base_zp + self.X) & 0xFF
            least = RAM.memory[zp_address]
            most = RAM.memory[(zp_address + 1) & 0xFF]
            return (most << 8) | least
        elif mode == MODE_INDIRECT_Y: #looks at the zero page then does that address plus the current Y adddress
            zp_address = RAM.memory[self.PC]
            self.PC += 1
            least = RAM.memory[zp_address]
            most = RAM.memory[(zp_address + 1) & 0xFF]
            base_address = (most << 8) | least
            return (base_address + self.Y) & 0xFFFF

    def LDA(self, mode):
        address = self.get_operand_address(mode)
        val = RAM.memory[address]
        self.A = val
        self.update_nz(self.A)

    def LDX(self, mode):
        address = self.get_operand_address(mode)
        val = RAM.memory[address]
        self.X = val
        self.update_nz(self.X)

    def LDY(self, mode):
        address = self.get_operand_address(mode)
        val = RAM.memory[address]
        self.Y = val
        self.update_nz(self.Y)

    def STA(self, mode):
        address = self.get_operand_address(mode)
        RAM.memory[address] = self.A

    def STX(self, mode):
        address = self.get_operand_address(mode)
        RAM.memory[address] = self.X

    def STY(self, mode):
        address = self.get_operand_address(mode)
        RAM.memory[address] = self.Y

    def TAX(self): #transfer accumulator to X register
        self.X = self.A
        self.update_nz(self.X)

    def TAY(self): #transfer accumulator to Y register
        self.Y = self.A
        self.update_nz(self.Y)

    def TXA(self): #transfer X register to accumulator
        self.A = self.X
        self.update_nz(self.A)

    def TYA(self): #transfer Y register to accumulator
        self.A = self.Y
        self.update_nz(self.A)

    def TSX(self): #sets the X gegister to the value in the stack pointer
        self.X = self.SP
        self.update_nz(self.X)

    def TXS(self): #sets the value of the stack pointer to the value in the X register
        self.SP = self.X

    def PHA(self): #push whats in accumulator to stack
        RAM.memory[0x0100 + self.SP] = self.A & 0xFF
        self.SP = (self.SP - 1) & 0xFF

    def PHP(self): #push flags to stack
        flags = self.flag | FLAG_B | FLAG_U
        RAM.memory[0x0100 + self.SP] = flags & 0xFF
        self.SP = (self.SP - 1) & 0xFF

    def PLA(self): #pull from stack then store in accumulator
        self.SP = (self.SP + 1) & 0xFF
        self.A = RAM.memory[0x0100 + self.SP]
        self.update_nz(self.A)

    def PLP(self): #pull from stack then set flags
        self.SP = (self.SP + 1) & 0xFF
        flags = RAM.memory[0x0100 + self.SP]
        self.flag = (flags & ~(FLAG_B | FLAG_U)) | FLAG_U

    def AND(self, mode): #ANd gate (pretty obvious)
        address = self.get_operand_address(mode)
        val = RAM.memory[address]
        self.A = self.A & val
        self.update_nz(self.A)

    def EOR(self, mode): #XOR gate
        address = self.get_operand_address(mode)
        val = RAM.memory[address]
        self.A = self.A ^ val
        self.update_nz(self.A)

    def IOR(self, mode): #regular OR gate
        address = self.get_operand_address(mode)
        val = RAM.memory[address]
        self.A = self.A | val
        self.update_nz(self.A)

    def BIT(self, mode): #check if anything is in the address given
        address = self.get_operand_address(mode)
        val = RAM.memory[address]
        temp = self.A & val
        overflow_bit6 = (val & 0x40) != 0
        self.update_nvz(self.A, overflow_bit6)
        self.set_flag(FLAG_Z, temp == 0)

    def ADC(self, mode): #add with a carry bit
        address = self.get_operand_address(mode)
        val = RAM.memory[address]
        carry = 1 if (self.flag & FLAG_C) else 0
        result = self.A + val + carry
        overflow = ((self.A ^ result) & (val ^ result) & 0x80) != 0
        self.A = result & 0xFF
        self.update_nvz(self.A, overflow)
        self.set_flag(FLAG_C, result > 0xFF)

    def SBC(self, mode): #subtract with a carry bit
        address = self.get_operand_address(mode)
        val = RAM.memory[address]
        inv = val ^0xFF
        carry = 1 if (self.flag & FLAG_C) else 0
        result = self.A + inv + carry
        overflow = ((self.A ^ result) & (val ^ result) & 0x80) != 0
        self.A = result & 0xFF
        self.update_nvz(self.A, overflow)
        self.set_flag(FLAG_C, result > 0xFF)

    def CMP(self, mode): #compare the value in the accumulator and in the RAM addess
        address = self.get_operand_address(mode)
        val = RAM.memory[address]
        temp = self.A - val
        self.set_flag(FLAG_C, self.A >= val)
        self.update_nz(temp & 0xFF)

    def CPX(self, mode): #compare the value in the X register and in the RAM addess
        address = self.get_operand_address(mode)
        val = RAM.memory[address]
        temp = self.X - val
        self.set_flag(FLAG_C, self.X >= val)
        self.update_nz(temp & 0xFF)

    def CPY(self, mode): #compare the value in the Y register and in the RAM addess
        address = self.get_operand_address(mode)
        val = RAM.memory[address]
        temp = self.Y - val
        self.set_flag(FLAG_C, self.Y >= val)
        self.update_nz(temp & 0xFF)

    def INC(self, mode): #increase value by 1
        address = self.get_operand_address(mode)
        val = RAM.memory[address]
        val = (val + 1) & 0xFF
        RAM.memory[address] = val
        self.update_nz(val)

    def INX(self): #increase value in X by 1
        self.X = (self.X + 1) & 0xFF
        self.update_nz(self.X)

    def INY(self): #same as X but with Y register
        self.Y = (self.Y + 1) & 0xFF
        self.update_nz(self.Y)

    def DEC(self, mode): #all same things as before but decreases by 1
        address = self.get_operand_address(mode)
        val = RAM.memory[address]
        val = (val - 1) & 0xFF
        RAM.memory[address] = val
        self.update_nz(val)

    def DEX(self):
        self.X = (self.X - 1) & 0xFF
        self.update_nz(self.X)

    def DEY(self):
        self.Y = (self.Y - 1) & 0xFF
        self.update_nz(self.Y)

    def ASL(self, mode): #arithmetic left shift
        address = self.get_operand_address(mode)
        val = RAM.memory[address]
        self.set_flag(FLAG_C, (val & 0x80) != 0)
        val = (val << 1) & 0xFF
        RAM.memory[address] = val
        self.update_nz(val)
    def ASL_Acc(self): #does a shift on the accumulator
        self.set_flag(FLAG_C, (self.A & 0x80) != 0)
        self.A = (self.A << 1) & 0xFF
        self.update_nz(self.A)

    def LSR(self, mode): #logical right shift
        address = self.get_operand_address(mode)
        val = RAM.memory[address]
        self.set_flag(FLAG_C, (val & 0x01) != 0)
        val = val >> 1
        RAM.memory[address] = val
        self.update_nz(val)
    def LSR_Acc(self): #does the shift to accumulator (same for all with _acc at end)
        self.set_flag(FLAG_C, (self.A & 0x01) != 0)
        self.A = self.A >> 1
        self.update_nz(self.A)

    def ROL(self, mode): #cyclical shift to left
        address = self.get_operand_address(mode)
        val = RAM.memory[address]
        carry = 1 if (self.flag & FLAG_C) else 0
        self.set_flag(FLAG_C, (val & 0x80) != 0)
        val = ((val << 1) | carry) & 0xFF
        RAM.memory[address] = val
        self.update_nz(val)
    def ROL_Acc(self):
        carry = 1 if (self.flag & FLAG_C) else 0
        self.set_flag(FLAG_C, (self.A & 0x80) != 0)
        self.A = ((self.A << 1) | carry) & 0xFF
        self.update_nz(self.A)

    def ROR(self, mode): #cyclical shift to right
        address = self.get_operand_address(mode)
        val = RAM.memory[address]
        carry = 1 if (self.flag & FLAG_C) else 0
        self.set_flag(FLAG_C, (val & 0x80) != 0)
        val = ((val >> 1) | carry) & 0xFF
        RAM.memory[address] = val
        self.update_nz(val)
    def ROR_Acc(self):
        carry = 1 if (self.flag & FLAG_C) else 0
        self.set_flag(FLAG_C, (self.A & 0x80) != 0)
        self.A = ((self.A >> 1) | carry) & 0xFF
        self.update_nz(self.A)

    def JMP(self, mode): #set PC to the value in the address given
        address = self.get_operand_address(mode)
        if mode == MODE_ABSOLUTE:
            self.PC = address
        else:
            least = RAM.memory[address]
            if (address & 0xFF) == 0xFF:
                most = RAM.memory[address & 0xFF00]
            else:
                most = RAM.memory[address + 1]
            self.PC = (most << 8) | least

    def tick(self):
        command = RAM.memory[self.PC]
        self.PC += 1
        if command == 0xA9:
            self.LDA(0)
        if command == 0xA2:
            self.LDX(0)
        if command == 0xA0:
            self.LDY(0)
        if command == 0x8D:
            self.STA(2)
        if command == 0x8E:
            self.STX(2)
        if command == 0x8C:
            self.STY(2)

cpu = CPU()

RAM.memory[0x1000] = 0xA9
RAM.memory[0x1001] = 0x12

RAM.memory[0x1002] = 0xA2
RAM.memory[0x1003] = 0x10

RAM.memory[0x1004] = 0xA0
RAM.memory[0x1005] = 0x08

cpu.tick()
cpu.tick()
cpu.tick()
if __name__ == "__main__":
    print(cpu.A)
    print(cpu.X)
    print(cpu.Y)
