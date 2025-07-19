# Burst Analysis Session – 2024-06-13

## Session Goals
- Capture and analyze BMW key fob RF bursts using SDR
- Extract and decode bursts into binary, hex, and human-readable formats
- Attempt to identify the Device ID and other protocol fields
- Summarize findings and plan next steps for protocol reverse engineering

## Scripts and Methods Used
- **Burst Splitting:**
  - Script to split raw binary output into individual bursts using pause delimiters
  - Enhanced to output all bursts in a single, well-formatted file with headers and statistics
- **Decoding:**
  - Script to extract only the likely signal bursts (odd-numbered, short bursts)
  - Output in binary, hex, and ASCII for each burst
- **Field Extraction:**
  - Script to split each burst into fields: Preamble, Device ID, Rolling Code, Command, Checksum/CRC, Unknown
  - Pretty-printed tables for each burst in `extracted_fields.txt`
  - Added summary section with most common value and confidence for each field

## Key Findings
- **No clear Device ID or other field:**
  - The most common value for each field appeared in only ~4.8%–11.9% of bursts
  - No field had a dominant, invariant value across all bursts
- **Possible causes:**
  - Field boundaries may not match the actual protocol
  - Device ID may be obfuscated, encrypted, or not in a fixed position
  - Some bursts may be noise or not true key fob signals

## Field Analysis Summary
```
No clear Preamble. Most common: ea f5 (Confidence: 4.8%)
No clear Device ID. Most common: ab d5 (Confidence: 4.8%)
No clear Rolling Code. Most common: 7a be (Confidence: 4.8%)
No clear Command. Most common: d5 (Confidence: 9.5%)
No clear Checksum/CRC. Most common: fa (Confidence: 11.9%)
```

## Recommendations & Next Steps
- **Capture more clean, single-press bursts** to reduce noise
- **Use URH to visually align bursts** and look for constant bytes
- **Try shifting field boundaries** in extraction scripts to see if a constant value emerges
- **Research protocol-specific details** (BMW key fob, FSK, Manchester encoding, etc.)
- **Compare with online reverse engineering efforts** ([example 1](https://0x44.cc/radio/2024/03/13/reversing-a-car-key-fob-signal.html), [example 2](https://github.com/rewindfreakshaw/SDR-Key-FOB-Hacking))
- **Automate field alignment analysis** to highlight invariant bytes

## Field Alignment Visualization
- **Purpose:** To spot which bytes are constant across all bursts (potential Device ID)
- **Method:**
  - Create a table where each row is a burst and each column is a byte position
  - Highlight columns with the same value in all (or most) bursts
- **Example:**
```
Burst |  0   1   2   3   4   5   6   7
-----------------------------------------
  1   | ff  e3  e5  fc  7f  bf  eb  fc
  2   | ef  57  aa  f5  7a  be  b7  af
  3   | ea  f5  75  7a  bd  4f  4b  ea
  ...
```
- **Next:** Consider writing a script to generate this table and highlight constant columns

## Issues Encountered
- **Git push error:** HTTP 408 timeout, likely due to large files or network issues
- **No clear Device ID found:** May require more data or protocol-specific decoding

## Conclusion
- The current approach provides a strong foundation for further analysis
- Next steps should focus on burst alignment, field boundary experimentation, and protocol research
- Document and automate findings for reproducibility and future work 