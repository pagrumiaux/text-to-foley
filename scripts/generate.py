#!/usr/bin/env python
"""
Quick audio generation script for text-to-foley.

Usage:
    python scripts/generate.py --prompt="shaking keys"
    python scripts/generate.py --prompt="door closing" --duration=3 --output=door.wav
    python scripts/generate.py --preset=rain_heavy --duration=10
"""

import argparse
import sys
from pathlib import Path

# Add src to path if running from scripts directory
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from text_to_foley import FoleyGenerator


def main():
    parser = argparse.ArgumentParser(
        description="Generate foley sound effects from text prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/generate.py --prompt="shaking keys"
  python scripts/generate.py --prompt="door closing" --duration=3 --output=door.wav
  python scripts/generate.py --preset=rain_heavy --duration=10
  python scripts/generate.py --prompt="footsteps" --variations=3 --enhance
        """
    )

    # Prompt or preset
    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument(
        "--prompt", "-p",
        type=str,
        help="Text description of the sound to generate"
    )
    prompt_group.add_argument(
        "--preset",
        type=str,
        help="Use a predefined preset (e.g., rain_heavy, door_close_heavy)"
    )

    # Generation parameters
    parser.add_argument(
        "--duration", "-d",
        type=float,
        default=5.0,
        help="Duration in seconds (default: 5.0)"
    )
    parser.add_argument(
        "--variations", "-n",
        type=int,
        default=1,
        help="Number of variations to generate (default: 1)"
    )
    parser.add_argument(
        "--guidance-scale", "-g",
        type=float,
        default=3.0,
        help="CFG guidance scale, higher=more faithful to prompt (default: 3.0)"
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=None,
        help="Random seed for reproducibility (default: None)"
    )
    parser.add_argument(
        "--enhance", "-e",
        action="store_true",
        help="Automatically enhance the prompt for better results"
    )

    # Output parameters
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output file path (default: auto-generated in outputs/)"
    )
    parser.add_argument(
        "--device",
        type=str,
        choices=["cuda", "cpu"],
        default=None,
        help="Device to use (default: auto-detect)"
    )

    # Parse arguments
    args = parser.parse_args()

    # Initialize generator
    print(f"Initializing FoleyGenerator (device: {args.device or 'auto-detect'})...")
    generator = FoleyGenerator(device=args.device)

    # Determine prompt
    if args.preset:
        print(f"Using preset: {args.preset}")
        audio = generator.generate_from_preset(
            preset=args.preset,
            duration=args.duration,
            num_variations=args.variations,
            guidance_scale=args.guidance_scale,
            seed=args.seed,
        )
        prompt_for_filename = args.preset
    else:
        prompt = args.prompt
        print(f"Generating audio for prompt: '{prompt}'")
        print(f"Parameters: duration={args.duration}s, variations={args.variations}, guidance_scale={args.guidance_scale}")

        audio = generator.generate(
            prompt=prompt,
            duration=args.duration,
            num_variations=args.variations,
            guidance_scale=args.guidance_scale,
            enhance_prompt_auto=args.enhance,
            seed=args.seed,
        )
        prompt_for_filename = prompt

    # Handle single or multiple variations
    if args.variations == 1:
        audio_list = [audio]
    else:
        audio_list = audio

    # Save outputs
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    for i, audio_obj in enumerate(audio_list):
        if args.output:
            if args.variations == 1:
                output_path = Path(args.output)
            else:
                base = Path(args.output)
                output_path = base.with_stem(f"{base.stem}_{i+1}")
        else:
            # Generate filename from prompt
            safe_name = "".join(
                c if c.isalnum() or c in "_ " else "_"
                for c in prompt_for_filename
            )
            safe_name = safe_name[:50].strip().replace(" ", "_")

            if args.variations > 1:
                safe_name = f"{safe_name}_{i+1}"

            output_path = output_dir / f"{safe_name}.wav"

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save
        audio_obj.save(output_path)
        print(f"✓ Saved: {output_path}")
        print(f"  Duration: {audio_obj.duration:.2f}s, Sample rate: {audio_obj.sample_rate}Hz")

    print(f"\nDone! Generated {len(audio_list)} audio file(s)")


if __name__ == "__main__":
    main()