import sys
import select

class keyboard:
    def __init__(self, base_address=0x0200):
        self.base_address = base_address
        self.buffer = []
        self.last_key = 0x00

    def contains(self, address): #check if address is in range
        return self.base_address <= address < self.base_address + 2

    def read(self, address): #looks at what keyboards doing
        offset = address - self.base_address
        if offset == 0:
            if self.buffer:
                self.last_key = self.buffer.pop(0)
                return self.last_key
            else:
                return 0x00
        elif offset == 1:
            return 0x01 if self.buffer else 0x00
        return 0x00

    def write(self, address, value): #cant to its read only info
        pass

    def poll(self): #looks for input
        try:
            if sys.platform != 'win32':
                if select.select([sys.stdin], [], [], 0)[0]:
                    char = sys.stdin.read(1)
                    if char:
                        keycode = ord(char) & 0xFF
                        self.buffer.append(keycode)
        except:
            pass

    def press_key(self, keycode): #press a key
        self.buffer.append(keycode & 0xFF)

    def get_last_key(self): #looks for thing last clicked
        return self.last_key

    def is_key_available(self): #checks if a key is waiting to be read
        return len(self.buffer) > 0

    def clear_buffer(self): #clears buffer (just look at the function name)
        self.buffer.clear()
