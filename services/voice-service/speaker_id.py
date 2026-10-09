import structlog
import numpy as np
from typing import Dict, Any, Optional

logger = structlog.get_logger()


class SpeakerIdentifier:
    """
    Acoustic Voice-Print Feature Extraction and Multi-User Speaker Identification.
    Identifies distinct speakers in a shared device context based on pitch (F0) & spectral footprint.
    """

    def __init__(self):
        # Known enrolled speaker profiles (pitch signature in Hz and spectral centroid)
        self._profiles = {
            "speaker_lead_dev": {"f0_mean": 135.0, "f0_std": 18.0, "spectral_centroid": 1400.0},
            "speaker_assistant_user": {"f0_mean": 195.0, "f0_std": 25.0, "spectral_centroid": 2100.0},
            "speaker_guest": {"f0_mean": 240.0, "f0_std": 30.0, "spectral_centroid": 2600.0},
        }

    def extract_voiceprint(self, pcm_bytes: bytes, sample_rate: int = 16000) -> Dict[str, float]:
        """Extracts acoustic features from raw 16-bit mono PCM."""
        if len(pcm_bytes) < 1600:  # < 50ms audio
            return {"f0_mean": 0.0, "energy": 0.0, "spectral_centroid": 0.0}

        audio = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32)
        
        # Energy
        energy = float(np.mean(np.abs(audio)))

        # Autocorrelation for pitch estimation (F0)
        corr = np.correlate(audio, audio, mode="full")
        corr = corr[len(corr) // 2 :]

        # Look for pitch peak between 80Hz and 350Hz
        min_lag = int(sample_rate / 350.0)
        max_lag = int(sample_rate / 80.0)

        peak_lag = min_lag + np.argmax(corr[min_lag:max_lag])
        estimated_f0 = float(sample_rate / peak_lag) if peak_lag > 0 else 150.0

        # Spectral Centroid (frequency brightness)
        fft_mags = np.abs(np.fft.rfft(audio))
        freqs = np.fft.rfftfreq(len(audio), d=1.0 / sample_rate)
        sum_mags = np.sum(fft_mags)
        centroid = float(np.sum(freqs * fft_mags) / sum_mags) if sum_mags > 0 else 1500.0

        return {
            "f0_mean": round(estimated_f0, 1),
            "energy": round(energy, 1),
            "spectral_centroid": round(centroid, 1),
        }

    def identify_speaker(self, pcm_bytes: bytes, sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Identify speaker ID from PCM audio bytes.
        Returns matched speaker_id, similarity score, and voiceprint features.
        """
        features = self.extract_voiceprint(pcm_bytes, sample_rate=sample_rate)

        if features["energy"] < 50.0:
            return {
                "speaker_id": "unknown",
                "confidence": 0.0,
                "features": features,
            }

        best_speaker = "speaker_lead_dev"
        best_dist = float("inf")

        for speaker_id, profile in self._profiles.items():
            # Normalized Euclidean distance across pitch and spectral features
            pitch_diff = abs(features["f0_mean"] - profile["f0_mean"]) / 100.0
            centroid_diff = abs(features["spectral_centroid"] - profile["spectral_centroid"]) / 1500.0
            dist = pitch_diff * 0.7 + centroid_diff * 0.3

            if dist < best_dist:
                best_dist = dist
                best_speaker = speaker_id

        # Convert distance to confidence (0.0 to 1.0)
        confidence = max(0.5, min(0.98, 1.0 - (best_dist * 0.5)))

        logger.info(
            "speaker_identified",
            speaker_id=best_speaker,
            confidence=round(confidence, 3),
            f0_estimate=features["f0_mean"],
        )

        return {
            "speaker_id": best_speaker,
            "confidence": round(confidence, 3),
            "features": features,
        }


speaker_identifier = SpeakerIdentifier()
