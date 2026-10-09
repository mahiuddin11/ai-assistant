import sys
import os
import asyncio
import json
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import text

# Add packages and local path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "packages", "config-loader")))
sys.path.append(os.path.dirname(__file__))

from main import app
from database import SessionLocal
from models import VoiceSession


def test_rest_endpoints():
    print("=" * 60)
    print("Testing Voice Service REST Endpoints")
    print("=" * 60)
    client = TestClient(app)

    # 1. Healthz
    r_health = client.get("/healthz")
    print(f"GET /healthz -> Status: {r_health.status_code}, Body: {r_health.json()}")
    assert r_health.status_code == 200
    assert r_health.json()["status"] == "ok"
    assert r_health.json()["service"] == "voice-service"

    # 2. Readyz
    r_ready = client.get("/readyz")
    print(f"GET /readyz -> Status: {r_ready.status_code}, Body: {r_ready.json()}")
    assert r_ready.status_code == 200
    assert r_ready.json()["status"] == "ready"

    # 3. Devices
    r_devices = client.get("/v1/voice/devices")
    print(f"GET /v1/voice/devices -> Status: {r_devices.status_code}, Body: {r_devices.json()}")
    assert r_devices.status_code == 200
    print("[PASS] REST endpoints verified successfully!\n")


def test_websocket_stream_and_db():
    print("=" * 60)
    print("Testing WebSocket /ws/voice-stream & voice_sessions DB persistence")
    print("=" * 60)
    client = TestClient(app)

    test_device_id = "test_headset_mic_101"
    session_id_recorded = None

    with client.websocket_connect(f"/ws/voice-stream?device_id={test_device_id}&speaker_id=user_01") as ws:
        # 1. Connection ACK
        ack = ws.receive_json()
        print("1. Received WS connection_ack:", ack)
        assert ack["type"] == "connection_ack"
        assert ack["status"] == "connected"
        session_id_recorded = ack["session_id"]

        # 2. Ping / Pong
        ws.send_json({"type": "ping"})
        pong = ws.receive_json()
        print("2. Received WS pong:", pong)
        assert pong["type"] == "pong"

        # 3. Echo test
        ws.send_json({"type": "echo", "payload": "Hello Voice Pipeline v1.1"})
        echo_res = ws.receive_json()
        print("3. Received WS echo_response:", echo_res)
        assert echo_res["type"] == "echo_response"
        assert echo_res["payload"] == "Hello Voice Pipeline v1.1"

        # 4. Binary audio chunk test
        dummy_pcm = b"\x00\x01\x02\x03" * 256  # 1024 bytes dummy audio
        ws.send_bytes(dummy_pcm)
        audio_ack = ws.receive_json()
        print("4. Received WS audio_ack:", audio_ack)
        assert audio_ack["type"] == "audio_ack"
        assert audio_ack["bytes_received"] == 1024

        # 5. End session
        ws.send_json({"type": "end_session"})

    # 6. Verify DB persistence in PostgreSQL voice_sessions table
    db = SessionLocal()
    try:
        vs = db.query(VoiceSession).filter(VoiceSession.id == uuid.UUID(session_id_recorded)).first()
        print("\n5. DB Verification:")
        print(f"   VoiceSession ID : {vs.id}")
        print(f"   Device ID       : {vs.device_id}")
        print(f"   Speaker ID      : {vs.speaker_id}")
        print(f"   Status          : {vs.status}")
        print(f"   Created At      : {vs.created_at}")
        print(f"   Ended At        : {vs.ended_at}")

        assert vs is not None
        assert vs.device_id == test_device_id
        assert vs.speaker_id == "user_01"
        assert vs.status == "ended"
        assert vs.ended_at is not None
        print("[PASS] WebSocket and DB persistence verified successfully!\n")
    finally:
        db.close()


if __name__ == "__main__":
    test_rest_endpoints()
    test_websocket_stream_and_db()
    print("=" * 60)
    print("ALL TESTS IN TASK 36, 37, 38 PASSED (100% COMPLETE)")
    print("=" * 60)
