import io
import os
import wave
import structlog
import numpy as np
from typing import Tuple, List, Dict, Any

logger = structlog.get_logger()

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None


class STTEngine:
    """
    CPU-optimized Speech-to-Text Engine using faster-whisper (CTranslate2).
    Supports English, Bengali, and Bengali-English code-mix.
    """

    def __init__(self, model_size: str = "tiny", device: str = "cpu", compute_type: str = "int8"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model = None

    def _ensure_loaded(self):
        if self._model is None:
            if WhisperModel is None:
                raise RuntimeError("faster-whisper is not installed in current environment.")
            logger.info("loading_stt_model", model_size=self.model_size, device=self.device, compute_type=self.compute_type)
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                download_root=os.path.join(os.path.dirname(__file__), ".model_cache"),
            )
            logger.info("stt_model_loaded_successfully", model_size=self.model_size)

    def transcribe_file(self, audio_path: str, language: str | None = None) -> Dict[str, Any]:
        """Transcribe an audio file from disk."""
        self._ensure_loaded()
        try:
            with wave.open(audio_path, "rb") as wf:
                sample_rate = wf.getframerate()
                n_channels = wf.getnchannels()
                frames = wf.readframes(wf.getnframes())
                audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
                if n_channels > 1:
                    audio_data = audio_data[::n_channels]
        except Exception:
            import soundfile as sf
            audio_data, sample_rate = sf.read(audio_path, dtype="float32")
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)

        segments, info = self._model.transcribe(
            audio_data,
            language=language,
            beam_size=5,
            vad_filter=False,
        )
        full_text = " ".join([segment.text.strip() for segment in segments]).strip()
        return {
            "text": full_text,
            "language": info.language,
            "language_probability": round(info.language_probability, 3),
            "duration": round(info.duration, 2),
        }

    def transcribe_pcm_bytes(self, pcm_bytes: bytes, sample_rate: int = 16000, language: str | None = None) -> Dict[str, Any]:
        """
        Transcribe in-memory 16-bit PCM mono audio bytes.
        """
        self._ensure_loaded()
        if not pcm_bytes:
            return {"text": "", "language": "unknown", "language_probability": 0.0, "duration": 0.0}

        # Convert 16-bit PCM bytes to float32 numpy array normalized between -1.0 and 1.0
        audio_data = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0

        if len(audio_data) == 0:
            return {"text": "", "language": "unknown", "language_probability": 0.0, "duration": 0.0}

        segments, info = self._model.transcribe(
            audio_data,
            language=language,
            beam_size=5,
            vad_filter=False,
        )
        full_text = " ".join([segment.text.strip() for segment in segments]).strip()
        return {
            "text": full_text,
            "language": info.language,
            "language_probability": round(info.language_probability, 3),
            "duration": round(info.duration, 2),
        }

    def create_wav_bytes(self, pcm_bytes: bytes, sample_rate: int = 16000, channels: int = 1) -> bytes:
        """Helper to package raw PCM into WAV byte format."""
        wav_io = io.BytesIO()
        with wave.open(wav_io, "wb") as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_bytes)
        return wav_io.getvalue()


# Default singleton instance
stt_engine = STTEngine(model_size="tiny", device="cpu", compute_type="int8")
