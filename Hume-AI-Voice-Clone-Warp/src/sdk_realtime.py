import asyncio
import base64
from typing import Optional

import numpy as np
import sounddevice as sd


class HumeSDKVoiceChat:
    """
    Realtime voice chat using the Hume Python SDK if available.

    Notes:
    - This implementation defensively introspects the SDK to avoid hard failures if
      method names differ across SDK versions. If it cannot find the expected hooks,
      it should raise a RuntimeError so callers can fall back to the WebSocket scaffold.
    - Audio capture and playback reuse the same approach as the WS scaffold.
    """

    def __init__(
        self,
        api_key: str,
        config_id: str,
        sample_rate: int = 16000,
        channels: int = 1,
        frame_ms: int = 20,
        output_device: Optional[str] = None,
    ) -> None:
        from audio_utils import resolve_output_device

        self.api_key = api_key
        self.config_id = config_id
        self.sample_rate = sample_rate
        self.channels = channels
        self.frame_ms = frame_ms
        self.frame_samples = int(self.sample_rate * self.frame_ms / 1000)
        self.dtype = "int16"
        self.output_device = resolve_output_device(output_device)

        self._in_stream: Optional[sd.InputStream] = None
        self._out_stream: Optional[sd.OutputStream] = None

    async def run(self) -> None:
        try:
            # Lazy import so the whole project doesn't fail if SDK isn't installed
            from hume import HumeStreamClient  # type: ignore
        except Exception as e:
            raise RuntimeError(f"Hume SDK not available: {e}")

        client = HumeStreamClient(self.api_key)

        # Acquire EVI/connect callable defensively
        evi = getattr(client, "evi", None)
        if evi is None:
            raise RuntimeError("Hume SDK does not expose 'client.evi' — cannot use SDK realtime.")
        connect = getattr(evi, "connect", None)
        if connect is None:
            raise RuntimeError("Hume SDK EVI object has no 'connect' — cannot use SDK realtime.")

        # Prepare output stream
        self._out_stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=self.dtype,
            blocksize=self.frame_samples,
            device=self.output_device,
        )
        self._out_stream.start()

        # Connect via SDK and run producer/consumer
        try:
            async with connect(config_id=self.config_id) as session:  # type: ignore[call-arg]
                producer = asyncio.create_task(self._producer(session))
                consumer = asyncio.create_task(self._consumer(session))
                done, pending = await asyncio.wait(
                    {producer, consumer}, return_when=asyncio.FIRST_EXCEPTION
                )
                for task in pending:
                    task.cancel()
        finally:
            if self._out_stream:
                self._out_stream.stop()
                self._out_stream.close()
            if self._in_stream:
                self._in_stream.stop()
                self._in_stream.close()

    async def _producer(self, session) -> None:
        import asyncio as aio

        q: aio.Queue[bytes] = aio.Queue(maxsize=8)

        def on_audio(indata, frames, time, status):  # noqa: A002
            if status:
                pass
            if indata.dtype != np.int16:
                pcm = (indata * 32767.0).clip(-32768, 32767).astype(np.int16)
            else:
                pcm = indata
            if pcm.ndim == 1:
                import numpy as _np
                pcm = _np.expand_dims(pcm, axis=1)
            try:
                q.put_nowait(pcm.tobytes())
            except aio.QueueFull:
                pass

        self._in_stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            blocksize=self.frame_samples,
            callback=on_audio,
        )
        self._in_stream.start()

        # Resolve a send method: prefer dedicated audio senders if present
        send_audio = None
        for name in ("send_audio", "send_audio_frame", "send_pcm"):
            fn = getattr(session, name, None)
            if callable(fn):
                send_audio = fn
                break
        generic_send = getattr(session, "send", None)

        if not send_audio and not generic_send:
            raise RuntimeError("Hume SDK session has no send method — cannot transmit audio.")

        try:
            while True:
                frame_bytes = await q.get()
                if send_audio:
                    await send_audio(frame_bytes, sample_rate=self.sample_rate, channels=self.channels)  # type: ignore[misc]
                else:
                    # Fallback: send a JSON message with base64 audio
                    b64 = base64.b64encode(frame_bytes).decode("ascii")
                    msg = {
                        "type": "audio_in",
                        "audio": b64,
                        "encoding": "pcm_s16le",
                        "sample_rate": self.sample_rate,
                        "channels": self.channels,
                    }
                    await generic_send(msg)  # type: ignore[misc]
        except asyncio.CancelledError:
            return

    async def _consumer(self, session) -> None:
        # Resolve a receive/listen method
        if hasattr(session, "listen") and callable(getattr(session, "listen")):
            async for event in session.listen():  # type: ignore[attr-defined]
                await self._handle_event(event)
            return
        if hasattr(session, "__aiter__"):
            async for event in session:
                await self._handle_event(event)
            return
        recv = getattr(session, "recv", None)
        if callable(recv):
            while True:
                event = await recv()
                await self._handle_event(event)
            
        raise RuntimeError("Hume SDK session does not support iteration or recv().")

    async def _handle_event(self, event) -> None:
        # Try common shapes: dict with base64 audio, raw bytes, or attribute-based
        try:
            if isinstance(event, (bytes, bytearray)):
                self._play_pcm(bytes(event))
                return
            if isinstance(event, dict):
                audio_b64 = event.get("audio") or event.get("audio_base64")
                if audio_b64:
                    import base64 as _b64
                    self._play_pcm(_b64.b64decode(audio_b64))
                return
            # Attribute-based (SDK objects)
            audio_b64 = getattr(event, "audio", None)
            if audio_b64 and isinstance(audio_b64, str):
                import base64 as _b64
                self._play_pcm(_b64.b64decode(audio_b64))
        except Exception:
            # best-effort playback
            pass

    def _play_pcm(self, pcm_bytes: bytes) -> None:
        if not self._out_stream:
            return
        try:
            arr = np.frombuffer(pcm_bytes, dtype=np.int16)
            if self.channels > 1:
                arr = arr.reshape(-1, self.channels)
            self._out_stream.write(arr)
        except Exception:
            pass