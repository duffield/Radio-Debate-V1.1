import sounddevice as sd
import soundfile as sf
import numpy as np
from typing import Optional, Union


def resolve_output_device(device_spec: Optional[Union[str, int]]) -> Optional[int]:
    """
    Resolve an output device by index or substring match on name.
    Returns device index or None to use default.
    """
    if device_spec is None:
        return None
    # If it's already an int (index), return it
    try:
        if isinstance(device_spec, int):
            return device_spec
        # Try to parse string as int
        return int(device_spec)
    except (ValueError, TypeError):
        pass

    # Substring match (case-insensitive) against output-capable devices
    wanted = str(device_spec).lower()
    devices = sd.query_devices()
    for idx, dev in enumerate(devices):
        try:
            name = str(dev.get("name", "")).lower()
            if dev.get("max_output_channels", 0) > 0 and wanted in name:
                return idx
        except Exception:
            continue
    print(f"[WARN] Output device matching '{device_spec}' not found; using system default.")
    return None


def play_wav(path: str, device: Optional[Union[str, int]] = None) -> None:
    data, samplerate = sf.read(path, dtype='float32')
    # Ensure 2D shape for sounddevice playback
    if data.ndim == 1:
        data = np.expand_dims(data, axis=1)

    dev_index = resolve_output_device(device)

    # Use OutputStream to select device explicitly (if provided)
    with sd.OutputStream(samplerate=samplerate, channels=data.shape[1], dtype='float32', device=dev_index):
        sd.play(data, samplerate, device=dev_index)
        sd.wait()
