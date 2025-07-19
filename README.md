## 🎧 JEL_Audio-Jitter-Simulator

This tool simulates **jitter**—the subtle time-based distortion that happens when samples are processed slightly off-time. It’s often invisible, but sometimes audible, especially in music.

---

### 🚀 Features

- 🐍 Written entirely in Python.
- 🎼 Supports **stereo WAV files** and **mono WAV files** of typical bit-sizes and sample-rates.
- 🎛️ Interactive GUI with preset hardware profiles:
  - **High-End DAC** (ultra-low jitter)
  - **Consumer Grade** (normal wear and tear)
  - **Vintage Gear** (a wobbly blast from the past)
- 🎚️ Fine-tune jitter with a slider multiplier.
- 💾 Saves processed files as `_jittered.wav` in the same dir as input-file is loaded from.

---

### 📦 Installation

Clone this repo and install dependencies:

```bash
git clone https://github.com/JELSTUDIO/JEL_Audio-Jitter-Simulator.git
cd JEL_Audio-Jitter-Simulator
pip3 install -r requirements.txt
```

---

### 🧪 Usage

Once installed, run the GUI:

```bash
python audio_jitter_gui.py
```

Then:
1. Select a stereo or mono WAV file.
2. Choose a hardware preset.
3. Adjust the jitter multiplier.
4. Click **Apply Jitter**.
5. A new file appears with `_jittered.wav` in the name.

🎉 This new file has the chosen jitter-flavor baked into the audio!

---

### 🧠 How It Works

Digital audio assumes perfectly spaced samples in time.  
But in reality, clock imperfections cause samples to land a few microseconds early or late—this is jitter.

This tool simulates that:
- Reconstructs your waveform with interpolation.
- Applies randomized timing offsets.
- Resamples with the jittered timing grid.

---

### 🙋 Who's This For?

- Audio engineers & curious musicians  
- DSP learners & educators  

---

### 📬 License & Attribution

MIT License.  
Originally created by [JELSTUDIO] using Microsoft Copilot.
