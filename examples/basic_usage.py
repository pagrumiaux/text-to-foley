"""
Basic usage examples.

This script demonstrates the core functionality of the library.
Run with: python examples/basic_usage.py
"""

from text_to_foley import FoleyGenerator, enhance_prompt, FoleyCategory
from text_to_foley.prompts import suggest_prompt_improvements

def main():
    # Initialize the generator
    # First call will download the model
    print("Initializing FoleyGenerator...")
    generator = FoleyGenerator()
    print(f"Generator ready: {generator}")
    print()
    
    # Example 1: Simple generation
    print("Example 1: basic generation")
    print("-" * 50)
    
    audio = generator.generate(
        prompt="footsteps on wooden floor, slow walking pace, indoor",
        duration=3.0
    )
    
    output_path = audio.save("outputs/footsteps_basic.wav")
    print(f"Generated: {output_path} with duration: {audio.duration:.2f}s")
    print()
    
    # Example 2: Using prompt enhancement
    print("Example 2: with prompt enhancement")
    print("-" * 50)
    
    simple_prompt = "door closing"
    enhanced = enhance_prompt(simple_prompt, category=FoleyCategory.DOORS)
    print(f"Original prompt: '{simple_prompt}'")
    print(f"Enhanced prompt: '{enhanced}'")
    
    audio = generator.generate(
        prompt=simple_prompt,
        duration=2.0,
        enhance_prompt_auto=True
    )
    audio.save("outputs/door_enhanced.wav")
    print()
    
    # Example 3: Generate multiple variations
    print("Example 3: multiple variations")
    print("-" * 50)
    
    variations = generator.generate(
        prompt="glass breaking and shattering, indoor",
        duration=2.5,
        num_variations=3,
        seed=42
    )
    
    for i, audio in enumerate(variations):
        path = audio.save(f"outputs/glass_break_v{i+1}.wav")
        print(f"Variation {i+1}: {path}")
    print()
    
    # Example 4: Using presets
    print("Example 4: using presets")
    print("-" * 50)
    
    print("Available presets:")
    presets = generator.list_presets()
    for name in list(presets.keys())[:5]:
        print(f"  {name}: {presets[name]}")
    print("  ...")
    
    audio = generator.generate_from_preset("rain_heavy", duration=5.0)
    audio.save("outputs/rain_preset.wav")
    print()
    
    # Example 5: Prompt analysis
    print("Example 5: prompt analysis")
    print("-" * 50)
    
    test_prompt = "door sound"
    suggestions = suggest_prompt_improvements(test_prompt)
    
    print(f"Analyzing prompt: '{test_prompt}'")
    print("Suggestions:")
    for s in suggestions:
        print(f"  • {s}")
    print()
        
    print()
    print("✅ All examples completed! Check the 'outputs' directory.")


if __name__ == "__main__":
    main()
