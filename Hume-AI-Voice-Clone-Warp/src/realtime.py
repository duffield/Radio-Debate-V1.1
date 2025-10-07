import asyncio
import base64
import json
from typing import Optional, Dict

import numpy as np
import sounddevice as sd
import websockets


class RealTimeVoiceChat:
    """
    Real-time voice chat scaffold over WebSockets.
    - Captures microphone audio (PCM S16LE) and streams frames to the server.
    - Receives audio frames (PCM S16LE or base64 JSON) and plays them back.

    This is a protocol-agnostic scaffold. Adjust the initial handshake and
    frame formats to match Hume's realtime API. Typically you will:
      1) Send a JSON config message with sample_rate, channels, encoding, voice_id
      2) Stream audio frames as base64 PCM chunks
      3) Receive audio frames from the server and write to the output stream
    """

    def __init__(
        self,
        ws_url: str,
        headers: Optional[Dict[str, str]] = None,
        voice_id: Optional[str] = None,
        config_id: Optional[str] = None,
        sample_rate: int = 16000,
        channels: int = 1,
        frame_ms: int = 20,
        output_device: Optional[str] = None,
    ) -> None:
        from audio_utils import resolve_output_device

        self.ws_url = ws_url
        self.headers = headers or {}
        self.voice_id = voice_id
        self.config_id = config_id
        self.sample_rate = sample_rate
        self.channels = channels
        self.frame_ms = frame_ms
        self.frame_samples = int(self.sample_rate * self.frame_ms / 1000)
        self.dtype = 'int16'  # PCM S16LE
        self.output_device = resolve_output_device(output_device)

        # Streams
        self._in_stream: Optional[sd.InputStream] = None
        self._out_stream: Optional[sd.OutputStream] = None

    async def run(self) -> None:
        # Prepare output stream for low-latency playback
        self._out_stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=self.dtype,
            blocksize=self.frame_samples,
            device=self.output_device,
        )
        self._out_stream.start()

        async with websockets.connect(self.ws_url, extra_headers=self.headers, ping_interval=20, ping_timeout=20) as ws:
            # Initial config/handshake message — adjust fields to match Hume's API
            config = {
                "type": "config",
                "audio": {
                    "encoding": "pcm_s16le",
                    "sample_rate": self.sample_rate,
                    "channels": self.channels,
                    "frame_ms": self.frame_ms,
                },
                # Prefer config_id (EVI) when provided; voice_id remains for legacy flows
                "config_id": self.config_id,
                "voice_id": self.voice_id,
                "agent": {
                    "instructions": "You are a helpful assistant. Keep responses concise.",
                },
            }
            await ws.send(json.dumps(config))

            # Start mic capture as a background task
            producer_task = asyncio.create_task(self._producer(ws))
            consumer_task = asyncio.create_task(self._consumer(ws))

            done, pending = await asyncio.wait(
                {producer_task, consumer_task},
                return_when=asyncio.FIRST_EXCEPTION,
            )

            for task in pending:
                task.cancel()

        # Cleanup
        if self._out_stream:
            self._out_stream.stop()
            self._out_stream.close()
        if self._in_stream:
            self._in_stream.stop()
            self._in_stream.close()

    async def _producer(self, ws):
        loop = asyncio.get_event_loop()
        q: asyncio.Queue[bytes] = asyncio.Queue(maxsize=8)

        def on_audio(indata, frames, time, status):  # noqa: A002 (shadowing builtins)
            if status:
                # You can log status if needed.
                pass
            # Convert float32 (-1..1) to int16 PCM if needed
            if indata.dtype != np.int16:
                pcm = (indata * 32767.0).clip(-32768, 32767).astype(np.int16)
            else:
                pcm = indata
            # Ensure shape is (frames, channels)
            if pcm.ndim == 1:
                pcm = np.expand_dims(pcm, axis=1)
            try:
                q.put_nowait(pcm.tobytes())
            except asyncio.QueueFull:
                # Drop frame if the queue is full to avoid latency buildup
                pass

        self._in_stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='float32',  # capture as float, convert to int16
            blocksize=self.frame_samples,
            callback=on_audio,
        )
        self._in_stream.start()

        try:
            while True:
                frame_bytes = await q.get()
                # Wrap in a JSON message with base64 (adjust to server expectations)
                b64 = base64.b64encode(frame_bytes).decode('ascii')
                msg = {
                    "type": "audio_in",
                    "audio": b64,
                    "encoding": "pcm_s16le",
                    "sample_rate": self.sample_rate,
                    "channels": self.channels,
                }
                await ws.send(json.dumps(msg))
        except asyncio.CancelledError:
            return

    async def _consumer(self, ws):
        try:
            while True:
                message = await ws.recv()
                if isinstance(message, (bytes, bytearray)):
                    # Treat as raw PCM S16LE
                    self._play_pcm(bytes(message))
                else:
                    # JSON text message
                    try:
                        obj = json.loads(message)
                    except Exception:
                        continue

                    # If audio present as base64, decode and play
                    if isinstance(obj, dict) and obj.get("audio"):
                        try:
                            audio_bytes = base64.b64decode(obj["audio"])  # expect PCM
                            self._play_pcm(audio_bytes)
                        except Exception:
                            pass
                    # You could also handle transcripts or other events here
        except asyncio.CancelledError:
            return

    def _play_pcm(self, pcm_bytes: bytes) -> None:
        if not self._out_stream:
            return
        try:
            # Convert bytes -> int16 numpy -> write to stream
            arr = np.frombuffer(pcm_bytes, dtype=np.int16)
            if self.channels > 1:
                arr = arr.reshape(-1, self.channels)
            else:
                # shape (n, 1) for OutputStream.write; it accepts 1D or 2D
                pass
            self._out_stream.write(arr)
        except Exception:
            # Drop invalid frames
            pass
