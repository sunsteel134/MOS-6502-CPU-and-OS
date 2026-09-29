class disk_controller:
    def __init__(self, base_address=0x0320, disk_filename="virtual_disk.bin"):
        self.base_address = base_address
        self.disk_filename = disk_filename
        self.sector = 0
        self.buf_addr = 0x0000
        self.status = 0
        self.sector_size = 256
        try:
            with open(self.disk_filename, "rb") as f:
                pass
        except FileNotFoundError:
            with open(self.disk_filename, "wb") as f:
                f.write(b'\x00' * (256 * 256))

    def contains(self, address):
        return self.base_address <= address < self.base_address + 8

    def read(self, address):
        offset = address - self.base_address
        if offset == 0x01:
            return self.sector
        elif offset == 0x02:
            return self.buf_addr & 0xFF
        elif offset == 0x03:
            return (self.buf_addr >> 8) & 0xFF
        elif offset == 0x04:
            return self.status
        return 0x00

    def write(self, address, value):
        offset = address - self.base_address
        if offset == 0x01:
            self.sector = value
        elif offset == 0x02:
            self.buf_addr = (self.buf_addr & 0xFF00) | value
        elif offset == 0x03:
            self.buf_addr = (self.buf_addr & 0x00FF) | (value << 8)
        elif offset == 0x00:
            if value == 1:
                self._read_sector()
            elif value == 2:
                self._write_sector()

    def attach_bus(self, bus): #attaches the bus to it (the bus just checks whats actually there)
        self.bus = bus

    def _read_sector(self): #read a file
        with open(self.disk_filename, "rb") as f:
            f.seek(self.sector * self.sector_size)
            data = f.read(self.sector_size)
            for i, byte in enumerate(data):
                self.bus.write(self.buf_addr + i, byte)
        self.status = 0

    def _write_sector(self): #write to a file
        data = bytearray(self.sector_size)
        for i in range(self.sector_size):
            data[i] = self.bus.read(self.buf_addr + i)
        with open(self.disk_filename, "r+b") as f:
            f.seek(self.sector * self.sector_size)
            f.write(data)
        self.status = 0
