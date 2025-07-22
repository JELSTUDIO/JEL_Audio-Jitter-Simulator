SCRIPT_VERSION = "1.6.0"

import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import tkinter as tk
from tkinter import filedialog
import os

# Preset jitter values (standard deviation in seconds)
PRESETS = {
    "High-End DAC": 1e-7,
    "Consumer Grade": 1e-6,
    "Vintage Gear": 5e-6,
    "Manual": None  # Special case
}

INTERPOLATION_METHODS = ["nearest", "linear", "slinear", "quadratic", "cubic", "zero"]

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None

        widget.bind("<Enter>", self.schedule)
        widget.bind("<Leave>", self.unschedule)

    def schedule(self, event=None):
        self.unschedule()
        self.id = self.widget.after(500, self.show_tooltip)

    def unschedule(self, event=None):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
        self.hide_tooltip()

    def show_tooltip(self):
        if self.tipwindow or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=4)

    def hide_tooltip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def apply_jitter(samples, sr, jitter_std, method='cubic'):
    time = np.arange(len(samples)) / sr
    jitter = np.random.normal(0, jitter_std, size=len(samples))
    jittered_time = time + jitter
    interpolator = interp1d(time, samples, kind=method, fill_value="extrapolate")
    return interpolator(jittered_time), jitter

def process_file(file_path, jitter_std, method):
    data, sr = sf.read(file_path)
    original_info = sf.info(file_path)
    output_file = file_path.replace(".wav", f"_jittered.wav")

    # Check if input is mono or stereo
    if data.ndim == 1:
        # Mono signal
        output, jitter = apply_jitter(data, sr, jitter_std, method)
        original = data
        jittered = output
    elif data.ndim == 2 and data.shape[1] == 2:
        # Stereo signal
        left, jitter = apply_jitter(data[:, 0], sr, jitter_std, method)
        right, jitter_right = apply_jitter(data[:, 1], sr, jitter_std, method)

        # Ensure both channels match in length
        if len(left) != len(right):
            max_len = max(len(left), len(right))
            left = np.pad(left, [(0, max_len - len(left))], mode='edge')
            right = np.pad(right, [(0, max_len - len(right))], mode='edge')

        output = np.column_stack((left, right))
        original = data[:, 0]  # preview just left channel
        jittered = output[:, 0]
    else:
        raise ValueError("Unsupported audio format (more than 2 channels?)")

    sf.write(output_file, output, sr, subtype=original_info.subtype)
    print(f"Saved jittered file to: {output_file}")

    # NEW: Save visuals
    plot_waveform_comparison(original, jittered, sr, method, output_file)
    plot_spectrogram_comparison(original, jittered, sr, method, output_file)
    plot_jitter_histogram(jitter, method, output_file)

    preview_waveform(data[:, 0] if data.ndim == 2 else data,
                     output[:, 0] if data.ndim == 2 else output,
                     sr)

def preview_waveform(original, jittered, sr):
    times = np.arange(len(original)) / sr
    plt.figure(figsize=(10, 4))
    plt.plot(times[:500], original[:500], label="Original", alpha=0.6)
    plt.plot(times[:500], jittered[:500], label="Jittered", alpha=0.6)
    plt.title("Waveform Comparison (First 500 Samples)")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_waveform_comparison(original, jittered, sr, method, output_path):
    times = np.arange(len(original)) / sr
    snippet = 500  # Number of samples to visualize
    plt.figure(figsize=(10, 4))
    plt.plot(times[:snippet], original[:snippet], label='Original', alpha=0.6)
    plt.plot(times[:snippet], jittered[:snippet], label='Jittered', alpha=0.6)
    plt.title(f"Waveform Comparison – Method: {method}")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.tight_layout()
    image_path = output_path.replace(".wav", f"_waveform_{method}.png")
    plt.savefig(image_path)
    plt.close()
    print(f"Saved waveform comparison to: {image_path}")

