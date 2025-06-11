import re
from collections import defaultdict

INPUT_FILE = "../signals/analyze/decoded_signals.txt"
OUTPUT_FILE = "../signals/analyze/field_alignment_table.txt"

# Parse decoded_signals.txt for bursts and their hex data
with open(INPUT_FILE, "r") as f:
    lines = f.readlines()

bursts = []
for line in lines:
    if line.startswith("Hex:"):
        hex_bytes = line.split(":", 1)[1].strip().split()
        bursts.append(hex_bytes)

# Find the max burst length
max_len = max(len(b) for b in bursts)

# Pad bursts to max length
for b in bursts:
    while len(b) < max_len:
        b.append("  ")  # pad with spaces for alignment

# Transpose to get columns
columns = list(zip(*bursts))

# Find invariant columns
invariant_cols = []
for i, col in enumerate(columns):
    values = set(x.strip() for x in col if x.strip())
    if len(values) == 1:
        invariant_cols.append(i)

# Write the table
with open(OUTPUT_FILE, "w") as out:
    # Header
    out.write("Burst | " + " ".join(f"{i:>2}" for i in range(max_len)) + "\n")
    out.write("-" * (7 + 3 * max_len) + "\n")
    for idx, b in enumerate(bursts):
        out.write(f"{idx+1:>5} | ")
        for i, byte in enumerate(b):
            mark = "*" if i in invariant_cols and byte.strip() else " "
            out.write(f"{byte}{mark} ")
        out.write("\n")
    out.write("\nInvariant columns (potential constant fields):\n")
    if invariant_cols:
        out.write(", ".join(str(i) for i in invariant_cols) + "\n")
    else:
        out.write("None found.\n")
    out.write("\n* Columns marked with * are invariant across all bursts.\n") 