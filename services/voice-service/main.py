import os
import sys
import json
import uuid
import asyncio
import structlog
from datetime import datetime, timezone
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db, engine
from models import VoiceSession
from config import ENVIRONMENT, CONVERSATION_SERVICE_URL
from stt_engine import stt_engine
from tts_engine import tts_engine
from wakeword_engine import wakeword_detector
from speaker_id import speaker_identifier
import httpx

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)
logger = structlog.get_logger()

app = FastAPI(
    title="Voice Streaming Gateway Service",
    description="Real-time voice streaming, STT, TTS, and wake-word gateway for AI Assistant",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def fetch_conversation_reply(user_message: str, conversation_id: str | None = None) -> str:
    """Fetch response from conversation-service with fallback."""
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(
                f"{CONVERSATION_SERVICE_URL}/v1/test/chat",
                json={"message": user_message, "conversation_id": conversation_id},
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("reply", "I am here to assist you.")
    except Exception as e:
        logger.warning("conversation_service_call_failed", error=str(e))

    # Graceful fallback response when conversation-service is not directly reachable in test mode
    return f"I heard you say: {user_message}. How can I help further?"


@app.get("/healthz", tags=["Health"])
async def healthz():
    return {"status": "ok", "service": "voice-service", "version": "1.1.0"}


@app.get("/readyz", tags=["Health"])
async def readyz(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        logger.error("readyz_check_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed",
        )


@app.get("/v1/voice/devices", tags=["Voice"])
async def list_voice_devices(db: Session = Depends(get_db)):
    """List distinct registered voice devices recorded in voice sessions."""
    rows = db.query(VoiceSession.device_id).distinct().all()
    devices = [r[0] for r in rows if r[0]]
    return {"devices": devices, "count": len(devices)}


@app.websocket("/ws/voice-stream")
async def voice_stream_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    """
    Bidirectional WebSocket endpoint for voice streaming, live STT, and streaming TTS.
    Supports binary audio chunks (PCM/WAV) and JSON control messages.
    """
    await websocket.accept()
    session_id = str(uuid.uuid4())
    device_id = websocket.query_params.get("device_id", "default_mic")
    speaker_id = websocket.query_params.get("speaker_id", None)
    language_hint = websocket.query_params.get("language", None)
    default_voice = "bn_BD" if language_hint == "bn" else "en_US-lessac-medium"

    # In-memory audio buffer for streaming STT
    audio_buffer = bytearray()

    # Register voice session in DB
    voice_session = VoiceSession(
        id=uuid.UUID(session_id),
        device_id=device_id,
        speaker_id=speaker_id,
        status="active",
    )
    db.add(voice_session)
    db.commit()

    logger.info("voice_ws_connected", session_id=session_id, device_id=device_id)

    # Send initial connection ACK
    await websocket.send_json({
        "type": "connection_ack",
        "session_id": session_id,
        "status": "connected",
        "message": "Voice stream WebSocket connected successfully.",
    })

    try:
        while True:
            message = await websocket.receive()
            if "text" in message and message["text"]:
                data = json.loads(message["text"])
                msg_type = data.get("type", "unknown")
                logger.info("voice_ws_text_received", session_id=session_id, msg_type=msg_type)

                if msg_type == "ping":
                    await websocket.send_json({"type": "pong", "session_id": session_id})

                elif msg_type == "echo":
                    await websocket.send_json({
                        "type": "echo_response",
                        "session_id": session_id,
                        "payload": data.get("payload", ""),
                    })

                elif msg_type == "barge_in_interrupt":
                    # Client explicitly signaled barge-in interruption during AI speech
                    logger.info("barge_in_interrupted_by_client", session_id=session_id)
                    voice_session.status = "interrupted"
                    db.commit()
                    await websocket.send_json({
                        "type": "barge_in_triggered",
                        "session_id": session_id,
                        "status": "playback_cancelled",
                    })

                elif msg_type in ("commit_audio", "flush_stt"):
                    # Process accumulated buffer with STT and Speaker ID
                    transcript_text = ""
                    lang = "unknown"
                    identified_speaker = speaker_id or "unknown"
                    speaker_conf = 0.0

                    if len(audio_buffer) > 0:
                        loop = asyncio.get_event_loop()
                        pcm_snapshot = bytes(audio_buffer)
                        
                        # 1. STT
                        result = await loop.run_in_executor(
                            None,
                            lambda: stt_engine.transcribe_pcm_bytes(pcm_snapshot, language=language_hint),
                        )
                        transcript_text = result["text"]
                        lang = result["language"]

                        # 2. Speaker Identification (Task 47)
                        spk_info = await loop.run_in_executor(
                            None,
                            lambda: speaker_identifier.identify_speaker(pcm_snapshot),
                        )
                        identified_speaker = spk_info["speaker_id"]
                        speaker_conf = spk_info["confidence"]

                        # Update voice_session in DB
                        voice_session.speaker_id = identified_speaker
                        db.commit()

                        await websocket.send_json({
                            "type": "transcript",
                            "session_id": session_id,
                            "text": transcript_text,
                            "language": lang,
                            "language_probability": result["language_probability"],
                            "duration": result["duration"],
                            "speaker_id": identified_speaker,
                            "speaker_confidence": speaker_conf,
                            "is_final": True,
                        })
                    else:
                        await websocket.send_json({
                            "type": "transcript",
                            "session_id": session_id,
                            "text": "",
                            "language": "unknown",
                            "language_probability": 0.0,
                            "duration": 0.0,
                            "speaker_id": identified_speaker,
                            "speaker_confidence": 0.0,
                            "is_final": True,
                        })

                    # If auto_respond requested or non-empty transcript, trigger conversation & TTS
                    if data.get("auto_respond", False) and transcript_text:
                        reply = await fetch_conversation_reply(transcript_text)
                        await websocket.send_json({
                            "type": "llm_reply",
                            "session_id": session_id,
                            "reply_text": reply,
                        })
                        voice_to_use = "bn_BD" if lang == "bn" else default_voice
                        # Stream TTS audio chunks
                        for chunk in tts_engine.stream_audio_chunks(reply, voice_name=voice_to_use, chunk_size=4096):
                            await websocket.send_bytes(chunk)

                        await websocket.send_json({
                            "type": "tts_completed",
                            "session_id": session_id,
                            "reply_text": reply,
                        })

                elif msg_type == "synthesize_text":
                    # Directly trigger TTS for provided text
                    text_to_speak = data.get("text", "")
                    voice_choice = data.get("voice", default_voice)
                    logger.info("synthesizing_text_for_ws", session_id=session_id, text=text_to_speak, voice=voice_choice)

                    await websocket.send_json({
                        "type": "tts_started",
                        "session_id": session_id,
                        "text": text_to_speak,
                        "voice": voice_choice,
                    })

                    # Stream synthesized audio chunks
                    total_bytes_sent = 0
                    for audio_chunk in tts_engine.stream_audio_chunks(text_to_speak, voice_name=voice_choice, chunk_size=4096):
                        await websocket.send_bytes(audio_chunk)
                        total_bytes_sent += len(audio_chunk)

                    await websocket.send_json({
                        "type": "tts_completed",
                        "session_id": session_id,
                        "total_bytes": total_bytes_sent,
                    })

                elif msg_type == "clear_buffer":
                    audio_buffer.clear()
                    await websocket.send_json({"type": "buffer_cleared", "session_id": session_id})

                elif msg_type == "end_session":
                    break

                else:
                    await websocket.send_json({
                        "type": "ack",
                        "session_id": session_id,
                        "received_type": msg_type,
                    })

            elif "bytes" in message and message["bytes"]:
                raw_audio = message["bytes"]
                audio_buffer.extend(raw_audio)
                logger.info("voice_ws_binary_received", session_id=session_id, chunk_size=len(raw_audio), total_buffer_len=len(audio_buffer))

                # Task 45: Live Wake-Word scanning on incoming audio frame
                ww_info = wakeword_detector.process_pcm_chunk(raw_audio)
                if ww_info["detected"]:
                    await websocket.send_json({
                        "type": "wakeword_detected",
                        "session_id": session_id,
                        "wake_word": ww_info["wake_word"],
                        "confidence": ww_info["confidence"],
                    })

                # If buffer has accumulated enough audio (e.g. >= 1 sec of 16kHz audio = 32000 bytes)
                if len(audio_buffer) >= 32000 and (len(audio_buffer) % 32000 == 0):
                    loop = asyncio.get_event_loop()
                    pcm_snapshot = bytes(audio_buffer)
                    partial_result = await loop.run_in_executor(
                        None,
                        lambda: stt_engine.transcribe_pcm_bytes(pcm_snapshot, language=language_hint),
                    )
                    await websocket.send_json({
                        "type": "transcript",
                        "session_id": session_id,
                        "text": partial_result["text"],
                        "language": partial_result["language"],
                        "language_probability": partial_result["language_probability"],
                        "duration": partial_result["duration"],
                        "is_final": False,
                    })
                else:
                    await websocket.send_json({
                        "type": "audio_ack",
                        "session_id": session_id,
                        "bytes_received": len(raw_audio),
                        "total_buffered": len(audio_buffer),
                    })

    except WebSocketDisconnect:
        logger.info("voice_ws_disconnected", session_id=session_id)
    except Exception as e:
        logger.error("voice_ws_error", session_id=session_id, error=str(e))
    finally:
        # Mark session as ended in DB
        try:
            voice_session.ended_at = datetime.now(timezone.utc)
            voice_session.status = "ended"
            db.commit()
        except Exception:
            pass
        logger.info("voice_session_closed", session_id=session_id)
