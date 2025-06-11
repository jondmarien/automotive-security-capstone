import re
from collections import Counter, defaultdict
from itertools import combinations

INPUT_FILE = "../signals/analyze/decoded_signals.txt"
ANALYZE_DIR = "../signals/analyze/"

# Helper to read bursts as lists of hex bytes and bits
def read_bursts():
    with open(INPUT_FILE, "r") as f:
        lines = f.readlines()
    bursts_hex = []
    bursts_bin = []
    for line in lines:
        if line.startswith("Hex:"):
            hex_bytes = line.split(":", 1)[1].strip().split()
            bursts_hex.append(hex_bytes)
        if line.startswith("Binary:"):
            bin_bytes = line.split(":", 1)[1].strip().split()
            bursts_bin.append(bin_bytes)
    return bursts_hex, bursts_bin

bursts_hex, bursts_bin = read_bursts()
max_len = max(len(b) for b in bursts_hex)
num_bursts = len(bursts_hex)

# Pad bursts to max length
for b in bursts_hex:
    while len(b) < max_len:
        b.append("")

# 1. Byte-shifted alignment search
with open(ANALYZE_DIR + "byte_shift_alignment.txt", "w") as out:
    out.write("# Byte-Shifted Alignment Search\n")
    for shift in range(max_len):
        out.write(f"\n## Shift: {shift} bytes\n")
        shifted = [b[shift:] + b[:shift] for b in bursts_hex]
        columns = list(zip(*shifted))
        invariant_cols = [i for i, col in enumerate(columns) if len(set(x for x in col if x)) == 1]
        out.write("Burst | " + " ".join(f"{i:>2}" for i in range(max_len)) + "\n")
        out.write("-" * (7 + 3 * max_len) + "\n")
        for idx, b in enumerate(shifted):
            out.write(f"{idx+1:>5} | ")
            for i, byte in enumerate(b):
                mark = "*" if i in invariant_cols and byte else " "
                out.write(f"{byte}{mark} ")
            out.write("\n")
        out.write("Invariant columns: " + (", ".join(str(i) for i in invariant_cols) if invariant_cols else "None") + "\n")

# 2. Partial invariance (majority rule)
with open(ANALYZE_DIR + "partial_invariance.txt", "w") as out:
    out.write("# Partial Invariance (Majority Rule >70%)\n")
    columns = list(zip(*bursts_hex))
    majority_cols = []
    for i, col in enumerate(columns):
        counter = Counter(x for x in col if x)
        if counter:
            most_common, count = counter.most_common(1)[0]
            if count / num_bursts > 0.7:
                majority_cols.append((i, most_common, count / num_bursts))
    out.write("Burst | " + " ".join(f"{i:>2}" for i in range(max_len)) + "\n")
    out.write("-" * (7 + 3 * max_len) + "\n")
    for idx, b in enumerate(bursts_hex):
        out.write(f"{idx+1:>5} | ")
        for i, byte in enumerate(b):
            mark = "#" if any(i == col[0] for col in majority_cols) and byte else " "
            out.write(f"{byte}{mark} ")
        out.write("\n")
    out.write("\nColumns with >70% same value:\n")
    for i, val, frac in majority_cols:
        out.write(f"Col {i}: {val} ({frac*100:.1f}%)\n")
    if not majority_cols:
        out.write("None found.\n")
    out.write("\n# Columns marked with # are mostly invariant (>70%).\n")

# 3. Pairwise similarity/clustering (byte-wise)
def hamming_distance(a, b):
    return sum(x != y for x, y in zip(a, b)) + abs(len(a) - len(b))

clusters = defaultdict(list)
used = set()
threshold = 2  # max byte difference for clustering
for i, burst in enumerate(bursts_hex):
    if i in used:
        continue
    cluster = [i]
    used.add(i)
    for j in range(i+1, len(bursts_hex)):
        if j not in used and hamming_distance(burst, bursts_hex[j]) <= threshold:
            cluster.append(j)
            used.add(j)
    clusters[i] = cluster
with open(ANALYZE_DIR + "pairwise_clusters.txt", "w") as out:
    out.write("# Pairwise Similarity Clustering (byte-wise, threshold=2)\n")
    for leader, members in clusters.items():
        out.write(f"Cluster led by Burst {leader+1}: {', '.join(str(m+1) for m in members)}\n")
    out.write(f"\nTotal clusters: {len(clusters)}\n")

# 4. Bit-level invariance
bit_bursts = []
for b in bursts_hex:
    bits = ''.join(f"{int(x,16):08b}" if x else '00000000' for x in b)
    bit_bursts.append(bits)
max_bits = max(len(bits) for bits in bit_bursts)
for i in range(len(bit_bursts)):
    if len(bit_bursts[i]) < max_bits:
        bit_bursts[i] += '0' * (max_bits - len(bit_bursts[i]))
with open(ANALYZE_DIR + "bit_level_invariance.txt", "w") as out:
    out.write("# Bit-Level Invariance Analysis\n")
    invariant_bits = []
    for i in range(max_bits):
        col = [bits[i] for bits in bit_bursts]
        if all(b == col[0] for b in col):
            invariant_bits.append(i)
    # Print a table (first 64 bits for brevity)
    out.write("Burst | " + " ".join(f"{i:>2}" for i in range(min(64, max_bits))) + (" ..." if max_bits > 64 else "") + "\n")
    out.write("-" * (7 + 3 * min(64, max_bits)) + ("..." if max_bits > 64 else "") + "\n")
    for idx, bits in enumerate(bit_bursts):
        out.write(f"{idx+1:>5} | ")
        for i in range(min(64, max_bits)):
            mark = "*" if i in invariant_bits else " "
            out.write(f"{bits[i]}{mark} ")
        if max_bits > 64:
            out.write("...")
        out.write("\n")
    out.write(f"\nInvariant bit positions: {', '.join(str(i) for i in invariant_bits) if invariant_bits else 'None'}\n")
    out.write("\n* Bits marked with * are invariant across all bursts.\n") 