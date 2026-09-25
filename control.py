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
MODE_INDIRECT = 9

class CPU:
    def __init__(self):
        self.A = 0x00
        self.X = 0x00
        self.Y = 0x00
        self.PC = 0x1000
        self.SP = 0xFD
        self.flag = FLAG_U

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
        self.set_flag(FLAG_Z, (self.A & val) == 0)
        self.set_flag(FLAG_V, (val & 0x40) != 0)
        self.set_flag(FLAG_N, (val & 0x80) != 0)

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
        self.set_flag(FLAG_C, (val & 0x01) != 0)
        val = ((val >> 1) | carry) & 0xFF
        RAM.memory[address] = val
        self.update_nz(val)
    def ROR_Acc(self):
        carry = 1 if (self.flag & FLAG_C) else 0
        self.set_flag(FLAG_C, (self.A & 0x01) != 0)
        self.A = ((self.A >> 1) | carry) & 0xFF
        self.update_nz(self.A)

    def JMP(self, mode): #set PC to the value in the address given
        address = self.get_operand_address(mode)
        if mode == MODE_ABSOLUTE:
            self.PC = address
        elif mode == MODE_INDIRECT:
            low = RAM.memory[address]
            if (address & 0x00FF) == 0x00FF:
                high = RAM.memory[address & 0xFF00]
            else:
                high = RAM.memory[(address + 1) & 0xFFFF]

            self.PC = (high << 8) | low

    def JSR(self, mode): #like branch in LMC but its where it will come back to after the code is done
        target_address = self.get_operand_address(mode)
        return_address = self.PC - 1
        RAM.memory[0x0100 + self.SP] = (return_address >> 8) & 0xFF
        self.SP = (self.SP - 1) & 0xFF
        RAM.memory[0x0100 + self.SP] = return_address & 0xFF
        self.SP = (self.SP - 1) & 0xFF
        self.PC = target_address

    def RTS(self): #tells the CPU to go back to where it said JSR
        self.SP = (self.SP + 1) & 0xFF
        least = RAM.memory[0x0100 + self.SP]
        self.SP = (self.SP + 1) & 0xFF
        most = RAM.memory[0x0100 + self.SP]
        return_address = (most << 8) | least
        self.PC = return_address + 1

    def BCS(self): #branch if the carry flag is set
        offset = RAM.memory[self.PC]
        self.PC += 1
        if self.flag & FLAG_C:
            if offset & 0x80:
                offset -= 0x100
            self.PC = (self.PC + offset) & 0xFFFF

    def BCC(self): #branch if the carry flag is not set
        offset = RAM.memory[self.PC]
        self.PC += 1
        if not (self.flag & FLAG_C):
            if offset & 0x80:
                offset -= 0x100
            self.PC = (self.PC + offset) & 0xFFFF

    def BEQ(self): #branch if the zero flag is set
        offset = RAM.memory[self.PC]
        self.PC += 1
        if self.flag & FLAG_Z:
            if offset & 0x80:
                offset -= 0x100
            self.PC = (self.PC + offset) & 0xFFFF

    def BNE(self): #branch if the zero flag is not set
        offset = RAM.memory[self.PC]
        self.PC += 1
        if not (self.flag & FLAG_Z):
            if offset & 0x80:
                offset -= 0x100
            self.PC = (self.PC + offset) & 0xFFFF

    def BMI(self): #branch if the negative flag is set
        offset = RAM.memory[self.PC]
        self.PC += 1
        if self.flag & FLAG_N:
            if offset & 0x80:
                offset -= 0x100
            self.PC = (self.PC + offset) & 0xFFFF

    def BPL(self): #branch if the negative flag is not set
        offset = RAM.memory[self.PC]
        self.PC += 1
        if not (self.flag & FLAG_N):
            if offset & 0x80:
                offset -= 0x100
            self.PC = (self.PC + offset) & 0xFFFF

    def BVS(self): #branch if the overflow flag is set
        offset = RAM.memory[self.PC]
        self.PC += 1
        if self.flag & FLAG_V:
            if offset & 0x80:
                offset -= 0x100
            self.PC = (self.PC + offset) & 0xFFFF

    def BVC(self): #branch if the overflow flag is not set
        offset = RAM.memory[self.PC]
        self.PC += 1
        if not (self.flag & FLAG_V):
            if offset & 0x80:
                offset -= 0x100
            self.PC = (self.PC + offset) & 0xFFFF

    def CLC(self): #clear carry flag
        self.set_flag(FLAG_C, False)

    def CLD(self): #clear decimal flag
        self.set_flag(FLAG_D, False)

    def CLI(self): #clear interupt disable flag
        self.set_flag(FLAG_I, False)

    def CLV(self): #clear overflow flag
        self.set_flag(FLAG_V, False)

    def SEC(self): #set carry flag
        self.set_flag(FLAG_C, True)

    def SED(self): #set decimal flag
        self.set_flag(FLAG_D, True)

    def SEI(self): #set interupt disable flag
        self.set_flag(FLAG_I, True)

    def BRK(self): #cause an interupt
        return_addr = (self.PC + 1) & 0xFFFF
        self.SP = (self.SP - 1) & 0xFF
        RAM.memory[0x0100 + self.SP] = (return_addr >> 8) & 0xFF
        self.SP = (self.SP - 1) & 0xFF
        RAM.memory[0x0100 + self.SP] = return_addr & 0xFF
        flags = self.flag | FLAG_B | FLAG_U
        self.SP = (self.SP - 1) & 0xFF
        RAM.memory[0x0100 + self.SP] = flags & 0xFF
        self.set_flag(FLAG_I, True)
        low = RAM.memory[0xFFFE]
        high = RAM.memory[0xFFFF]
        self.PC = (high << 8) | low

    def NOP(self): #literally just pass
        pass

    def RTI(self): #come back from an interupt
        self.SP = (self.SP + 1) & 0xFF
        flags = RAM.memory[0x0100 + self.SP]
        self.flag = (flags & ~(FLAG_B | FLAG_U)) | FLAG_U
        self.SP = (self.SP + 1) & 0xFF
        least = RAM.memory[0x0100 + self.SP]
        self.SP = (self.SP + 1) & 0xFF
        most = RAM.memory[0x0100 + self.SP]
        self.PC = (most << 8) | least

    def tick(self):
        opcode = RAM.memory[self.PC]
        self.PC = (self.PC + 1) & 0xFFFF
        if opcode == 0xA9:
            self.LDA(MODE_IMMEDIATE)
        elif opcode == 0xA5:
            self.LDA(MODE_ZERO_PAGE)
        elif opcode == 0xB5:
            self.LDA(MODE_ZERO_PAGE_X)
        elif opcode == 0xAD:
            self.LDA(MODE_ABSOLUTE)
        elif opcode == 0xBD:
            self.LDA(MODE_ABSOLUTE_X)
        elif opcode == 0xB9:
            self.LDA(MODE_ABSOLUTE_Y)
        elif opcode == 0xA1:
            self.LDA(MODE_INDIRECT_X)
        elif opcode == 0xB1:
            self.LDA(MODE_INDIRECT_Y)
        elif opcode == 0xA2:
            self.LDX(MODE_IMMEDIATE)
        elif opcode == 0xA6:
            self.LDX(MODE_ZERO_PAGE)
        elif opcode == 0xB6:
            self.LDX(MODE_ZERO_PAGE_Y)
        elif opcode == 0xAE:
            self.LDX(MODE_ABSOLUTE)
        elif opcode == 0xBE:
            self.LDX(MODE_ABSOLUTE_Y)
        elif opcode == 0xA0:
            self.LDY(MODE_IMMEDIATE)
        elif opcode == 0xA4:
            self.LDY(MODE_ZERO_PAGE)
        elif opcode == 0xB4:
            self.LDY(MODE_ZERO_PAGE_X)
        elif opcode == 0xAC:
            self.LDY(MODE_ABSOLUTE)
        elif opcode == 0xBC:
            self.LDY(MODE_ABSOLUTE_X)
        elif opcode == 0x85:
            self.STA(MODE_ZERO_PAGE)
        elif opcode == 0x95:
            self.STA(MODE_ZERO_PAGE_X)
        elif opcode == 0x8D:
            self.STA(MODE_ABSOLUTE)
        elif opcode == 0x9D:
            self.STA(MODE_ABSOLUTE_X)
        elif opcode == 0x99:
            self.STA(MODE_ABSOLUTE_Y)
        elif opcode == 0x81:
            self.STA(MODE_INDIRECT_X)
        elif opcode == 0x91:
            self.STA(MODE_INDIRECT_Y)
        elif opcode == 0x86:
            self.STX(MODE_ZERO_PAGE)
        elif opcode == 0x96:
            self.STX(MODE_ZERO_PAGE_Y)
        elif opcode == 0x8E:
            self.STX(MODE_ABSOLUTE)
        elif opcode == 0x84:
            self.STY(MODE_ZERO_PAGE)
        elif opcode == 0x94:
            self.STY(MODE_ZERO_PAGE_X)
        elif opcode == 0x8C:
            self.STY(MODE_ABSOLUTE)
        elif opcode == 0xAA:
            self.TAX()
        elif opcode == 0xA8:
            self.TAY()
        elif opcode == 0x8A:
            self.TXA()
        elif opcode == 0x98:
            self.TYA()
        elif opcode == 0xBA:
            self.TSX()
        elif opcode == 0x9A:
            self.TXS()
        elif opcode == 0x48:
            self.PHA()
        elif opcode == 0x08:
            self.PHP()
        elif opcode == 0x68:
            self.PLA()
        elif opcode == 0x28:
            self.PLP()
        elif opcode == 0x29:
            self.AND(MODE_IMMEDIATE)
        elif opcode == 0x25:
            self.AND(MODE_ZERO_PAGE)
        elif opcode == 0x35:
            self.AND(MODE_ZERO_PAGE_X)
        elif opcode == 0x2D:
            self.AND(MODE_ABSOLUTE)
        elif opcode == 0x3D:
            self.AND(MODE_ABSOLUTE_X)
        elif opcode == 0x39:
            self.AND(MODE_ABSOLUTE_Y)
        elif opcode == 0x21:
            self.AND(MODE_INDIRECT_X)
        elif opcode == 0x31:
            self.AND(MODE_INDIRECT_Y)
        elif opcode == 0x49:
            self.EOR(MODE_IMMEDIATE)
        elif opcode == 0x45:
            self.EOR(MODE_ZERO_PAGE)
        elif opcode == 0x55:
            self.EOR(MODE_ZERO_PAGE_X)
        elif opcode == 0x4D:
            self.EOR(MODE_ABSOLUTE)
        elif opcode == 0x5D:
            self.EOR(MODE_ABSOLUTE_X)
        elif opcode == 0x59:
            self.EOR(MODE_ABSOLUTE_Y)
        elif opcode == 0x41:
            self.EOR(MODE_INDIRECT_X)
        elif opcode == 0x51:
            self.EOR(MODE_INDIRECT_Y)
        elif opcode == 0x09:
            self.IOR(MODE_IMMEDIATE)
        elif opcode == 0x05:
            self.IOR(MODE_ZERO_PAGE)
        elif opcode == 0x15:
            self.IOR(MODE_ZERO_PAGE_X)
        elif opcode == 0x0D:
            self.IOR(MODE_ABSOLUTE)
        elif opcode == 0x1D:
            self.IOR(MODE_ABSOLUTE_X)
        elif opcode == 0x19:
            self.IOR(MODE_ABSOLUTE_Y)
        elif opcode == 0x01:
            self.IOR(MODE_INDIRECT_X)
        elif opcode == 0x11:
            self.IOR(MODE_INDIRECT_Y)
        elif opcode == 0x24:
            self.BIT(MODE_ZERO_PAGE)
        elif opcode == 0x2C:
            self.BIT(MODE_ABSOLUTE)
        elif opcode == 0x69:
            self.ADC(MODE_IMMEDIATE)
        elif opcode == 0x65:
            self.ADC(MODE_ZERO_PAGE)
        elif opcode == 0x75:
            self.ADC(MODE_ZERO_PAGE_X)
        elif opcode == 0x6D:
            self.ADC(MODE_ABSOLUTE)
        elif opcode == 0x7D:
            self.ADC(MODE_ABSOLUTE_X)
        elif opcode == 0x79:
            self.ADC(MODE_ABSOLUTE_Y)
        elif opcode == 0x61:
            self.ADC(MODE_INDIRECT_X)
        elif opcode == 0x71:
            self.ADC(MODE_INDIRECT_Y)
        elif opcode == 0xE9:
            self.SBC(MODE_IMMEDIATE)
        elif opcode == 0xE5:
            self.SBC(MODE_ZERO_PAGE)
        elif opcode == 0xF5:
            self.SBC(MODE_ZERO_PAGE_X)
        elif opcode == 0xED:
            self.SBC(MODE_ABSOLUTE)
        elif opcode == 0xFD:
            self.SBC(MODE_ABSOLUTE_X)
        elif opcode == 0xF9:
            self.SBC(MODE_ABSOLUTE_Y)
        elif opcode == 0xE1:
            self.SBC(MODE_INDIRECT_X)
        elif opcode == 0xF1:
            self.SBC(MODE_INDIRECT_Y)
        elif opcode == 0xC9:
            self.CMP(MODE_IMMEDIATE)
        elif opcode == 0xC5:
            self.CMP(MODE_ZERO_PAGE)
        elif opcode == 0xD5:
            self.CMP(MODE_ZERO_PAGE_X)
        elif opcode == 0xCD:
            self.CMP(MODE_ABSOLUTE)
        elif opcode == 0xDD:
            self.CMP(MODE_ABSOLUTE_X)
        elif opcode == 0xD9:
            self.CMP(MODE_ABSOLUTE_Y)
        elif opcode == 0xC1:
            self.CMP(MODE_INDIRECT_X)
        elif opcode == 0xD1:
            self.CMP(MODE_INDIRECT_Y)
        elif opcode == 0xE0:
            self.CPX(MODE_IMMEDIATE)
        elif opcode == 0xE4:
            self.CPX(MODE_ZERO_PAGE)
        elif opcode == 0xEC:
            self.CPX(MODE_ABSOLUTE)
        elif opcode == 0xC0:
            self.CPY(MODE_IMMEDIATE)
        elif opcode == 0xC4:
            self.CPY(MODE_ZERO_PAGE)
        elif opcode == 0xCC:
            self.CPY(MODE_ABSOLUTE)
        elif opcode == 0xE6:
            self.INC(MODE_ZERO_PAGE)
        elif opcode == 0xF6:
            self.INC(MODE_ZERO_PAGE_X)
        elif opcode == 0xEE:
            self.INC(MODE_ABSOLUTE)
        elif opcode == 0xFE:
            self.INC(MODE_ABSOLUTE_X)
        elif opcode == 0xE8:
            self.INX()
        elif opcode == 0xC8:
            self.INY()
        elif opcode == 0xC6:
            self.DEC(MODE_ZERO_PAGE)
        elif opcode == 0xD6:
            self.DEC(MODE_ZERO_PAGE_X)
        elif opcode == 0xCE:
            self.DEC(MODE_ABSOLUTE)
        elif opcode == 0xDE:
            self.DEC(MODE_ABSOLUTE_X)
        elif opcode == 0xCA:
            self.DEX()
        elif opcode == 0x88:
            self.DEY()
        elif opcode == 0x0A:
            self.ASL_Acc()
        elif opcode == 0x06:
            self.ASL(MODE_ZERO_PAGE)
        elif opcode == 0x16:
            self.ASL(MODE_ZERO_PAGE_X)
        elif opcode == 0x0E:
            self.ASL(MODE_ABSOLUTE)
        elif opcode == 0x1E:
            self.ASL(MODE_ABSOLUTE_X)
        elif opcode == 0x4A:
            self.LSR_Acc()
        elif opcode == 0x46:
            self.LSR(MODE_ZERO_PAGE)
        elif opcode == 0x56:
            self.LSR(MODE_ZERO_PAGE_X)
        elif opcode == 0x4E:
            self.LSR(MODE_ABSOLUTE)
        elif opcode == 0x5E:
            self.LSR(MODE_ABSOLUTE_X)
        elif opcode == 0x2A:
            self.ROL_Acc()
        elif opcode == 0x26:
            self.ROL(MODE_ZERO_PAGE)
        elif opcode == 0x36:
            self.ROL(MODE_ZERO_PAGE_X)
        elif opcode == 0x2E:
            self.ROL(MODE_ABSOLUTE)
        elif opcode == 0x3E:
            self.ROL(MODE_ABSOLUTE_X)
        elif opcode == 0x6A:
            self.ROR_Acc()
        elif opcode == 0x66:
            self.ROR(MODE_ZERO_PAGE)
        elif opcode == 0x76:
            self.ROR(MODE_ZERO_PAGE_X)
        elif opcode == 0x6E:
            self.ROR(MODE_ABSOLUTE)
        elif opcode == 0x7E:
            self.ROR(MODE_ABSOLUTE_X)
        elif opcode == 0x4C:
            self.JMP(MODE_ABSOLUTE)
        elif opcode == 0x6C:
            self.JMP(MODE_INDIRECT)
        elif opcode == 0x20:
            self.JSR(MODE_ABSOLUTE)
        elif opcode == 0x60:
            self.RTS()
        elif opcode == 0x90:
            self.BCC()
        elif opcode == 0xB0:
            self.BCS()
        elif opcode == 0xF0:
            self.BEQ()
        elif opcode == 0x30:
            self.BMI()
        elif opcode == 0xD0:
            self.BNE()
        elif opcode == 0x10:
            self.BPL()
        elif opcode == 0x50:
            self.BVC()
        elif opcode == 0x70:
            self.BVS()
        elif opcode == 0x18:
            self.CLC()
        elif opcode == 0xD8:
            self.CLD()
        elif opcode == 0x58:
            self.CLI()
        elif opcode == 0xB8:
            self.CLV()
        elif opcode == 0x38:
            self.SEC()
        elif opcode == 0xF8:
            self.SED()
        elif opcode == 0x78:
            self.SEI()
        elif opcode == 0x00:
            self.BRK()
        elif opcode == 0x40:
            self.RTI()
        elif opcode == 0xEA:
            self.NOP()
        else:
            raise ValueError(
                f"Unsupported opcode ${opcode:02X} at "
                f"${(self.PC - 1) & 0xFFFF:04X}"
            )

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
