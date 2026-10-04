import os
from assembler.assembler import assembler

disk = "virtual_disk.bin"
sector_size = 256
game_sector = 2
max = 4
load_addr = 0x2100

asm = assembler()
asm.PC = load_addr
with open("snake.asm", "r") as f:
    code = bytes(asm.assemble(f.read()))
sectors = -(-len(code) // sector_size)
if sectors > max:
    raise SystemExit(f"snake is {len(code)} bytes ({sectors} sectors) but G only loads {max}")
if not os.path.exists(disk):
    with open(disk, "wb") as f:
        f.write(b"\x00" * (256 * sector_size))
with open(disk, "r+b") as f:
    f.seek(game_sector * sector_size)
    f.write(code + b"\x00" * (max * sector_size - len(code)))
print(f"snake: {len(code)} bytes written to {disk} at sector {game_sector} ({sectors} sector(s) used)")
