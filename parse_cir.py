"""Parse raw RTT CIR log files into HDF5 files of CIR magnitude profiles.

Each log file is named with its session and occupancy label (for example
"Session03_Label2.txt") and contains the 1016-tap Ipatov CIR for each frame,
one "real imag" pair per line. Lines that start with '#' are comments.
"""

import glob
import os
import re

import h5py
import numpy as np

IPATOV_TAPS = 1016


def parse_log(path):
    """Return an array of shape (frames, 1016) with the CIR magnitude per tap."""
    frames = []
    buf = []
    with open(path) as f:
        for line in f:
            if line.startswith('#'):
                continue
            m = re.findall(r'-?\d+', line)
            if len(m) >= 2:
                real, imag = int(m[0]), int(m[1])
                buf.append(complex(real, imag))
                if len(buf) == IPATOV_TAPS:
                    frames.append(np.abs(np.array(buf)))  # |h| = sqrt(I^2 + Q^2)
                    buf = []
    return np.array(frames, dtype=np.float32)


def main():
    os.makedirs('data_cir_full', exist_ok=True)
    for path in sorted(glob.glob(os.path.join('raw_cir_logs', '*.txt'))):
        name = os.path.basename(path)
        label = int(re.search(r'Label(\d)', name).group(1))
        mag = parse_log(path)
        out = os.path.join('data_cir_full', name.replace('.txt', '.h5'))
        with h5py.File(out, 'w') as hf:
            hf.create_dataset('cir_mag', data=mag)
            hf.attrs['label'] = label
        print(f"{name}: {mag.shape[0]} frames, label {label}")


if __name__ == '__main__':
    main()