def plot_spectrogram_comparison(original, jittered, sr, method, output_path):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for i, (signal, title) in enumerate([(original, "Original"), (jittered, "Jittered")]):
        axes[i].specgram(signal, NFFT=1024, Fs=sr, noverlap=512, cmap='viridis')
        axes[i].set_title(f"{title} – Method: {method}")
        axes[i].set_xlabel("Time (s)")
        axes[i].set_ylabel("Frequency (Hz)")
    plt.tight_layout()
    image_path = output_path.replace(".wav", f"_spectrogram_{method}.png")
    plt.savefig(image_path)
    plt.close()
    print(f"Saved spectrogram comparison to: {image_path}")

def plot_jitter_histogram(jitter_array, method, output_path):
    plt.figure(figsize=(8, 4))
    plt.hist(jitter_array * 1e6, bins=100, color='steelblue', edgecolor='black')
    plt.title(f"Jitter Distribution – Method: {method}")
    plt.xlabel("Jitter (µs)")
    plt.ylabel("Count")
    plt.tight_layout()
    image_path = output_path.replace(".wav", f"_jitter_histogram_{method}.png")
    plt.savefig(image_path)
    plt.close()
    print(f"Saved jitter histogram to: {image_path}")

def launch_gui():
    def browse_file():
        filename = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if filename:
            file_entry.delete(0, tk.END)
            file_entry.insert(0, filename)

    def update_manual_input(*args):
        is_manual = preset_var.get() == "Manual"
        manual_entry.configure(state=tk.NORMAL if is_manual else tk.DISABLED)

    def run_simulation():
        file_path = file_entry.get()
        preset_name = preset_var.get()
        method = interp_var.get()
        if preset_name == "Manual":
            try:
                jitter_std = float(manual_entry.get())
                if jitter_std <= 0:
                    raise ValueError
            except ValueError:
                print("Please enter a valid positive number for manual jitter.")
                return
        else:
            jitter_std = PRESETS[preset_name] * float(jitter_scale.get())
        process_file(file_path, jitter_std, method)

    root = tk.Tk()
    root.title("Audio Jitter Simulator")

    tk.Label(root, text="WAV file:").grid(row=0, column=0)
    file_entry = tk.Entry(root, width=40)
    file_entry.grid(row=0, column=1)
    tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2)
    ToolTip(file_entry, "Select your input WAV file (mono or stereo)")

    tk.Label(root, text="Hardware Preset:").grid(row=1, column=0)
    preset_var = tk.StringVar(value="Consumer Grade")
    preset_menu = tk.OptionMenu(root, preset_var, *PRESETS.keys(), command=update_manual_input)
    preset_menu.grid(row=1, column=1)
    ToolTip(preset_menu, "Choose a hardware preset or select Manual input")

    tk.Label(root, text="Jitter Multiplier:").grid(row=2, column=0)
    jitter_scale = tk.Scale(root, from_=0.5, to=5.0, resolution=0.1,
                            orient=tk.HORIZONTAL)
    jitter_scale.set(1.0)
    jitter_scale.grid(row=2, column=1)
    ToolTip(jitter_scale, "Multiplies the preset jitter value")

    tk.Label(root, text="Manual Jitter Value (sec):").grid(row=3, column=0)
    manual_entry = tk.Entry(root)
    manual_entry.grid(row=3, column=1)
    manual_entry.insert(0, "0.000001")
    manual_entry.configure(state=tk.DISABLED)
    ToolTip(manual_entry, "Enter custom jitter in seconds (used only if Manual is selected)")

    tk.Label(root, text="Interpolation Method:").grid(row=4, column=0)
    interp_var = tk.StringVar(value="cubic")
    interp_menu = tk.OptionMenu(root, interp_var, *INTERPOLATION_METHODS)
    interp_menu.grid(row=4, column=1)
    ToolTip(interp_menu, 
        "Choose how the waveform is interpolated.\n" +
        "• cubic = smooth, natural curves\n" +
        "• nearest = jagged steps\n" +
        "• linear/slinear/quadratic = progressively smoother\n" +
        "• zero = flat segments"
    )

    tk.Button(root, text="Apply Jitter", command=run_simulation).grid(row=5, column=1)

    version_label = tk.Label(root, text=f"JEL Audio-Jitter-Simulator – Version {SCRIPT_VERSION}", fg="gray")
    version_label.grid(row=6, column=1, pady=(10, 0))

    root.mainloop()

launch_gui()