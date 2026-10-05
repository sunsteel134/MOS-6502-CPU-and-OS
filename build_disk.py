import os
from assembler.assembler import assembler

DISK_NAME = "virtual_disk.bin"
SECTOR_SIZE = 256
LOAD_ADDR = 0x2100

GAMES = [
    {"name": "snake", "file": "snake.asm", "start_sector": 2, "max_sectors": 4},
    {"name": "pong", "file": "pong.asm", "start_sector": 6, "max_sectors": 4},
    {"name": "rogue", "file": "rogue.asm", "start_sector": 10, "max_sectors": 6},
]

if not os.path.exists(DISK_NAME):
    with open(DISK_NAME, "wb") as f:
        f.write(b"\x00" * (256 * SECTOR_SIZE))

with open(DISK_NAME, "r+b") as f:
    for game in GAMES:
        if not os.path.exists(game["file"]):
            print(f"Skipping {game['name']}: file {game['file']} not found.")
            continue
        asm = assembler()
        asm.PC = LOAD_ADDR
        with open(game["file"], "r") as gf:
            code = bytes(asm.assemble(gf.read()))
        sectors_needed = -(-len(code) // SECTOR_SIZE)
        if sectors_needed > game["max_sectors"]:
            raise SystemExit(
                f"Error: {game['name']} is {len(code)} bytes ({sectors_needed} sectors) "
                f"but max allowed is {game['max_sectors']} sectors."
            )
        f.seek(game["start_sector"] * SECTOR_SIZE)
        padding = b"\x00" * (game["max_sectors"] * SECTOR_SIZE - len(code))
        f.write(code + padding)
        print(f"Wrote {game['name']}: {len(code)} bytes at sector {game['start_sector']} ({sectors_needed} sector(s))")
