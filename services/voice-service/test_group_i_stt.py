import os
import sys
import uuid
import math
import struct
import wave

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient

# Local imports
sys.path.append(os.path.dirname(__file__))
from main import app
from stt_engine import stt_engine
from test_stt_standalone import generate_synthetic_speech_wav
from benchmark_stt_wer import run_wer_benchmarks


def test_task_39_standalone_stt():
    print("=" * 60)
    print("1. Testing Task 39: Standalone faster-whisper STT")
    print("=" * 60)
    wav_path = os.path.join(os.path.dirname(__file__), "test_t39.wav")
    pcm_bytes = generate_synthetic_speech_wav(wav_path, duration_sec=1.5)

    res = stt_engine.transcribe_file(wav_path)
    print("File transcription:", res)
    assert "duration" in res
    assert res["duration"] > 0

    res_pcm = stt_engine.transcribe_pcm_bytes(bytes(pcm_bytes))
    print("PCM transcription:", res_pcm)
    assert "language" in res_pcm

    if os.path.exists(wav_path):
        os.remove(wav_path)
    print("[PASS] Task 39 Standalone STT Verified!\n")


def test_task_40_streaming_stt_websocket():
    print("=" * 60)
    print("2. Testing Task 40: WebSocket Streaming STT (/ws/voice-stream)")
    print("=" * 60)
    client = TestClient(app)

    with client.websocket_connect("/ws/voice-stream?device_id=mic_stream_01") as ws:
        # Handshake
        ack = ws.receive_json()
        print("Connected ACK:", ack)
        assert ack["type"] == "connection_ack"

        # Stream 16000 samples (1 sec) in 4 chunks of 4000 samples (8000 bytes each)
        chunk_size = 8000
        for chunk_idx in range(4):
            # Formant audio chunk
            raw_chunk = bytearray()
            for i in range(2000):
                sample_val = int(math.sin(2.0 * math.pi * 300.0 * (i / 16000.0)) * 16000.0)
                raw_chunk.extend(struct.pack("<h", sample_val))

            ws.send_bytes(bytes(raw_chunk))
            audio_ack = ws.receive_json()
            print(f"Chunk {chunk_idx+1} ACK:", audio_ack)
            assert audio_ack["type"] in ("audio_ack", "transcript")

        # Commit audio to trigger final STT transcription
        ws.send_json({"type": "commit_audio"})
        transcript_res = ws.receive_json()
        print("Transcript Event:", transcript_res)
        assert transcript_res["type"] == "transcript"
        assert transcript_res["is_final"] is True
        assert "language" in transcript_res

        # End session
        ws.send_json({"type": "end_session"})

    print("[PASS] Task 40 WebSocket Streaming STT Verified!\n")


def test_task_41_wer_benchmarks():
    print("=" * 60)
    print("3. Testing Task 41: WER Benchmark Suite & Report Generation")
    print("=" * 60)
    bench_results = run_wer_benchmarks()
    assert len(bench_results) >= 5

    report_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "docs", "benchmarks", "stt_wer_report.md"))
    assert os.path.exists(report_path), f"Report not found at {report_path}"
    print(f"[PASS] Task 41 Benchmark Report Verified at: {report_path}\n")


if __name__ == "__main__":
    test_task_39_standalone_stt()
    test_task_40_streaming_stt_websocket()
    test_task_41_wer_benchmarks()
    print("=" * 60)
    print("ALL GROUP I (TASKS 39, 40, 41) TESTS PASSED (100% COMPLETE)")
    print("=" * 60)
