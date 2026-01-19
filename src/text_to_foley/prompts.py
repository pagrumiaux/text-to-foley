"""
Prompt engineering utilities for audio generation.

This module contains templates, enhancement functions, and best practices
for crafting effective prompts for audio generation models.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class FoleyCategory(str, Enum):
    """Categories of foley sounds with optimized prompt structures."""
    
    FOOTSTEPS = "footsteps"
    IMPACTS = "impacts"
    AMBIENCES = "ambiences"
    MECHANICAL = "mechanical"
    WEATHER = "weather"
    FOLIAGE = "foliage"
    WATER = "water"
    CLOTH = "cloth"
    GLASS = "glass"
    METAL = "metal"
    WOOD = "wood"
    VEHICLES = "vehicles"
    DOORS = "doors"
    UI_SOUNDS = "ui_sounds"


@dataclass
class PromptTemplate:
    """Template for constructing effective foley prompts."""
    
    category: FoleyCategory
    base_structure: str
    recommended_modifiers: list[str]
    example_prompts: list[str]


# Foley-optimized prompt templates based on sound design best practices
PROMPT_TEMPLATES: dict[FoleyCategory, PromptTemplate] = {
    FoleyCategory.FOOTSTEPS: PromptTemplate(
        category=FoleyCategory.FOOTSTEPS,
        base_structure="{action} on {surface}, {pace} pace, {perspective}",
        recommended_modifiers=[
            "walking", "running", "shuffling", "tiptoeing", "stomping",
            "wood", "concrete", "gravel", "grass", "tile", "carpet", "metal",
            "slow", "medium", "fast", "steady", "irregular",
            "close-up", "distant", "indoor", "outdoor"
        ],
        example_prompts=[
            "footsteps on wooden floor, slow walking pace, indoor close-up",
            "running footsteps on wet pavement, fast pace, outdoor",
            "shuffling feet on carpet, slow irregular pace, muffled",
            "heavy boots on metal grating, steady walking pace, industrial"
        ]
    ),
    FoleyCategory.IMPACTS: PromptTemplate(
        category=FoleyCategory.IMPACTS,
        base_structure="{object} {action} {surface}, {intensity}",
        recommended_modifiers=[
            "hitting", "dropping", "crashing", "slamming", "tapping",
            "metal", "wood", "glass", "plastic", "stone", "concrete",
            "light", "heavy", "sharp", "dull", "resonant"
        ],
        example_prompts=[
            "metal object dropping on concrete floor, heavy thud with ring",
            "book falling on wooden table, medium impact, indoor",
            "glass bottle hitting tile, sharp crack, close perspective",
            "cardboard box dropped on ground, soft thump, outdoor"
        ]
    ),
    FoleyCategory.AMBIENCES: PromptTemplate(
        category=FoleyCategory.AMBIENCES,
        base_structure="{environment} ambience, {elements}, {mood}",
        recommended_modifiers=[
            "forest", "city", "office", "cafe", "beach", "park", "subway",
            "birds", "traffic", "chatter", "wind", "machinery",
            "peaceful", "busy", "quiet", "intense", "calm"
        ],
        example_prompts=[
            "forest ambience, birds chirping, light wind through leaves, peaceful",
            "busy city street, traffic noise, distant car horns, urban",
            "quiet office ambience, air conditioning hum, keyboard typing, calm",
            "beach ambience, waves crashing, seagulls, windy"
        ]
    ),
    FoleyCategory.MECHANICAL: PromptTemplate(
        category=FoleyCategory.MECHANICAL,
        base_structure="{mechanism} {action}, {quality}, {context}",
        recommended_modifiers=[
            "door", "lever", "switch", "gear", "hinge", "lock", "latch",
            "opening", "closing", "clicking", "turning", "squeaking",
            "old", "new", "rusty", "smooth", "stiff",
            "indoor", "outdoor", "industrial"
        ],
        example_prompts=[
            "old wooden door creaking open slowly, rusty hinges, indoor",
            "metal lever being pulled, mechanical click, industrial",
            "light switch clicking on and off, plastic, close-up",
            "car door closing firmly, modern vehicle, outdoor"
        ]
    ),
    FoleyCategory.WEATHER: PromptTemplate(
        category=FoleyCategory.WEATHER,
        base_structure="{weather_type}, {intensity}, {perspective}",
        recommended_modifiers=[
            "rain", "thunder", "wind", "hail", "snow",
            "light", "heavy", "gentle", "intense", "distant", "close",
            "indoor perspective", "outdoor", "on roof", "on window"
        ],
        example_prompts=[
            "heavy rain on metal roof, steady downpour, indoor perspective",
            "thunder rumble, distant storm, outdoor",
            "gentle rain on window, light patter, cozy indoor",
            "strong wind through trees, howling, outdoor exposure"
        ]
    ),
    FoleyCategory.WATER: PromptTemplate(
        category=FoleyCategory.WATER,
        base_structure="{water_action}, {intensity}, {context}",
        recommended_modifiers=[
            "dripping", "splashing", "pouring", "flowing", "bubbling",
            "light", "heavy", "gentle", "rushing",
            "sink", "bathtub", "river", "puddle", "glass"
        ],
        example_prompts=[
            "water dripping into sink, slow steady drips, bathroom",
            "water being poured into glass, clear liquid, close-up",
            "river flowing gently, calm water over rocks, outdoor",
            "splash in puddle, single footstep, outdoor wet pavement"
        ]
    ),
    FoleyCategory.CLOTH: PromptTemplate(
        category=FoleyCategory.CLOTH,
        base_structure="{fabric} {action}, {quality}",
        recommended_modifiers=[
            "rustling", "folding", "tearing", "brushing", "flapping",
            "silk", "cotton", "denim", "leather", "canvas", "paper",
            "soft", "crisp", "heavy", "light"
        ],
        example_prompts=[
            "fabric rustling, clothing movement, soft cotton",
            "leather jacket creaking, movement sounds, close-up",
            "paper being crumpled, crisp texture, office",
            "flag flapping in wind, canvas material, outdoor"
        ]
    ),
}


def enhance_prompt(
    prompt: str,
    category: Optional[FoleyCategory] = None,
    add_quality_descriptors: bool = True,
    add_perspective: bool = True,
) -> str:
    """
    Enhance a basic prompt with foley-specific details for better generation.
    
    Args:
        prompt: The base prompt to enhance
        category: Optional foley category to guide enhancement
        add_quality_descriptors: Add audio quality terms like "clear", "high fidelity"
        add_perspective: Add spatial/perspective information
        
    Returns:
        Enhanced prompt string optimized for audio generation
        
    Example:
        >>> enhance_prompt("door closing")
        'door closing firmly, clear audio, close-up recording'
    """
    enhanced_parts = [prompt.strip()]
    
    # Add category-specific enhancements
    if category and category in PROMPT_TEMPLATES:
        template = PROMPT_TEMPLATES[category]
        # Could add random modifier from template, but for reproducibility
        # we just ensure the structure is good
        pass
    
    # Add quality descriptors that help AudioGen
    if add_quality_descriptors:
        quality_terms = ["high quality", "clear audio"]
        if not any(term in prompt.lower() for term in quality_terms):
            enhanced_parts.append("high quality sound")
    
    # Add perspective if not present
    if add_perspective:
        perspective_terms = ["close-up", "distant", "indoor", "outdoor", "perspective"]
        if not any(term in prompt.lower() for term in perspective_terms):
            enhanced_parts.append("close-up recording")
    
    return ", ".join(enhanced_parts)


def get_category_examples(category: FoleyCategory) -> list[str]:
    """Get example prompts for a specific foley category."""
    if category in PROMPT_TEMPLATES:
        return PROMPT_TEMPLATES[category].example_prompts
    return []


def suggest_prompt_improvements(prompt: str) -> list[str]:
    """
    Analyze a prompt and suggest improvements for better generation.
    
    Args:
        prompt: The prompt to analyze
        
    Returns:
        List of suggestions for improving the prompt
    """
    suggestions = []
    prompt_lower = prompt.lower()
    
    # Check for vague terms
    vague_terms = ["sound", "noise", "something", "thing"]
    for term in vague_terms:
        if term in prompt_lower and len(prompt_lower.split()) < 4:
            suggestions.append(
                f"Consider replacing '{term}' with a more specific description"
            )
    
    # Check for missing material/surface
    material_terms = [
        "wood", "metal", "glass", "concrete", "tile", "carpet", 
        "gravel", "grass", "plastic", "leather", "fabric"
    ]
    action_terms = ["footstep", "impact", "hit", "drop", "walk", "step"]
    has_action = any(term in prompt_lower for term in action_terms)
    has_material = any(term in prompt_lower for term in material_terms)
    
    if has_action and not has_material:
        suggestions.append(
            "Adding a surface material (wood, metal, concrete, etc.) improves results"
        )
    
    # Check for perspective
    perspective_terms = ["close", "distant", "near", "far", "indoor", "outdoor"]
    if not any(term in prompt_lower for term in perspective_terms):
        suggestions.append(
            "Consider adding perspective (close-up, distant, indoor, outdoor)"
        )
    
    # Check for intensity/speed
    intensity_terms = [
        "slow", "fast", "gentle", "heavy", "light", "strong", 
        "soft", "loud", "quiet", "intense"
    ]
    if not any(term in prompt_lower for term in intensity_terms):
        suggestions.append(
            "Adding intensity descriptors (gentle, heavy, slow, fast) helps"
        )
    
    # Check prompt length
    word_count = len(prompt.split())
    if word_count < 3:
        suggestions.append(
            "Short prompts often produce generic results. Try adding more detail."
        )
    elif word_count > 20:
        suggestions.append(
            "Very long prompts may confuse the model. Consider focusing on key details."
        )
    
    return suggestions


# Quick reference for common foley sounds
FOLEY_QUICK_PROMPTS = {
    # Footsteps
    "walk_wood": "footsteps walking on wooden floor, steady pace, indoor",
    "walk_concrete": "footsteps on concrete sidewalk, casual walking, outdoor",
    "walk_gravel": "footsteps crunching on gravel path, slow walking",
    "run_pavement": "running footsteps on pavement, fast pace, outdoor",
    
    # Doors
    "door_open_wood": "wooden door opening slowly, creaking hinges, indoor",
    "door_close_heavy": "heavy door closing firmly, solid thud, indoor",
    "door_slam": "door slamming shut, aggressive impact, indoor",
    
    # Impacts
    "object_drop_table": "object dropped on wooden table, light impact",
    "glass_break": "glass shattering, breaking impact, indoor",
    "metal_clang": "metal objects clanging together, resonant",
    
    # Weather
    "rain_light": "light rain falling, gentle patter, outdoor",
    "rain_heavy": "heavy rain downpour, intense rainfall, outdoor",
    "thunder_distant": "distant thunder rumble, approaching storm",
    "wind_trees": "wind blowing through trees, leaves rustling",
    
    # Ambience
    "office_quiet": "quiet office ambience, air conditioning, keyboard typing",
    "city_traffic": "city street ambience, traffic, distant car horns",
    "forest_day": "forest ambience, birds singing, gentle breeze",
    
    # UI/Digital
    "click_button": "button click, digital interface, clean click sound",
    "notification": "notification sound, digital alert, pleasant tone",
}
