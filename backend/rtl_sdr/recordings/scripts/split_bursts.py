import re

INPUT_FILE = "../signals/analyze/binary_output.txt"
OUTPUT_FILE = "../signals/analyze/all_bursts.txt"

# Read the input file
with open(INPUT_FILE, "r") as f:
    data = f.read()

# Find all bursts and their pause durations
pattern = re.compile(r"([01]+) \[Pause: (\d+) samples\]")
matches = pattern.findall(data)

bursts = []
pause_durations = []
for burst, pause in matches:
    bursts.append(burst)
    pause_durations.append(int(pause))

# Calculate summary stats
num_bursts = len(bursts)
avg_length = sum(len(b) for b in bursts) / num_bursts if num_bursts else 0


# Helper to format bits into bytes and wrap lines
def format_bits(bits, group=8, line_bytes=32):
    grouped = [bits[i : i + group] for i in range(0, len(bits), group)]
    lines = [
        " ".join(grouped[i : i + line_bytes])
        for i in range(0, len(grouped), line_bytes)
    ]
    return "\n".join(lines)


# Write all bursts to a single file with enhanced formatting
with open(OUTPUT_FILE, "w") as out:
    out.write(f"Total bursts: {num_bursts}\n")
    out.write(f"Average burst length: {avg_length:.2f} bits\n\n")
    for i, (burst, pause) in enumerate(zip(bursts, pause_durations)):
        out.write("=" * 30 + "\n")
        out.write(f"Burst {i + 1}\n")
        out.write(f"Length: {len(burst)} bits\n")
        out.write(f"Pause after: {pause} samples\n")
        out.write("-" * 24 + "\n")
        out.write(format_bits(burst) + "\n")
        out.write("\n")

print(f"Extracted {num_bursts} bursts to {OUTPUT_FILE}.")
