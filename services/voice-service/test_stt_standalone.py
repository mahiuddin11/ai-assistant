import os
import sys
import wave
import struct
import math
import numpy as np

sys.path.append(os.path.dirname(__file__))
from stt_engine import STTEngine


def generate_synthetic_speech_wav(output_path: str, duration_sec: float = 2.0, sample_rate: int = 16000):
    """
    Generate a formatted 16kHz Mono 16-bit PCM WAV file with modulated voice-like frequencies for standalone pipeline testing.
    """
    num_samples = int(sample_rate * duration_sec)
    wav_file = wave.open(output_path, "wb")
    wav_file.setnchannels(1)  # Mono
    wav_file.setsampwidth(2)  # 16-bit
    wav_file.setframerate(sample_rate)

    raw_frames = bytearray()
    for i in range(num_samples):
        t = float(i) / sample_rate
        # Multi-harmonic voice formant simulation
        value = (
            0.5 * math.sin(2.0 * math.pi * 220.0 * t) +
            0.3 * math.sin(2.0 * math.pi * 440.0 * t) +
            0.2 * math.sin(2.0 * math.pi * 880.0 * t)
        )
        # Apply amplitude envelope (fade-in & fade-out)
        envelope = math.sin(math.pi * (i / num_samples))
        sample_val = int(value * envelope * 24000.0)
        raw_frames.extend(struct.pack("<h", max(-32768, min(32767, sample_val))))

    wav_file.writeframes(raw_frames)
    wav_file.close()
    return raw_frames


def main():
    print("=" * 60)
    print("Task 39: Standalone faster-whisper STT Engine Test")
    print("=" * 60)

    engine = STTEngine(model_size="tiny", device="cpu", compute_type="int8")

    test_wav = os.path.join(os.path.dirname(__file__), "test_speech_sample.wav")
    print(f"1. Generating test WAV audio: {test_wav}")
    pcm_bytes = generate_synthetic_speech_wav(test_wav, duration_sec=2.0)
    print(f"   Generated WAV file ({os.path.getsize(test_wav)} bytes).")

    print("\n2. Testing transcribe_file()...")
    res_file = engine.transcribe_file(test_wav)
    print("   Transcription Output:", res_file)
    assert "duration" in res_file
    assert res_file["duration"] > 0
    print("   [PASS] transcribe_file() executed successfully on CPU int8.")

    print("\n3. Testing in-memory transcribe_pcm_bytes()...")
    res_bytes = engine.transcribe_pcm_bytes(bytes(pcm_bytes))
    print("   PCM Transcription Output:", res_bytes)
    assert "language" in res_bytes
    print("   [PASS] transcribe_pcm_bytes() executed successfully.")

    # Clean up test file
    if os.path.exists(test_wav):
        os.remove(test_wav)

    print("\n" + "=" * 60)
    print("TASK 39 (faster-whisper Standalone STT): VERIFIED & PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
