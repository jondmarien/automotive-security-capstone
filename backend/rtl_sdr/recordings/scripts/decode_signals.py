import re

INPUT_FILE = "../signals/analyze/all_bursts.txt"
OUTPUT_FILE = "../signals/analyze/decoded_signals.txt"

# Helper to convert binary string to hex string
def bin_to_hex(bin_str):
    # Remove spaces and pad to multiple of 8
    bits = bin_str.replace(' ', '')
    if len(bits) % 8 != 0:
        bits = bits.ljust((len(bits) // 8 + 1) * 8, '0')
    hex_bytes = [f"{int(bits[i:i+8], 2):02x}" for i in range(0, len(bits), 8)]
    return ' '.join(hex_bytes)

# Helper to convert binary string to ASCII (printable, else '.')
def bin_to_ascii(bin_str):
    bits = bin_str.replace(' ', '')
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8:
            byte = byte.ljust(8, '0')
        val = int(byte, 2)
        if 32 <= val <= 126:
            chars.append(chr(val))
        else:
            chars.append('.')
    return ''.join(chars)

# Read all bursts
with open(INPUT_FILE, "r") as f:
    content = f.read()

# Find all bursts with their headers and binary data
pattern = re.compile(r"=+\nBurst (\d+)\nLength: (\d+) bits\nPause after: (\d+) samples\n-+\n([01 ]+)\n", re.MULTILINE)
results = pattern.findall(content)

# Filter only odd-numbered bursts
odd_bursts = [(int(num), int(length), int(pause), data.replace('\n', ' '))
              for num, length, pause, data in results if int(num) % 2 == 1]

with open(OUTPUT_FILE, "w") as out:
    for num, length, pause, data in odd_bursts:
        out.write("="*30 + "\n")
        out.write(f"Burst {num}\n")
        out.write(f"Length: {length} bits\n")
        out.write(f"Pause after: {pause} samples\n")
        out.write("-"*24 + "\n")
        out.write(f"Binary:   {data.strip()}\n")
        out.write(f"Hex:      {bin_to_hex(data)}\n")
        out.write(f"ASCII:    {bin_to_ascii(data)}\n\n")

print(f"Decoded {len(odd_bursts)} bursts to {OUTPUT_FILE}.") 