import numpy as np
import scipy.io.wavfile as wavfile

# Read the WAV file
sample_rate, data = wavfile.read('../signals/baseband_434000000Hz_16-18-05_11-06-2025.wav')

# If stereo (I/Q channels), separate them
if len(data.shape) == 2:
    I = data[:, 0]  # Left channel = I
    Q = data[:, 1]  # Right channel = Q
else:
    # If mono, you'll need to process differently
    print("Mono WAV - may need different processing")

# Create complex IQ samples
iq_samples = I + 1j * Q

# Convert to desired format and save
# Option 1: Save as complex64 (32-bit float IQ)
iq_samples = iq_samples.astype(np.complex64)
iq_samples.tofile('../signals/output.iq')