import os
import sys
import wave

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.append(os.path.dirname(__file__))
from tts_engine import tts_engine


def test_english_tts():
    print("=" * 60)
    print("Task 42: English Text-to-Speech (TTS) Test")
    print("=" * 60)
    en_text = "Hello! I am your AI assistant, ready to assist you today."
    en_wav = os.path.join(os.path.dirname(__file__), "test_en_speech.wav")

    print(f"Synthesizing English text: '{en_text}'")
    tts_engine.synthesize_wav(en_text, en_wav, voice_name="en_US-lessac-medium")

    assert os.path.exists(en_wav)
    with wave.open(en_wav, "rb") as wf:
        n_channels = wf.getnchannels()
        sr = wf.getframerate()
        n_frames = wf.getnframes()
        duration = n_frames / float(sr)

    print(f"   Generated WAV: {en_wav}")
    print(f"   Channels: {n_channels}, Sample Rate: {sr} Hz, Duration: {duration:.2f}s, Size: {os.path.getsize(en_wav)} bytes")
    assert duration > 1.0
    assert os.path.getsize(en_wav) > 10000

    if os.path.exists(en_wav):
        os.remove(en_wav)
    print("[PASS] Task 42 English TTS Verified!\n")


def test_bengali_tts():
    print("=" * 60)
    print("Task 43: Bengali Text-to-Speech (TTS) Test")
    print("=" * 60)
    bn_text = "হ্যালো! আমি আপনার এআই সহকারী, আপনাকে কীভাবে সাহায্য করতে পারি?"
    bn_wav = os.path.join(os.path.dirname(__file__), "test_bn_speech.wav")

    print(f"Synthesizing Bengali text: '{bn_text}'")
    tts_engine.synthesize_wav(bn_text, bn_wav, voice_name="bn_BD")

    assert os.path.exists(bn_wav)
    with wave.open(bn_wav, "rb") as wf:
        n_channels = wf.getnchannels()
        sr = wf.getframerate()
        n_frames = wf.getnframes()
        duration = n_frames / float(sr)

    print(f"   Generated WAV: {bn_wav}")
    print(f"   Channels: {n_channels}, Sample Rate: {sr} Hz, Duration: {duration:.2f}s, Size: {os.path.getsize(bn_wav)} bytes")
    assert duration > 1.0
    assert os.path.getsize(bn_wav) > 10000

    if os.path.exists(bn_wav):
        os.remove(bn_wav)
    print("[PASS] Task 43 Bengali TTS Verified!\n")


if __name__ == "__main__":
    test_english_tts()
    test_bengali_tts()
    print("=" * 60)
    print("ALL TTS VOICE TESTS (TASKS 42 & 43) PASSED (100% COMPLETE)")
    print("=" * 60)
