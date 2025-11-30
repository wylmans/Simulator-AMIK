"""
Script untuk generate sound effect seperti UNDERTALE
Sound effect akan bunyi setiap karakter muncul

Requirements: numpy, scipy
Install dengan: pip install numpy scipy

Note: Untuk convert ke MP3, butuh ffmpeg atau pydub
"""

import numpy as np
from scipy.io import wavfile
import os

def generate_undertale_blip(filename="sounds/bubble", duration=0.04, frequency=800):
    """
    Generate sound effect seperti Undertale - blip pendek dan jelas

    Args:
        filename: Path output file (tanpa extension)
        duration: Durasi sound dalam detik (pendek = 0.04)
        frequency: Frekuensi nada (Hz)
    """

    # Create sounds directory jika belum ada
    os.makedirs("sounds", exist_ok=True)

    # Parameters
    sample_rate = 44100  # Sample rate (Hz)

    # Generate time array
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Generate SQUARE WAVE (retro/pixel game style seperti Undertale)
    signal = np.sign(np.sin(2 * np.pi * frequency * t))

    # Add very fast envelope (hampir tidak ada fade, langsung bunyi)
    envelope = np.ones_like(t)
    attack_samples = int(0.002 * sample_rate)  # 2ms attack (sangat cepat)
    release_samples = int(0.015 * sample_rate)  # 15ms release

    # Very fast attack
    if attack_samples < len(envelope):
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

    # Quick release
    if release_samples < len(envelope):
        envelope[-release_samples:] = np.linspace(1, 0, release_samples)

    # Apply envelope
    signal = signal * envelope

    # Normalize ke 16-bit integer range
    signal = np.int16(signal / np.max(np.abs(signal)) * 32767 * 0.6)  # 60% volume

    # Save to WAV
    wav_file = filename + ".wav"
    wavfile.write(wav_file, sample_rate, signal)
    print(f"✅ WAV created: {wav_file}")

    # Try to convert to MP3
    try:
        from pydub import AudioSegment
        sound = AudioSegment.from_wav(wav_file)
        mp3_file = filename + ".mp3"
        sound.export(mp3_file, format="mp3")
        print(f"✅ MP3 created: {mp3_file}")
        return mp3_file
    except ImportError:
        print(f"⚠️  pydub tidak tersedia, hanya WAV yang dibuat")
        print(f"   Gunakan {wav_file} atau install: pip install pydub")
        return wav_file
    except Exception as e:
        print(f"⚠️  Convert ke MP3 gagal, gunakan WAV")
        return wav_file


def generate_undertale_style_sounds():
    """Generate berbagai varian sound seperti karakter Undertale"""

    print("🎮 Generating UNDERTALE-style sound effects...\n")
    print("="*60)

    # Sound 1: Standard text blip (seperti Sans/Papyrus)
    print("\n1. STANDARD BLIP (Recommended - Undertale style):")
    generate_undertale_blip("sounds/bubble", duration=0.04, frequency=800)

    # Sound 2: High pitch (seperti Flowey/Toriel)
    print("\n2. HIGH PITCH (Cute/High voice):")
    generate_undertale_blip("sounds/bubble_high", duration=0.035, frequency=1200)

    # Sound 3: Low pitch (seperti Asgore/Deep voice)
    print("\n3. LOW PITCH (Deep voice):")
    generate_undertale_blip("sounds/bubble_low", duration=0.045, frequency=500)

    # Sound 4: Very high (seperti Flowey evil laugh)
    print("\n4. VERY HIGH (Special characters):")
    generate_undertale_blip("sounds/bubble_special", duration=0.03, frequency=1500)

    print("\n" + "="*60)
    print("✨ Sound effects generation complete!")
    print("\n📝 REKOMENDASI:")
    print("   Gunakan: sounds/bubble.wav atau sounds/bubble.mp3")
    print("   Sound ini akan bunyi SETIAP karakter seperti Undertale!")
    print("\n💡 TIPS:")
    print("   - bubble.wav = Standard (paling mirip Undertale)")
    print("   - bubble_high.wav = Untuk NPC dengan suara tinggi")
    print("   - bubble_low.wav = Untuk NPC dengan suara dalam")
    print("   - bubble_special.wav = Untuk karakter spesial/robot")


def show_usage_info():
    """Tampilkan info penggunaan"""
    print("\n" + "="*60)
    print("📚 CARA PAKAI:")
    print("="*60)
    print("\n1. File sound sudah dibuat di folder sounds/")
    print("   Game akan otomatis detect file sound")
    print("\n2. Sound akan bunyi SETIAP karakter (non-spasi)")
    print("   Mirip seperti Undertale!")
    print("\n3. Jika ingin ganti sound untuk NPC tertentu:")
    print("   Edit core/dialogue.py dan buat multiple DialogueBox")
    print("   dengan sound berbeda")
    print("\n4. Test di game:")
    print("   - Dekati NPC")
    print("   - Tekan E")
    print("   - Dengarkan sound effect setiap huruf muncul!")
    print("="*60)


if __name__ == "__main__":
    try:
        # Generate Undertale-style sounds
        generate_undertale_style_sounds()

        # Show usage info
        show_usage_info()

        print("\n🎊 SELESAI! Sound effects siap digunakan!")
        print("   Jalankan game dan test sound nya! 🎮")

    except ImportError as e:
        print("❌ Error: Library tidak ditemukan!")
        print("Install dengan: pip install numpy scipy")
        print("\nOptional (untuk MP3): pip install pydub")
        print(f"\nDetail: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
