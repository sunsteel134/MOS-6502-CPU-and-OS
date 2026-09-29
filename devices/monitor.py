import tkinter as tk

class monitor:
    def __init__(self, bus, on_key=None, base_address=0x0400, width_chars=40, height_chars=25):
        self.bus = bus
        self.base_address = base_address
        self.cols = width_chars
        self.rows = height_chars
        self.size = self.cols * self.rows
        self.vram = bytearray(self.size)
        if hasattr(self.bus, "attach"):
            self.bus.attach(self)
        self.on_key = on_key
        self.root = tk.Tk()
        self.root.title("MOCOS Display Monitor")
        self.root.configure(bg="#050505")
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(
            self.root,
            width=self.cols * 16,
            height=self.rows * 20,
            bg="#101010",
            highlightthickness=2,
            highlightbackground="#222222"
        )
        self.canvas.pack(padx=10, pady=10)
        self.grid = []
        for r in range(self.rows):
            row_ids = []
            for c in range(self.cols):
                x = c * 16 + 8
                y = r * 20 + 10
                text_id = self.canvas.create_text(
                    x, y,
                    text=" ",
                    fill="#00FF66",
                    font=("Courier", 14, "bold")
                )
                row_ids.append(text_id)
            self.grid.append(row_ids)
        self.root.bind("<Key>", self._on_key)
        self.canvas.bind("<Button-1>", lambda e: self.canvas.focus_set())
        self.root.focus_force()

    def contains(self, address):
        return self.base_address <= address < (self.base_address + self.size)

    def read(self, address):
        offset = address - self.base_address
        return self.vram[offset]

    def write(self, address, value):
        offset = address - self.base_address
        self.vram[offset] = value & 0xFF

    def _on_key(self, event): #writes the character you press to the RAM
        if event.keysym == "Return":
            key_ascii = 0x0D
        elif event.keysym == "BackSpace":
            key_ascii = 0x08
        elif event.char:
            key_ascii = ord(event.char.upper())
        else:
            return
        if self.on_key:
            self.on_key(key_ascii)

    def render(self): #renders things (duh)
        for row in range(self.rows):
            for col in range(self.cols):
                addr = self.base_address + (row * self.cols) + col
                val = self.bus.read(addr)
                char_str = chr(val) if 32 <= val <= 126 else " "
                self.canvas.itemconfig(self.grid[row][col], text=char_str)

    def show(self): #actually starts it
        self.root.update()
