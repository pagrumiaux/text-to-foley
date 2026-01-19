# Scripts

Utility scripts for quick audio generation and testing.

## generate.py

Quick audio generation script for creating foley sound effects from the command line.

### Basic Usage

```bash
# Simple generation
python scripts/generate.py --prompt="shaking keys"

# With custom duration
python scripts/generate.py --prompt="door closing" --duration=3

# Specify output file
python scripts/generate.py --prompt="glass breaking" --output=outputs/glass.wav

# Generate multiple variations
python scripts/generate.py --prompt="footsteps" --variations=3

# Use a preset
python scripts/generate.py --preset=rain_heavy --duration=10

# Auto-enhance the prompt
python scripts/generate.py --prompt="door" --enhance

# Set random seed for reproducibility
python scripts/generate.py --prompt="footsteps" --seed=42
```

### All Options

```
--prompt, -p          Text description of the sound to generate
--preset              Use a predefined preset
--duration, -d        Duration in seconds (default: 5.0)
--variations, -n      Number of variations to generate (default: 1)
--guidance-scale, -g  CFG guidance scale (default: 3.0)
--seed, -s            Random seed for reproducibility
--enhance, -e         Automatically enhance the prompt
--output, -o          Output file path (default: outputs/)
--device              Device to use: cuda or cpu (default: auto-detect)
```

### Examples

```bash
# Generate a 10-second rain ambience
python scripts/generate.py --preset=rain_heavy --duration=10

# Generate 5 variations of footsteps
python scripts/generate.py --prompt="footsteps on wood" --variations=5

# Reproducible generation
python scripts/generate.py --prompt="door slam" --seed=42 --duration=2

# High guidance for more faithful generation
python scripts/generate.py --prompt="glass shattering" --guidance-scale=5.0
```

### Output

By default, files are saved to the `outputs/` directory with auto-generated names based on the prompt. Use `--output` to specify a custom path.
