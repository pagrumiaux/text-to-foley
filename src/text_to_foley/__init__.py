"""Text to foley - Generate foley sound effects from text descriptions."""

from text_to_foley.generator import FoleyGenerator
from text_to_foley.audio import GeneratedAudio
from text_to_foley.prompts import FoleyCategory, enhance_prompt

__version__ = "0.1.0"
__all__ = [
    "FoleyGenerator",
    "GeneratedAudio",
    "FoleyCategory",
    "enhance_prompt",
]
