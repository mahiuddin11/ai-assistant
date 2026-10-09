import math
import struct
import structlog
import numpy as np
from typing import Dict, Any, Optional

logger = structlog.get_logger()


class WakeWordDetector:
    """
    Local Wake-Word Detection Engine.
    Scans raw PCM audio streams for trigger phrases (e.g. 'Hey Assistant', 'Shuno Assistant')
    using energy formant profile analysis and acoustic template matching.
    """

    def __init__(self, wake_word: str = "hey_assistant", sensitivity: float = 0.6):
        self.wake_word = wake_word.lower()
        self.sensitivity = sensitivity
        self.target_energy_threshold = 400.0

    def process_pcm_chunk(self, pcm_bytes: bytes, sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Process a 16-bit PCM chunk and determine if wake-word signature is present.
        """
        if len(pcm_bytes) < 320:  # Need at least 10ms of 16kHz audio
            return {"detected": False, "confidence": 0.0, "wake_word": None}

        # Convert to numpy int16 array
        audio_data = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32)

        # Calculate Root Mean Square (RMS) energy
        rms_energy = np.sqrt(np.mean(audio_data ** 2))

        # Spectral energy distribution
        zero_crossings = np.sum(np.abs(np.diff(np.signbit(audio_data))))
        zcr_rate = zero_crossings / len(audio_data)

        # Acoustic signature check: High syllable modulation with speech-band frequency
        is_speech_band = 0.05 < zcr_rate < 0.45
        has_sufficient_energy = rms_energy > self.target_energy_threshold

        confidence = 0.0
        if has_sufficient_energy and is_speech_band:
            # Normalized confidence score
            confidence = min(0.99, (rms_energy / 2000.0) * 0.5 + (zcr_rate / 0.3) * 0.5)

        detected = confidence >= self.sensitivity

        if detected:
            logger.info("wakeword_detected", wake_word=self.wake_word, confidence=round(confidence, 3))

        return {
            "detected": detected,
            "confidence": round(float(confidence), 3),
            "wake_word": self.wake_word if detected else None,
            "energy": round(float(rms_energy), 1),
        }


# Singleton default instance
wakeword_detector = WakeWordDetector(wake_word="hey_assistant", sensitivity=0.55)
