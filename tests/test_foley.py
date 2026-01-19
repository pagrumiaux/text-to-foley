"""
Tests for Text to foley.

Run with: pytest tests/ -v
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch

from text_to_foley.prompts import (
    enhance_prompt,
    suggest_prompt_improvements,
    FoleyCategory,
    FOLEY_QUICK_PROMPTS,
)
from text_to_foley.audio import GeneratedAudio


class TestPromptEnhancement:
    """Tests for prompt enhancement functionality."""
    
    def test_enhance_basic_prompt(self):
        """Enhancing a basic prompt adds quality descriptors."""
        result = enhance_prompt("footsteps")
        assert "high quality" in result.lower() or "clear" in result.lower()
    
    def test_enhance_already_detailed_prompt(self):
        """Detailed prompts don't get redundant additions."""
        detailed = "footsteps on wooden floor, slow pace, close-up recording, high quality"
        result = enhance_prompt(detailed)
        # Should not double up on quality terms
        assert result.count("high quality") <= 1
    
    def test_enhance_with_category(self):
        """Category-specific enhancement works."""
        result = enhance_prompt("walking", category=FoleyCategory.FOOTSTEPS)
        assert len(result) > len("walking")
    
    def test_enhance_preserves_original(self):
        """Original prompt content is preserved."""
        original = "glass breaking loudly"
        result = enhance_prompt(original)
        assert "glass" in result.lower()
        assert "breaking" in result.lower()


class TestPromptSuggestions:
    """Tests for prompt improvement suggestions."""
    
    def test_vague_prompt_gets_suggestions(self):
        """Vague prompts receive improvement suggestions."""
        suggestions = suggest_prompt_improvements("sound")
        assert len(suggestions) > 0
    
    def test_detailed_prompt_fewer_suggestions(self):
        """Well-crafted prompts get fewer suggestions."""
        detailed = "footsteps on wooden floor, slow walking pace, indoor close-up"
        suggestions = suggest_prompt_improvements(detailed)
        # Should have fewer suggestions than a vague prompt
        vague_suggestions = suggest_prompt_improvements("noise")
        assert len(suggestions) <= len(vague_suggestions)
    
    def test_missing_material_detected(self):
        """Missing material in action prompts is flagged."""
        suggestions = suggest_prompt_improvements("footsteps walking")
        material_suggestion = any("material" in s.lower() or "surface" in s.lower() 
                                  for s in suggestions)
        assert material_suggestion
    
    def test_short_prompt_warning(self):
        """Very short prompts get length warnings."""
        suggestions = suggest_prompt_improvements("door")
        assert any("short" in s.lower() or "detail" in s.lower() for s in suggestions)


class TestQuickPrompts:
    """Tests for the quick prompt shortcuts."""
    
    def test_quick_prompts_exist(self):
        """Quick prompts dictionary is populated."""
        assert len(FOLEY_QUICK_PROMPTS) > 0
    
    def test_quick_prompts_are_detailed(self):
        """Quick prompts contain sufficient detail."""
        for key, prompt in FOLEY_QUICK_PROMPTS.items():
            assert len(prompt.split()) >= 3, f"Prompt '{key}' too short: {prompt}"
    
    def test_quick_prompt_categories(self):
        """Quick prompts cover common foley categories."""
        keys = list(FOLEY_QUICK_PROMPTS.keys())
        categories = [k.split('_')[0] for k in keys]
        
        expected_categories = ['walk', 'door', 'rain', 'office']
        for expected in expected_categories:
            assert any(expected in cat for cat in categories), \
                f"Missing category: {expected}"


class TestGeneratedAudio:
    """Tests for the GeneratedAudio class."""
    
    @pytest.fixture
    def sample_audio(self):
        """Create a sample audio for testing."""
        # 1 second of sine wave at 440Hz
        sr = 16000
        duration = 1.0
        t = np.linspace(0, duration, int(sr * duration))
        waveform = np.sin(2 * np.pi * 440 * t).astype(np.float32)
        return GeneratedAudio(waveform=waveform, sample_rate=sr, prompt="test")
    
    def test_duration_calculation(self, sample_audio):
        """Duration is calculated correctly."""
        assert abs(sample_audio.duration - 1.0) < 0.01
    
    def test_num_channels_mono(self, sample_audio):
        """Channel count is correct for mono."""
        assert sample_audio.num_channels == 1
    
    def test_num_channels_stereo(self):
        """Channel count is correct for stereo."""
        stereo = np.random.randn(2, 16000).astype(np.float32)
        audio = GeneratedAudio(waveform=stereo, sample_rate=16000)
        assert audio.num_channels == 2
    
    def test_fade_in_out(self, sample_audio):
        """Fade in/out is applied correctly."""
        faded = sample_audio.fade_in_out(fade_in_duration=0.1, fade_out_duration=0.1)
        
        # Check that start is faded (should be near zero)
        assert abs(faded.waveform[0]) < 0.1
        # Check that end is faded
        assert abs(faded.waveform[-1]) < 0.1
        
    def test_to_tensor(self, sample_audio):
        """Conversion to tensor works."""
        import torch
        tensor = sample_audio.to_tensor()
        assert isinstance(tensor, torch.Tensor)
        assert tensor.shape[-1] == len(sample_audio.waveform)

class TestFoleyGenerator:
    """Tests for the main FoleyGenerator class (mocked model)."""

    @patch('audiocraft.models.AudioGen')
    def test_generator_initialization(self, mock_audiogen):
        """Generator initializes correctly."""
        from text_to_foley import FoleyGenerator

        generator = FoleyGenerator(device="cpu")
        assert generator.device == "cpu"
        assert generator._model is None  # Lazy loading

    @patch('audiocraft.models.AudioGen')
    def test_generator_device_detection(self, mock_audiogen):
        """Device auto-detection works."""
        from text_to_foley import FoleyGenerator
        import torch

        generator = FoleyGenerator()

        # Should pick an available device
        assert generator.device in ["cuda", "mps", "cpu"]
    
    def test_list_presets(self):
        """list_presets returns expected content."""
        from text_to_foley import FoleyGenerator
        
        presets = FoleyGenerator.list_presets()
        assert isinstance(presets, dict)
        assert len(presets) > 0
        assert "rain_heavy" in presets


# Integration test marker - only run if audiocraft is available
@pytest.mark.integration
class TestIntegration:
    """Integration tests that require the actual model."""
    
    @pytest.fixture(scope="class")
    def generator(self):
        """Shared generator for integration tests."""
        try:
            from text_to_foley import FoleyGenerator
            return FoleyGenerator()
        except ImportError:
            pytest.skip("AudioCraft not installed")
    
    def test_generate_short_audio(self, generator):
        """Can generate a short audio clip."""
        audio = generator.generate(
            prompt="footsteps on wood",
            duration=1.0
        )
        
        assert audio.duration > 0.5
        assert audio.sample_rate == 16000
    
    def test_generate_with_preset(self, generator):
        """Can generate from preset."""
        audio = generator.generate_from_preset("rain_light", duration=2.0)
        assert audio.duration > 1.0
