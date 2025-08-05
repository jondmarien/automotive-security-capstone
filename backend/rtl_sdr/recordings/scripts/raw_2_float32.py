import numpy as np

# Adjust these as needed
RAW_FILE = "../signals/output.raw"
IQ_FILE = "../signals/output_urh.iq"

# Read raw int16 data (I/Q interleaved)
data = np.fromfile(RAW_FILE, dtype=np.float32)

# Reshape to (N, 2) for I and Q
iq = data.reshape(-1, 2)
i = iq[:, 0].astype(np.float32)
q = iq[:, 1].astype(np.float32)

# Normalize to [-1, 1] (optional, but recommended)
i /= 32768.0
q /= 32768.0

# Create complex float32 array
iq_complex = i + 1j * q

# Save as complex64 (float32) for URH
iq_complex.astype(np.complex64).tofile(IQ_FILE)
