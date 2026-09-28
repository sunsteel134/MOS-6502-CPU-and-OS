class text_display:
    def __init__(self, base_address=0x0400, cols=40, rows=25):
        self.base_address = base_address
        self.cols = cols
        self.rows = rows
        self.vram_size = cols * rows #video ram dont think its virtual memory (thats for me im an idiot not for the person reading)
        self.vram = bytearray(self.vram_size)
        self.cursor_x = 0
        self.cursor_y = 0
        self.dirty = True

    def contains(self, address): #checks if data is within range
        return self.base_address <= address < self.base_address + self.vram_size

    def read(self, address): #reads it (im not putting this goddamn comment anymore)
        offset = address - self.base_address
        if 0 <= offset < self.vram_size:
            return self.vram[offset]
        return 0x00

    def write(self, address, value): #writes to the data (im not gonna keep writing this either)
        offset = address - self.base_address
        if 0 <= offset < self.vram_size:
            if self.vram[offset] != value:
                self.dirty = True
            self.vram[offset] = value & 0xFF

    def render(self): #display stuff
        if not self.dirty:
            return
        print("\033[H", end='')
        for row in range(self.rows):
            line_start = row * self.cols
            line_end = line_start + self.cols
            line_bytes = bytes(self.vram[line_start:line_end])
            try:
                line = line_bytes.decode('ascii', errors='replace')
            except:
                line = str(line_bytes)
            print(line)
        self.dirty = False

    def clear(self): #get rid of spaces
        for i in range(self.vram_size):
            self.vram[i] = 0x20
        self.cursor_x = 0
        self.cursor_y = 0
        self.dirty = True

    def put_char(self, char_code): #put character where the cursor is
        if char_code == 0x0D:
            self.cursor_x = 0
            return
        elif char_code == 0x0A:
            self.cursor_y += 1
            if self.cursor_y >= self.rows:
                self.cursor_y = 0
            return
        elif char_code == 0x08:
            if self.cursor_x > 0:
                self.cursor_x -= 1
                offset = self.cursor_y * self.cols + self.cursor_x
                self.vram[offset] = 0x20
            return
        offset = self.cursor_y * self.cols + self.cursor_x
        self.vram[offset] = char_code & 0x7F
        self.dirty = True
        self.cursor_x += 1
        if self.cursor_x >= self.cols:
            self.cursor_x = 0
            self.cursor_y += 1
            if self.cursor_y >= self.rows:
                self.cursor_y = 0

    def set_cursor(self, x, y): #move the cursor somewhere
        self.cursor_x = x % self.cols
        self.cursor_y = y % self.rows

    def get_string(self, x, y, length): #get the string
        start = y * self.cols + x
        end = start + length
        return bytes(self.vram[start:end]).decode('ascii', errors='replace')
