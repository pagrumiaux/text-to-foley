"""
Core foley audio generation using AudioGen.

This module wraps the AudioGen model from Meta's AudioCraft library
with foley-specific optimizations and a clean API.
"""

import logging
from pathlib import Path
from typing import Optional, Union
import torch

from text_to_foley.audio import GeneratedAudio
from text_to_foley.prompts import (
    FoleyCategory,
    enhance_prompt,
    FOLEY_QUICK_PROMPTS,
)

logger = logging.getLogger(__name__)


class FoleyGenerator:
    """
    Generate foley sound effects from text descriptions.
    
    This class wraps AudioGen with foley-specific optimizations including
    prompt enhancement, sensible defaults for sound effects, and convenient
    output handling.
    
    Example:
        >>> generator = FoleyGenerator()
        >>> audio = generator.generate("footsteps on wooden floor")
        >>> audio.save("footsteps.wav")
        
    Attributes:
        model: The underlying AudioGen model
        device: Device the model is loaded on
        sample_rate: Output sample rate (16000 Hz for AudioGen)
    """
    
    DEFAULT_MODEL = "facebook/audiogen-medium"
    SAMPLE_RATE = 16000
    
    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        device: Optional[str] = None,
        cache_dir: Optional[str] = None,
    ):
        """
        Initialize the FoleyGenerator.

        Args:
            model_name: AudioGen model to use. Currently available:
                - "facebook/audiogen-medium" (1.5B params, default)
                Note: AudioGen only provides this single pretrained model.
                      Requires GPU with at least 16GB VRAM.
            device: Device to run on ('cuda', 'mps', 'cpu').
                    Auto-detected if None.
            cache_dir: Directory for model cache. Uses default if None.
        """
        self.model_name = model_name
        self.device = self._get_device(device)
        self.cache_dir = cache_dir
        self._model = None
        
        logger.info(f"FoleyGenerator initialized (device: {self.device})")
    
    def _get_device(self, device: Optional[str]) -> str:
        """Determine the best available device."""
        if device is not None:
            return device
        
        if torch.cuda.is_available():
            return "cuda"
        return "cpu"
    
    @property
    def model(self):
        """Lazy-load the model on first use."""
        if self._model is None:
            self._model = self._load_model()
        return self._model
    
    @property
    def sample_rate(self) -> int:
        """Output sample rate of the model."""
        return self.SAMPLE_RATE
    
    def _load_model(self):
        """Load the AudioGen model."""
        from audiocraft.models import AudioGen
        logger.info(f"Loading AudioGen model: {self.model_name}")
        
        model = AudioGen.get_pretrained(self.model_name, device=self.device)
        logger.info("Model loaded successfully")
        
        return model
    
    def generate(
        self,
        prompt: str,
        duration: float = 10.0,
        num_variations: int = 1,
        guidance_scale: float = 3.0,
        enhance_prompt_auto: bool = False,
        category: Optional[FoleyCategory] = None,
        seed: Optional[int] = None,
        progress_callback: Optional[callable] = None,
    ) -> Union[GeneratedAudio, list[GeneratedAudio]]:
        """
        Generate foley audio from a text prompt.
        
        Args:
            prompt: Text description of the desired sound effect.
                    Can also be a key from FOLEY_QUICK_PROMPTS.
            duration: Duration of generated audio in seconds (max ~30s)
            num_variations: Number of variations to generate
            guidance_scale: Classifier-free guidance scale (higher = more faithful
                           to prompt but potentially less diverse). Default 3.0 is
                           good for foley.
            enhance_prompt_auto: Automatically enhance the prompt with foley-specific
                                 details for better results.
            category: Optional foley category to guide prompt enhancement
            seed: Random seed for reproducibility
            progress_callback: Optional callback for progress updates
            
        Returns:
            GeneratedAudio if num_variations=1, else list of GeneratedAudio
            
        Example:
            >>> audio = generator.generate(
            ...     "glass breaking and falling",
            ...     duration=3.0,
            ...     guidance_scale=4.0
            ... )
        """
        # Check for quick prompt shortcut
        if prompt in FOLEY_QUICK_PROMPTS:
            prompt = FOLEY_QUICK_PROMPTS[prompt]
            logger.info(f"Using quick prompt: {prompt}")
        
        # Enhance prompt if requested
        if enhance_prompt_auto:
            original_prompt = prompt
            prompt = enhance_prompt(prompt, category=category)
            logger.info(f"Enhanced prompt: '{original_prompt}' -> '{prompt}'")
        
        # Set generation parameters
        self.model.set_generation_params(
            duration=duration,
            cfg_coef=guidance_scale,
        )
        
        # Set seed if provided
        if seed is not None:
            torch.manual_seed(seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed(seed)
        
        # Generate
        logger.info(f"Generating {num_variations} variation(s): '{prompt}'")
        
        # AudioGen expects a list of prompts
        prompts = [prompt] * num_variations
        
        with torch.no_grad():
            wav = self.model.generate(prompts)
        
        # Convert to GeneratedAudio objects
        results = []
        for i in range(num_variations):
            audio_tensor = wav[i]  # (1, num_samples)
            
            audio = GeneratedAudio(
                waveform=audio_tensor.squeeze().cpu(),
                sample_rate=self.model.sample_rate,
                prompt=prompt,
                metadata={
                    "model": self.model_name,
                    "duration": duration,
                    "guidance_scale": guidance_scale,
                    "variation": i,
                    "seed": seed,
                }
            )
            
            # Apply fade to avoid clicks
            audio = audio.fade_in_out(fade_in_duration=0.01, fade_out_duration=0.05)
            results.append(audio)
        
        if num_variations == 1:
            return results[0]
        return results
    
    def generate_batch(
        self,
        prompts: list[str],
        duration: float = 5.0,
        guidance_scale: float = 3.0,
        enhance_prompt_auto: bool = False,
    ) -> list[GeneratedAudio]:
        """
        Generate audio for multiple prompts efficiently.
        
        This is more efficient than calling generate() multiple times
        as it batches the generation.
        
        Args:
            prompts: List of text prompts
            duration: Duration for all generated audio
            guidance_scale: CFG scale for all generations
            enhance_prompt_auto: Enhance all prompts automatically
            
        Returns:
            List of GeneratedAudio objects
        """
        if enhance_prompt_auto:
            prompts = [enhance_prompt(p) for p in prompts]
        
        self.model.set_generation_params(
            duration=duration,
            cfg_coef=guidance_scale,
        )
        
        logger.info(f"Batch generating {len(prompts)} sounds")
        
        with torch.no_grad():
            wav = self.model.generate(prompts)
        
        results = []
        for i, prompt in enumerate(prompts):
            audio = GeneratedAudio(
                waveform=wav[i].squeeze().cpu(),
                sample_rate=self.model.sample_rate,
                prompt=prompt,
                metadata={
                    "model": self.model_name,
                    "duration": duration,
                    "guidance_scale": guidance_scale,
                    "batch_index": i,
                }
            )
            audio = audio.fade_in_out()
            results.append(audio)
        
        return results
    
    def generate_from_preset(
        self,
        preset: str,
        duration: float = 5.0,
        **kwargs
    ) -> GeneratedAudio:
        """
        Generate audio using a predefined preset.
        
        Args:
            preset: Key from FOLEY_QUICK_PROMPTS
            duration: Duration in seconds
            **kwargs: Additional arguments passed to generate()
            
        Returns:
            GeneratedAudio object
            
        Example:
            >>> audio = generator.generate_from_preset("rain_heavy")
        """
        if preset not in FOLEY_QUICK_PROMPTS:
            available = ", ".join(FOLEY_QUICK_PROMPTS.keys())
            raise ValueError(
                f"Unknown preset: {preset}. Available: {available}"
            )
        
        prompt = FOLEY_QUICK_PROMPTS[preset]
        return self.generate(prompt, duration=duration, **kwargs)
    
    @staticmethod
    def list_presets() -> dict[str, str]:
        """Return all available foley presets."""
        return FOLEY_QUICK_PROMPTS.copy()
