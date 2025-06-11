import re
from collections import Counter

INPUT_FILE = "../signals/analyze/decoded_signals.txt"
OUTPUT_FILE = "../signals/analyze/extracted_fields.txt"

# Default field lengths (in bytes)
FIELD_LAYOUT = [
    ("Preamble", 2),
    ("Device ID", 2),
    ("Rolling Code", 2),
    ("Command", 1),
    ("Checksum/CRC", 1),
]

# Helper to split hex string into fields
def split_fields(hex_bytes):
    fields = {}
    idx = 0
    for name, length in FIELD_LAYOUT:
        fields[name] = hex_bytes[idx:idx+length]
        idx += length
    fields["Unknown"] = hex_bytes[idx:]
    return fields

# Helper to pretty-print a field row
def field_row(name, value):
    return f"| {name:<12} | {value:<24} |"

# Helper to join bytes for display
def join_bytes(byte_list):
    return ' '.join(byte_list) if byte_list else ''

# Parse decoded_signals.txt for bursts and their hex data
with open(INPUT_FILE, "r") as f:
    lines = f.readlines()

bursts = []
current = {}
for line in lines:
    if line.startswith("Burst "):
        if current:
            bursts.append(current)
        current = {"header": line.strip()}
    elif line.startswith("Hex:"):
        hex_bytes = line.split(":", 1)[1].strip().split()
        current["hex_bytes"] = hex_bytes
    elif line.startswith("Length:") or line.startswith("Pause after:"):
        current.setdefault("meta", []).append(line.strip())
if current:
    bursts.append(current)

# Extract fields for each burst
all_field_values = {name: [] for name, _ in FIELD_LAYOUT}
with open(OUTPUT_FILE, "w") as out:
    for i, burst in enumerate(bursts):
        meta = burst.get("meta", [])
        out.write(f"{burst['header']}\n")
        for m in meta:
            out.write(f"{m}\n")
        out.write("+--------------+--------------------------+\n")
        out.write("| Field        | Value                    |\n")
        out.write("+--------------+--------------------------+\n")
        fields = split_fields(burst.get("hex_bytes", []))
        for name, _ in FIELD_LAYOUT:
            value = join_bytes(fields[name])
            all_field_values[name].append(value)
            out.write(field_row(name, value) + "\n")
        out.write(field_row("Unknown", join_bytes(fields["Unknown"])) + "\n")
        out.write("+--------------+--------------------------+\n\n")

    # --- Summary Section ---
    out.write("\n" + "="*40 + "\n")
    out.write("Summary of Field Analysis\n")
    out.write("="*40 + "\n")
    total_bursts = len(bursts)
    for name in all_field_values:
        values = all_field_values[name]
        counter = Counter(values)
        most_common, count = counter.most_common(1)[0] if counter else (None, 0)
        confidence = (count / total_bursts) * 100 if total_bursts else 0
        if most_common and confidence > 50:
            out.write(f"Most likely {name}: {most_common} (Confidence: {confidence:.1f}%)\n")
        elif most_common:
            out.write(f"No clear {name}. Most common: {most_common} (Confidence: {confidence:.1f}%)\n")
        else:
            out.write(f"No data for {name}.\n")
    out.write("\n")
    out.write("Confidence is the percentage of bursts with the most common value. If no value exceeds 50%, the result is uncertain.\n")

print(f"Extracted fields for {len(bursts)} bursts to {OUTPUT_FILE}.") 