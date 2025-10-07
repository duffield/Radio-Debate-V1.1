import argparse
import os
import time
from pathlib import Path
from typing import Optional

from recorder import record_wav
from audio_utils import play_wav
from hume_client import HumeClient


DEF_OUTPUT = "data/voice_sample.wav"


def ensure_dirs(path: str) -> None:
    p = Path(path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Hume AI Voice Clone Chat App")
    parser.add_argument("--input", type=str, default=None, help="Path to existing WAV sample to use for voice cloning")
    parser.add_argument("--record-seconds", type=int, default=10, help="Seconds to record if no input file is provided")
    parser.add_argument("--output", type=str, default=DEF_OUTPUT, help="Where to save the recorded sample")
    parser.add_argument("--rate", type=int, default=16000, help="Sample rate for recording")
    parser.add_argument("--channels", type=int, default=1, help="Channels for recording (1=mono)")
    parser.add_argument("--test-playback", action="store_true", help="Play back the recorded sample to verify audio setup")
    parser.add_argument("--realtime", action="store_true", help="Start real-time voice conversation after cloning")
    parser.add_argument("--output-device", type=str, default=os.getenv("AUDIO_OUTPUT_DEVICE"), help="Audio output device name substring or index (e.g., 'Headphones' or 3)")
    parser.add_argument("--config-id", type=str, default=os.getenv("HUME_CONFIG_ID"), help="Hume EVI configuration ID to control model/voice selection")

    args = parser.parse_args()

    sample_path: Optional[str] = args.input

    if not sample_path:
        ensure_dirs(args.output)
        
        # Interactive prompt for voice recording
        print("\n=== Voice Sample Recording ===")
        print(f"This will record your voice for {args.record_seconds} seconds to train the AI voice clone.")
        print("Tips for best results:")
        print("  • Find a quiet environment")
        print("  • Speak clearly and naturally")
        print("  • Use your normal speaking voice")
        print("  • Read some text or speak about any topic")
        print("\nPress Enter when you're ready to start recording, or Ctrl+C to cancel...")
        
        try:
            input()
        except KeyboardInterrupt:
            print("\nCancelled by user.")
            return
        
        # Countdown before recording
        print("\nStarting recording in...")
        for i in range(3, 0, -1):
            print(f"  {i}...")
            time.sleep(1)
        print("  🎤 RECORDING NOW! 🎤")
        print(f"Speak for {args.record_seconds} seconds (or press Ctrl+C to stop early)")
        
        record_wav(args.output, duration_seconds=args.record_seconds, sample_rate=args.rate, channels=args.channels)
        sample_path = args.output
        print(f"\n✅ Recording saved: {sample_path}")

    if args.test_playback and sample_path:
        print("Playing back sample...")
        play_wav(sample_path, device=args.output_device)

    # Initialize Hume client (reads env vars; does not log secrets)
    client = HumeClient()

    # Determine if we're using an EVI configuration (preferred) or legacy voice_id flow
    config_id = args.config_id

    voice_id = None
    if config_id:
        print(f"Using EVI config ID: {config_id} (voice selection is handled in your Hume dashboard)")
    else:
        print("Cloning voice from sample (scaffold)...")
        voice_id = client.clone_voice_from_file(sample_path)
        if voice_id:
            print(f"Cloned voice_id: {voice_id}")
        else:
            print("Voice cloning is scaffolded. Please complete API endpoint/SDK integration in hume_client.py")

    if args.realtime:
        print("Starting real-time voice conversation (scaffold)... Press Ctrl+C to stop.")
        client.start_realtime_chat(voice_id, output_device=args.output_device, config_id=config_id)
        return

    # Start simple chat demo (text-in, audio-out) scaffold
    print("Starting chat demo (scaffold). Type your message and press Enter. Type 'exit' to quit.")
    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if user_text.lower() in {"exit", "quit"}:
            break

        audio_path = client.synthesize_speech(user_text, voice_id=voice_id)
        if audio_path and os.path.exists(audio_path):
            print("Assistant: (playing synthesized audio)")
            play_wav(audio_path, device=args.output_device)
        else:
            print("Assistant: (no audio - Hume TTS integration needs completion)")


if __name__ == "__main__":
    main()
