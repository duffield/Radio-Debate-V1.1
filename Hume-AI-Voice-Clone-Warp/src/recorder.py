import sounddevice as sd
import soundfile as sf
import numpy as np
from pathlib import Path


def record_wav(path: str, duration_seconds: int = 10, sample_rate: int = 16000, channels: int = 1) -> None:
    """
    Records audio from the default input device and writes a WAV file.
    """
    Path(path).expanduser().parent.mkdir(parents=True, exist_ok=True)

    print("Press Ctrl+C to stop early.")
    try:
        audio = sd.rec(int(duration_seconds * sample_rate), samplerate=sample_rate, channels=channels, dtype='float32')
        sd.wait()
    except KeyboardInterrupt:
        # If user interrupts early, capture what we have by stopping stream
        sd.stop()
        audio, _ = sd.get_stream().read(sd.get_stream().frames)
    except Exception as e:
        raise RuntimeError(f"Audio recording failed: {e}")

    # Ensure mono if channels=1
    if channels == 1 and audio.ndim > 1:
        audio = audio[:, 0]

    # Normalize to prevent clipping if needed
    max_abs = np.max(np.abs(audio)) if audio.size else 0
    if max_abs > 1.0:
        audio = audio / max_abs

    sf.write(path, audio, sample_rate)
    
