# Text-to-Foley

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.1.0-ee4c2c.svg)](https://pytorch.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Generate professional foley sound effects from text descriptions using AI-powered audio generation.

## Features

- Generate high-quality foley sound effects from text prompts
- Built on Meta's AudioCraft/AudioGen foundation model
- Smart prompt enhancement system for better audio quality
- Preset library with optimized prompts for common sound categories
- Simple, intuitive Python API
- Audio processing utilities (fade in/out, normalization)

## Installation

### Prerequisites

- Python 3.9 or higher
- CUDA-capable GPU (recommended for faster generation)
- FFmpeg development libraries (Linux):

  ```bash
  sudo apt install ffmpeg libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libavfilter-dev libswscale-dev libswresample-dev
  ```

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/text-to-foley.git
   cd text-to-foley
   ```

2. **Create a virtual environment**

   Using conda (recommended):
   ```bash
   conda create -n text-to-foley python=3.9 -y
   conda activate text-to-foley
   ```

   Or using venv:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install PyTorch**

   For CUDA 12.1 (GPU):
   ```bash
   pip install torch==2.1.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu121
   ```

   For CPU only:
   ```bash
   pip install torch==2.1.0 torchaudio==2.1.0
   ```

4. **Install the package**
   ```bash
   pip install -e .
   ```

5. **Verify installation**
   ```bash
   python -c "from text_to_foley import FoleyGenerator; print('Installation successful!')"
   ```

## Quick Start

Generate audio quickly using the provided script:

```bash
# Simple generation
python scripts/generate.py --prompt="shaking keys"

# With custom duration and output
python scripts/generate.py --prompt="door closing" --duration=3 --output=door.wav

# Use a preset
python scripts/generate.py --preset=rain_heavy --duration=10

# Generate multiple variations
python scripts/generate.py --prompt="footsteps on wood" --variations=3
```

See [scripts/README.md](scripts/README.md) for all available options.

### Python API

```python
from text_to_foley import FoleyGenerator

# Initialize the generator (model loads on first use)
generator = FoleyGenerator()

# Generate a sound effect
audio = generator.generate(
    prompt="footsteps on wooden floor, slow walking pace",
    duration=5.0,
    guidance_scale=3.0
)

# Save to file
audio.save("footsteps.wav")

# Generate multiple variations
variations = generator.generate(
    prompt="glass breaking on tile floor",
    duration=3.0,
    num_variations=3
)

# Save each variation
for i, audio in enumerate(variations):
    audio.save(f"glass_break_{i+1}.wav")

# Use presets for quick generation
rain_audio = generator.generate_from_preset("rain_heavy", duration=10.0)
rain_audio.save("rain.wav")

# Apply audio processing
processed = audio.fade_in_out(fade_in_duration=0.05, fade_out_duration=0.1)
processed.save("footsteps_faded.wav")
```

## Examples

The following examples demonstrate the library's capabilities. Audio files are generated using the prompts shown below:

| Prompt | Audio File | Duration | Description |
|--------|------------|----------|-------------|
| `"footsteps on wooden floor, slow walking pace, indoor"` | [footsteps.wav](examples/audio/footsteps.wav) | 5s | Realistic indoor footsteps |
| `"heavy rain on metal roof, steady downpour"` | [rain.wav](examples/audio/rain.wav) | 10s | Atmospheric rain ambience |
| `"large window glass violently shattering, exploding into pieces, dramatic crash"` | [glass_break.wav](examples/audio/glass_break.wav) | 3s | Spectacular glass destruction |
| `"deep thunder rumble, powerful storm rolling thunder, dramatic boom"` | [thunder.wav](examples/audio/thunder.wav) | 4s | Powerful thunderstorm sound |

## Advanced Usage

### Batch Generation

Generate multiple sounds efficiently:

```python
from text_to_foley import FoleyGenerator

generator = FoleyGenerator()

# Batch generate multiple different sounds
prompts = [
    "footsteps on gravel",
    "door closing softly",
    "glass clinking",
    "paper rustling"
]

audio_list = generator.generate_batch(
    prompts=prompts,
    duration=3.0,
    guidance_scale=3.0
)

# Save all generated audio
for i, audio in enumerate(audio_list):
    audio.save(f"batch_output_{i+1}.wav")
```

### Prompt Enhancement

Improve your prompts automatically for better results:

```python
from text_to_foley import enhance_prompt, suggest_prompt_improvements

# Get suggestions for improving a prompt
prompt = "door sound"
suggestions = suggest_prompt_improvements(prompt)
print("Suggestions:", suggestions)

# Automatically enhance a prompt
enhanced = enhance_prompt(prompt)
print("Enhanced:", enhanced)

# Use enhancement during generation
audio = generator.generate(
    prompt="door closing",
    enhance_prompt_auto=True  # Automatically enhances the prompt
)
```

### Reproducible Generation

Use seeds for consistent results:

```python
# Generate with a specific seed
audio1 = generator.generate(
    prompt="thunder rumble",
    duration=5.0,
    seed=42
)

# Same seed = same output
audio2 = generator.generate(
    prompt="thunder rumble",
    duration=5.0,
    seed=42
)

# audio1 and audio2 will be identical
```


### Listing Available Presets

```python
# Get all available presets
presets = generator.list_presets()

for key, prompt in presets.items():
    print(f"{key}: {prompt}")
```
