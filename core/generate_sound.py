"""
Script untuk generate sound effects sederhana
Jalankan: python generate_sounds.py
"""

import numpy as np
import wave
import struct
import os

def generate_beep(filename, frequency=440, duration=0.1, sample_rate=44100):
    """Generate simple beep sound"""
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Generate sine wave dengan fade out
    audio = np.sin(2 * np.pi * frequency * t)

    # Apply fade out untuk smooth ending
    fade_samples = int(sample_rate * 0.02)  # 20ms fade
    fade = np.linspace(1, 0, fade_samples)
    audio[-fade_samples:] *= fade

    # Convert to 16-bit
    audio = np.int16(audio * 32767 * 0.5)  # 50% volume

    # Save as WAV
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio.tobytes())

    print(f"✅ Generated: {filename}")


def generate_bubble(filename, sample_rate=44100):
    """Generate bubble/text sound (like Undertale)"""
    duration = 0.05  # Very short
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Combine multiple frequencies for "bubbly" sound
    audio = (np.sin(2 * np.pi * 800 * t) * 0.3 +
             np.sin(2 * np.pi * 1200 * t) * 0.2 +
             np.sin(2 * np.pi * 600 * t) * 0.1)

    # Quick envelope
    envelope = np.exp(-t * 50)
    audio *= envelope

    # Convert to 16-bit
    audio = np.int16(audio * 32767)

    # Save as WAV
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio.tobytes())

    print(f"✅ Generated: {filename}")


def generate_correct(filename, sample_rate=44100):
    """Generate 'correct answer' sound (ascending)"""
    duration = 0.3
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Ascending chord
    freqs = [523, 659, 784]  # C, E, G (major chord)
    audio = np.zeros_like(t)

    for i, freq in enumerate(freqs):
        start = int(len(t) * i / len(freqs))
        end = int(len(t) * (i + 1) / len(freqs))
        audio[start:end] += np.sin(2 * np.pi * freq * t[start:end])

    # Fade out
    fade_samples = int(sample_rate * 0.05)
    fade = np.linspace(1, 0, fade_samples)
    audio[-fade_samples:] *= fade

    # Normalize and convert
    audio = audio / np.max(np.abs(audio))
    audio = np.int16(audio * 32767 * 0.6)

    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio.tobytes())

    print(f"✅ Generated: {filename}")


def generate_wrong(filename, sample_rate=44100):
    """Generate 'wrong answer' sound (short buzz)"""
    duration = 0.15
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Low buzz
    audio = np.sin(2 * np.pi * 200 * t)

    # Envelope
    envelope = np.exp(-t * 15)
    audio *= envelope

    audio = np.int16(audio * 32767 * 0.5)

    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio.tobytes())

    print(f"✅ Generated: {filename}")


def generate_fail(filename, sample_rate=44100):
    """Generate 'fail' sound (descending dramatic)"""
    duration = 0.5
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Descending frequencies (sad trombone style)
    freq_start = 400
    freq_end = 200
    freq = np.linspace(freq_start, freq_end, len(t))

    # Generate sweep
    phase = 2 * np.pi * np.cumsum(freq) / sample_rate
    audio = np.sin(phase)

    # Add some "gentar" effect (tremolo)
    tremolo = 1 + 0.3 * np.sin(2 * np.pi * 8 * t)
    audio *= tremolo

    # Envelope
    envelope = np.exp(-t * 3)
    audio *= envelope

    audio = np.int16(audio * 32767 * 0.6)

    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio.tobytes())

    print(f"✅ Generated: {filename}")


def main():
    """Generate all sound effects"""
    # Create sounds directory if not exists
    os.makedirs("sounds", exist_ok=True)

    print("Generating sound effects...")
    print()

    # Generate all sounds
    generate_bubble("sounds/bubble.wav")
    generate_correct("sounds/correct.wav")
    generate_wrong("sounds/wrong.wav")
    generate_fail("sounds/fail.wav")

    print()
    print("=" * 50)
    print("✅ All sound effects generated successfully!")
    print("=" * 50)
    print()
    print("Sound files created in 'sounds/' directory:")
    print("  - bubble.wav   : Text typing sound")
    print("  - correct.wav  : Correct answer sound")
    print("  - wrong.wav    : Wrong answer sound")
    print("  - fail.wav     : Failed quest sound (gentar!)")
    print()


if __name__ == "__main__":
    try:
        main()
    except ImportError:
        print("❌ ERROR: NumPy tidak terinstall!")
        print()
        print("Install dengan: pip install numpy")
        print()
    except Exception as e:
        print(f"❌ ERROR: {e}")
