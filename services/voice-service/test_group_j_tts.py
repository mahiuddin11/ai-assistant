import os
import sys
import wave
from fastapi.testclient import TestClient

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.append(os.path.dirname(__file__))
from main import app
from tts_engine import tts_engine


def test_task_42_english_tts():
    print("=" * 60)
    print("1. Testing Task 42: English Text-to-Speech (Piper)")
    print("=" * 60)
    en_text = "Good morning! Your voice streaming pipeline is operating with low latency."
    pcm_bytes, sr = tts_engine.synthesize_pcm(en_text, voice_name="en_US-lessac-medium")
    print(f"Synthesized '{en_text[:40]}...' -> {len(pcm_bytes)} PCM bytes @ {sr}Hz")
    assert len(pcm_bytes) > 5000
    assert sr > 8000
    print("[PASS] Task 42 English TTS Verified!\n")


def test_task_43_bengali_tts():
    print("=" * 60)
    print("2. Testing Task 43: Bengali Text-to-Speech (Piper Bengali Voice)")
    print("=" * 60)
    bn_text = "শুভ সকাল! আপনার ভয়েস অ্যাসিস্ট্যান্ট সেবা দেওয়ার জন্য প্রস্তুত।"
    pcm_bytes, sr = tts_engine.synthesize_pcm(bn_text, voice_name="bn_BD")
    print(f"Synthesized '{bn_text[:40]}...' -> {len(pcm_bytes)} PCM bytes @ {sr}Hz")
    assert len(pcm_bytes) > 5000
    assert sr > 8000
    print("[PASS] Task 43 Bengali TTS Verified!\n")


def test_task_44_websocket_tts_streaming():
    print("=" * 60)
    print("3. Testing Task 44: WebSocket Real-Time TTS Streaming (/ws/voice-stream)")
    print("=" * 60)
    client = TestClient(app)

    with client.websocket_connect("/ws/voice-stream?device_id=test_speaker_device") as ws:
        ack = ws.receive_json()
        print("Connected ACK:", ack)
        assert ack["type"] == "connection_ack"

        # Request direct text synthesis via WebSocket
        ws.send_json({
            "type": "synthesize_text",
            "text": "Your automated build succeeded.",
            "voice": "en_US-lessac-medium",
        })

        # Expect tts_started
        start_event = ws.receive_json()
        print("TTS Started Event:", start_event)
        assert start_event["type"] == "tts_started"

        # Receive streamed audio binary frames until tts_completed
        received_audio_bytes = 0
        while True:
            msg = ws.receive()
            if "bytes" in msg and msg["bytes"]:
                received_audio_bytes += len(msg["bytes"])
            elif "text" in msg and msg["text"]:
                data = ws.receive_json() if False else eval(msg["text"])
                if data.get("type") == "tts_completed":
                    print("TTS Completed Event:", data)
                    assert data["type"] == "tts_completed"
                    break

        print(f"Total TTS audio received via WebSocket stream: {received_audio_bytes} bytes.")
        assert received_audio_bytes > 5000

        ws.send_json({"type": "end_session"})

    print("[PASS] Task 44 WebSocket TTS Streaming Verified!\n")


if __name__ == "__main__":
    test_task_42_english_tts()
    test_task_43_bengali_tts()
    test_task_44_websocket_tts_streaming()
    print("=" * 60)
    print("ALL GROUP J (TASKS 42, 43, 44) TESTS PASSED (100% COMPLETE)")
    print("=" * 60)
