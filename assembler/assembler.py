from opcodes import (
    opcodes,
    MODE_IMMEDIATE, MODE_ZERO_PAGE, MODE_ZERO_PAGE_X, MODE_ZERO_PAGE_Y,
    MODE_ABSOLUTE, MODE_ABSOLUTE_X, MODE_ABSOLUTE_Y,
    MODE_INDIRECT_X, MODE_INDIRECT_Y, MODE_INDIRECT, MODE_ACCUMULATOR
)

class assembler: #outputs it in hex code must put through bus to be able to run it
    def __init__(self):
        self.symbols = {}
        self.PC = 0x0100

    def assemble(self, code): #does the thing
        lines = code.splitlines()
        machine_code = bytearray()
        current_address = self.PC
        pass1_cleaned = []
        for line in lines:
            line = line.split(';')[0].strip()
            if not line:
                continue
            if ':' in line:
                parts = line.split(':', 1)
                label = parts[0].strip()
                self.symbols[label] = current_address
                line = parts[1].strip()
                if not line:
                    continue
            pass1_cleaned.append((current_address, line))
            current_address += self._get_instruction_size(line)
        for address, line in pass1_cleaned:
            out = self._parse_instruction(line, address)
            machine_code.extend(out)
        return machine_code

    def _get_instruction_size(self, line): #finds the size of the instruction
        parts = line.split()
        pneumonic = parts[0].upper()
        branches = ("BCC", "BCS", "BEQ", "BMI", "BNE", "BPL", "BVC", "BVS")
        if pneumonic in branches:
            return 2
        if len(parts) == 1:
            return 1
        operand = parts[1]
        mode = self._infer_mode(operand)
        if mode in (MODE_IMMEDIATE, MODE_ZERO_PAGE, MODE_ZERO_PAGE_X, MODE_ZERO_PAGE_Y, MODE_INDIRECT_X, MODE_INDIRECT_Y):
            return 2
        elif mode in (MODE_ABSOLUTE, MODE_ABSOLUTE_X, MODE_ABSOLUTE_Y, MODE_INDIRECT):
            return 3
        return 2

    def _infer_mode(self, operand): #figures out mode coming through
        operand = operand.strip()
        if operand == "" or operand.upper() == "A":
            return MODE_ACCUMULATOR
        elif operand.startswith('#'):
            return MODE_IMMEDIATE
        elif operand.startswith('(') and operand.endswith(')'):
            if ',X' in operand.upper():
                return MODE_INDIRECT_X
            elif ',Y' in operand.upper():
                return MODE_INDIRECT_Y
            else:
                return MODE_INDIRECT
        elif ',' in operand:
            if ',X' in operand.upper():
                return MODE_ZERO_PAGE_X
            elif ',Y' in operand.upper():
                return MODE_ZERO_PAGE_Y
        else:
            try:
                val = int(operand, 0)
                if val <= 0xFF:
                    return MODE_ZERO_PAGE
                else:
                    return MODE_ABSOLUTE
            except ValueError:
                return MODE_ABSOLUTE
                
    def _parse_instruction(self, line,current_address): #pass the instruction
        parts = line.split(None, 1)
        pneumonic = parts[0].upper()
        operand = parts[1].strip() if len(parts) > 1 else ""
        branches = ("BCC", "BCS", "BEQ", "BMI", "BNE", "BPL", "BVC", "BVS")
        if pneumonic in branches:
            if not operand:
                raise ValueError(f"Branch instruction {pneumonic} requires a target label or address")
            clean_op = operand
            if clean_op in self.symbols:
                target_addr = self.symbols[clean_op]
            else:
                if clean_op.startswith('$'):
                    clean_op = '0x' + clean_op[1:]
                target_addr = int(clean_op, 0)
            offset = target_addr - (current_address + 2)
            if not (-128 <= offset <= 127):
                raise ValueError(f"Branch target out of range (-128 to 127 bytes): {offset}")
            if pneumonic not in opcodes:
                raise ValueError(f"Unknown branch opcode: {pneumonic}")
            return [opcodes[pneumonic], offset & 0xFF]
        if not operand or operand.upper() == "A":
            if pneumonic in ("ASL", "LSR", "ROL", "ROR") and operand.upper == "A":
                key = (pneumonic, MODE_ACCUMULATOR)
            else:
                key = pneumonic
            if key in opcodes:
                return [opcodes[key]]
            else:
                raise ValueError(f"unknown instruction: {pneumonic}")
        mode = self._infer_mode(operand)
        clean_op = operand
        if clean_op.startswith('#'):
            clean_op = clean_op[1:]
        if clean_op.startswith('('):
            clean_op = clean_op.strip('()')
        if ',X' in clean_op.upper():
            clean_op = clean_op.upper().replace(',X', '').strip()
        elif ',Y' in clean_op.upper():
            clean_op = clean_op.upper().replace(',Y', '').strip()
        try:
            if clean_op in self.symbols:
                val = self.symbols[clean_op]
            else:
                if clean_op.startswith('$'):
                    clean_op = '0x' + clean_op[1:]
                val = int(clean_op, 0)
        except ValueError:
            raise ValueError(f"Undefined symbol or invalid operand: {operand}")
        key = (pneumonic, mode)
        if key not in opcodes:
            raise ValueError(f"Unsupported instruction/mode combination: {pneumonic} with mode {mode}")
        opcode = opcodes[key]
        result = [opcode]
        if mode in (MODE_IMMEDIATE, MODE_ZERO_PAGE, MODE_ZERO_PAGE_X, MODE_ZERO_PAGE_Y, MODE_INDIRECT_X, MODE_INDIRECT_Y):
            result.append(val & 0xFF)
        elif mode in (MODE_ABSOLUTE, MODE_ABSOLUTE_X, MODE_ABSOLUTE_Y, MODE_INDIRECT):
            result.append(val & 0xFF)
            result.append((val >> 8) & 0xFF)
        return result
