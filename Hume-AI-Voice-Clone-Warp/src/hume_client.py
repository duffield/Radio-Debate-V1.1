import os
import base64
import json
import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict

import requests


@dataclass
class HumeConfig:
    api_key: Optional[str]
    secret_key: Optional[str]
    base_url: str = "https://api.hume.ai/v0"
    work_dir: str = "data"
    ws_url: Optional[str] = None  # e.g., wss://api.hume.ai/v0/realtime
    voice_clone_url: Optional[str] = None  # Full URL for voice cloning endpoint
    tts_url: Optional[str] = None          # Full URL for TTS/synthesis endpoint


class HumeClient:
    """
    Hume API client scaffolding.
    - Reads credentials from environment variables: HUME_API_KEY, HUME_SECRET_KEY
    - Endpoints are placeholders. Insert the correct Hume API endpoints or use the official SDK.
    """

    def __init__(self) -> None:
        self.cfg = HumeConfig(
            api_key=os.getenv("HUME_API_KEY"),
            secret_key=os.getenv("HUME_SECRET_KEY"),
            base_url=os.getenv("HUME_API_BASE_URL", "https://api.hume.ai/v0"),
            ws_url=os.getenv("HUME_WS_URL"),
            voice_clone_url=os.getenv("HUME_VOICE_CLONE_URL"),
            tts_url=os.getenv("HUME_TTS_URL"),
        )
        Path(self.cfg.work_dir).mkdir(parents=True, exist_ok=True)

        if not self.cfg.api_key or not self.cfg.secret_key:
            print("[WARN] HUME_API_KEY or HUME_SECRET_KEY not set; API calls will be skipped.")

    # ---------------------- Voice Cloning ----------------------
    def clone_voice_from_file(self, wav_path: str) -> Optional[str]:
        """
        Upload an audio sample and create a cloned voice.
        Returns a voice_id string on success.

        Note: The exact REST path varies by product/version. Provide HUME_VOICE_CLONE_URL
        (a full URL) in your environment to avoid 404s from placeholder paths.
        """
        if not (self.cfg.api_key and self.cfg.secret_key):
            return None

        url = self.cfg.voice_clone_url
        if not url:
            print(
                "[WARN] HUME_VOICE_CLONE_URL not set. Set it to your account's voice cloning endpoint to enable cloning."
            )
            return None

        headers = {
            "Authorization": f"Bearer {self.cfg.api_key}",
            "X-Hume-Secret-Key": self.cfg.secret_key,
        }

        # Use context manager to ensure the file handle is closed
        try:
            with open(wav_path, "rb") as fh:
                files = {"file": fh}
                resp = requests.post(url, headers=headers, files=files, timeout=60)
        except Exception as e:
            print(f"[ERROR] Voice cloning exception: {e}")
            return None

        if resp.status_code in (200, 201):
            try:
                data = resp.json()
            except Exception:
                print("[WARN] Voice clone response was not JSON.")
                return None
            voice_id = data.get("voice_id") or data.get("id")
            if not voice_id:
                print("[WARN] Voice clone response missing voice_id.")
            return voice_id
        else:
            print(f"[WARN] Voice clone request failed: {resp.status_code} {resp.text}")
            return None

    # ---------------------- TTS (Text -> Speech) ----------------------
    def synthesize_speech(self, text: str, voice_id: Optional[str]) -> Optional[str]:
        """
        Synthesize speech from text using a cloned voice and write a WAV to data/.
        Returns path to the WAV file, or None.

        Provide HUME_TTS_URL (full URL) to the correct TTS endpoint to avoid 404s.
        """
        if not (self.cfg.api_key and self.cfg.secret_key):
            return None
        if not text:
            return None

        url = self.cfg.tts_url
        if not url:
            print("[WARN] HUME_TTS_URL not set. Set it to the correct TTS endpoint to enable synthesis.")
            return None

        headers = {
            "Authorization": f"Bearer {self.cfg.api_key}",
            "X-Hume-Secret-Key": self.cfg.secret_key,
            "Content-Type": "application/json",
        }
        payload = {
            "text": text,
            "voice_id": voice_id,
            "format": "wav",  # adjust per API
            "sample_rate": 16000,
        }
        try:
            resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
        except Exception as e:
            print(f"[ERROR] TTS exception: {e}")
            return None

        if resp.status_code in (200, 201):
            try:
                data = resp.json()
            except Exception:
                print("[WARN] TTS response was not JSON.")
                return None
            b64_audio = data.get("audio") or data.get("audio_base64")
            if not b64_audio:
                print("[WARN] No audio returned in response.")
                return None
            try:
                audio_bytes = base64.b64decode(b64_audio)
            except Exception as e:
                print(f"[ERROR] Failed to decode audio: {e}")
                return None
            out_path = os.path.join(self.cfg.work_dir, "assistant_reply.wav")
            try:
                with open(out_path, "wb") as f:
                    f.write(audio_bytes)
            except Exception as e:
                print(f"[ERROR] Failed to write WAV file: {e}")
                return None
            return out_path
        else:
            print(f"[WARN] TTS request failed: {resp.status_code} {resp.text}")
            return None

    # ---------------------- Real-time Chat (WebSocket) ----------------------
    def start_realtime_chat(self, voice_id: Optional[str], output_device: Optional[str] = None, config_id: Optional[str] = None) -> None:
        """
        Streaming chat session using Hume.
        - If config_id is provided and the Hume SDK is available, prefer the SDK path (no WS URL needed).
        - Otherwise, fall back to the raw WebSocket scaffold using HUME_WS_URL.
        """
        if not (self.cfg.api_key and self.cfg.secret_key):
            print("[WARN] Missing credentials; cannot start real-time chat.")
            return

        # Try SDK-first if a config is provided and not explicitly disabled
        use_sdk = bool(config_id) and os.getenv("HUME_DISABLE_SDK", "0") not in {"1", "true", "TRUE"}
        if use_sdk and config_id:
            try:
                print(f"[INFO] Using Hume SDK realtime with config_id={config_id}")
                from sdk_realtime import HumeSDKVoiceChat
                chat = HumeSDKVoiceChat(
                    api_key=self.cfg.api_key,  # type: ignore[arg-type]
                    config_id=config_id,
                    sample_rate=16000,
                    channels=1,
                    frame_ms=20,
                    output_device=output_device or os.getenv("AUDIO_OUTPUT_DEVICE"),
                )
                asyncio.run(chat.run())
                return
            except Exception as e:
                print(f"[ERROR] SDK realtime failed: {e}")
                # Only fall back to raw WS if explicitly allowed
                if os.getenv("HUME_FALLBACK_WS", "0") not in {"1", "true", "TRUE"}:
                    print("[INFO] Not falling back to raw WebSocket. Set HUME_FALLBACK_WS=1 to enable fallback.")
                    return
                print("[WARN] Falling back to raw WebSocket scaffold...")

        # Fall back to raw WS if SDK not used/allowed
        if not self.cfg.ws_url:
            print("[WARN] HUME_WS_URL not set. Cannot start WebSocket realtime. Provide a valid WS URL or use SDK with HUME_CONFIG_ID.")
            return

        print(f"[INFO] Using raw WebSocket endpoint: {self.cfg.ws_url}")
        # Defer to the realtime helper so this client stays thin
        from realtime import RealTimeVoiceChat

        headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.cfg.api_key}",
            "X-Hume-Secret-Key": self.cfg.secret_key,
        }
        chat = RealTimeVoiceChat(
            ws_url=self.cfg.ws_url,
            headers=headers,
            voice_id=voice_id,
            config_id=config_id,
            sample_rate=16000,
            channels=1,
            frame_ms=20,
            output_device=output_device or os.getenv("AUDIO_OUTPUT_DEVICE"),
        )
        try:
            asyncio.run(chat.run())
        except KeyboardInterrupt:
            print("[INFO] Real-time chat stopped by user.")
        except Exception as e:
            print(f"[ERROR] Real-time chat encountered an error: {e}")
