"""
Audio utility classes and functions for handling generated audio.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union
import numpy as np
import soundfile as sf
import torch
import torchaudio

@dataclass
class GeneratedAudio:
    """
    Class for generated audio.
    
    Attributes:
        waveform: Audio waveform as numpy array or torch tensor
        sample_rate: Sample rate in Hz
        prompt: The prompt used to generate this audio
        metadata: Additional generation metadata
    """
    
    waveform: Union[np.ndarray, "torch.Tensor"]
    sample_rate: int
    prompt: str = ""
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Convert torch tensor to numpy if needed for consistency."""
        if isinstance(self.waveform, torch.Tensor):
            self._tensor = self.waveform
            self.waveform = self.waveform.cpu().numpy()
        else:
            self._tensor = None
    
    @property
    def duration(self) -> float:
        """Duration of the audio in seconds."""
        if self.waveform.ndim == 1:
            return len(self.waveform) / self.sample_rate
        return self.waveform.shape[-1] / self.sample_rate
    
    @property
    def num_channels(self) -> int:
        """Number of audio channels."""
        if self.waveform.ndim == 1:
            return 1
        return self.waveform.shape[0]
    
    def save(
        self,
        path: Union[str, Path],
        normalize: bool = True,
        target_loudness: float = -14.0,
    ) -> Path:
        """
        Save the audio to a file.
        
        Args:
            path: Output file path
            normalize: Apply loudness normalization
            target_loudness: Target LUFS for normalization (default: -14 LUFS)
            
        Returns:
            Path to the saved file
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Get audio data
        audio = self.waveform.copy()
        
        # Proper shape for soundfile (samples, channels)
        if audio.ndim == 1:
            audio = audio.reshape(-1, 1)
        elif audio.ndim == 2 and audio.shape[0] < audio.shape[1]:
            # (channels, samples) -> (samples, channels)
            audio = audio.T
        
        # Peak normalization
        if normalize:
            peak = np.abs(audio).max()
            if peak > 0:
                # Normalize to target dB below full scale
                target_peak = 10 ** (target_loudness / 20)
                audio = audio * (target_peak / peak)
               
        # Save
        sf.write(path, audio, self.sample_rate)
        
        return path
    
    def to_tensor(self) -> "torch.Tensor":
        """Convert to PyTorch tensor."""
        if self._tensor is not None:
            return self._tensor
        return torch.from_numpy(self.waveform)
    
   
    def fade_in_out(
        self,
        fade_in_duration: float = 0.01,
        fade_out_duration: float = 0.05
    ) -> "GeneratedAudio":
        """
        Apply fade in and fade out to avoid clicks.
        
        Args:
            fade_in_duration: Fade in duration in seconds
            fade_out_duration: Fade out duration in seconds
            
        Returns:
            New GeneratedAudio with fades applied
        """
        audio = self.waveform.copy()
        
        fade_in_samples = int(fade_in_duration * self.sample_rate)
        fade_out_samples = int(fade_out_duration * self.sample_rate)
        
        # Create fade curves
        fade_in = np.linspace(0, 1, fade_in_samples)
        fade_out = np.linspace(1, 0, fade_out_samples)
        
        if audio.ndim == 2:
            # Apply to all channels
            audio[:, :fade_in_samples] *= fade_in
            audio[:, -fade_out_samples:] *= fade_out
        else:
            audio[:fade_in_samples] *= fade_in
            audio[-fade_out_samples:] *= fade_out
        
        return GeneratedAudio(
            waveform=audio,
            sample_rate=self.sample_rate,
            prompt=self.prompt,
            metadata={**self.metadata, "fades_applied": True}
        )


def load_audio(path: Union[str, Path], target_sr: Optional[int] = None) -> GeneratedAudio:
    """
    Load audio from a file.
    
    Args:
        path: Path to the audio file
        target_sr: Target sample rate (resample if different)
        
    Returns:
        GeneratedAudio object
    """
    path = Path(path)
    
    audio, sr = sf.read(path)
    
    # Convert to (channels, samples) format
    if audio.ndim == 1:
        audio = audio.reshape(1, -1)
    elif audio.ndim == 2 and audio.shape[1] < audio.shape[0]:
        audio = audio.T
    
    # Resample if needed
    if target_sr is not None and sr != target_sr:
        audio_tensor = torch.from_numpy(audio).float()
        resampler = torchaudio.transforms.Resample(sr, target_sr)
        audio = resampler(audio_tensor).numpy()
        sr = target_sr
    
    return GeneratedAudio(
        waveform=audio.squeeze(),
        sample_rate=sr,
        metadata={"source_file": str(path)}
    )

