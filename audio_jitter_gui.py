import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import tkinter as tk
from tkinter import filedialog

# Preset jitter values (standard deviation in seconds)
PRESETS = {
    "High-End DAC": 1e-7,
    "Consumer Grade": 1e-6,
    "Vintage Gear": 5e-6
}

def apply_jitter(samples, sr, jitter_std):
    time = np.arange(len(samples)) / sr
    jitter = np.random.normal(0, jitter_std, size=len(samples))
    jittered_time = time + jitter
    interpolator = interp1d(time, samples, kind='cubic', fill_value="extrapolate")
    return interpolator(jittered_time)

def process_file(file_path, jitter_std):
    data, sr = sf.read(file_path)
    original_info = sf.info(file_path)
    output_file = file_path.replace(".wav", f"_jittered.wav")

    # Check if input is mono or stereo
    if data.ndim == 1:
        # Mono signal
        output = apply_jitter(data, sr, jitter_std)
    elif data.ndim == 2 and data.shape[1] == 2:
        # Stereo signal
        left = apply_jitter(data[:, 0], sr, jitter_std)
        right = apply_jitter(data[:, 1], sr, jitter_std)
        output = np.column_stack((left, right))
    else:
        raise ValueError("Unsupported audio format (more than 2 channels?)")

    sf.write(output_file, output, sr, subtype=original_info.subtype)
    print(f"Saved jittered file to: {output_file}")

def launch_gui():
    def browse_file():
        filename = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if filename:
            file_entry.delete(0, tk.END)
            file_entry.insert(0, filename)

    def run_simulation():
        file_path = file_entry.get()
        preset_name = preset_var.get()
        jitter_std = PRESETS[preset_name] * float(jitter_scale.get())
        process_file(file_path, jitter_std)

    root = tk.Tk()
    root.title("Audio Jitter Simulator")

    tk.Label(root, text="WAV file:").grid(row=0, column=0)
    file_entry = tk.Entry(root, width=40)
    file_entry.grid(row=0, column=1)
    tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2)

    tk.Label(root, text="Hardware Preset:").grid(row=1, column=0)
    preset_var = tk.StringVar(value="Consumer Grade")
    tk.OptionMenu(root, preset_var, *PRESETS.keys()).grid(row=1, column=1)

    tk.Label(root, text="Jitter Multiplier:").grid(row=2, column=0)
    jitter_scale = tk.Scale(root, from_=0.5, to=5.0, resolution=0.1,
                            orient=tk.HORIZONTAL)
    jitter_scale.set(1.0)
    jitter_scale.grid(row=2, column=1)

    tk.Button(root, text="Apply Jitter", command=run_simulation).grid(row=3, column=1)

    root.mainloop()

launch_gui()