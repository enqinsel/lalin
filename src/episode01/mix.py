"""Frame-addressed Raina and recorded Foley mix for Episode 01."""

import argparse
import json
from pathlib import Path
import wave

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RATE = 48000
FPS = 30
SAMPLES_PER_FRAME = RATE // FPS
QUIET = (529, 559)
SWITCHES = [
    (187, "light_dim.wav", 1.10, 240),
    (322, "light_flash.wav", 1.10, 240),
    (525, "light_off.wav", 1.10, 240),
]


def read_wave(path):
    with wave.open(str(path), "rb") as source:
        if (source.getframerate(), source.getnchannels(), source.getsampwidth()) != (RATE, 1, 2):
            raise ValueError(f"48 kHz mono PCM16 bekleniyor: {path}")
        return np.frombuffer(source.readframes(source.getnframes()), "<i2").astype(np.float32) / 32768


def voice_gain(samples):
    chunks = samples[:len(samples) - len(samples) % 480].reshape(-1, 480)
    rms = np.sqrt(np.mean(chunks * chunks, axis=1))
    active = rms[rms > .018]
    if not len(active):
        raise ValueError("Konuşma gövdesi bulunamadı.")
    average = float(np.sqrt(np.mean(active * active)))
    peak = float(np.max(np.abs(samples)))
    return min(10 ** (-18.0 / 20) / average, 10 ** (-3.5 / 20) / peak)


def mix(drivers, destination, cloth_frame, delivery_frames):
    shots = json.loads((HERE / "scene_plan.json").read_text())["shots"]
    dialogue = []
    for shot in shots:
        audio = read_wave(drivers / f"plan{shot['id']:02}.wav")
        if len(audio) != shot["seconds"] * RATE:
            raise ValueError(f"Plan {shot['id']} ile ses süresi farklı.")
        gain = voice_gain(audio)
        dialogue.append(audio * gain)
        print(f"Plan {shot['id']} Raina seviye düzeltmesi {20*np.log10(gain):+.2f} dB")
    speech = np.concatenate(dialogue)
    if delivery_frames is not None:
        samples = delivery_frames * SAMPLES_PER_FRAME
        if not QUIET[1] * SAMPLES_PER_FRAME < samples <= len(speech):
            raise ValueError("Geçersiz teslim süresi.")
        if samples < len(speech) and np.max(np.abs(speech[samples:])) > 1e-5:
            raise ValueError("Teslim kesmesi konuşmaya denk geliyor.")
        speech = speech[:samples]
    room = read_wave(HERE / "audio/room_tone.wav")[:len(speech)].copy()
    if len(room) != len(speech):
        raise ValueError("Oda tonu bölümden kısa.")
    room *= 1.15
    fade = 2400
    room[:fade] *= np.linspace(0, 1, fade)
    room[-fade:] *= np.linspace(1, 0, fade)
    quiet_start, quiet_end = (frame * SAMPLES_PER_FRAME for frame in QUIET)
    room[quiet_start - fade:quiet_start] *= np.linspace(1, 0, fade)
    room[quiet_start:quiet_end] = 0
    room[quiet_end:quiet_end + fade] *= np.linspace(0, 1, fade)
    if np.max(np.abs(speech[quiet_start:quiet_end])) > 1e-5:
        raise ValueError("Sessizlik aralığında konuşma var.")

    soundtrack = speech + room
    cues = [(frame, HERE / "audio" / path, gain, attack) for frame, path, gain, attack in SWITCHES]
    if cloth_frame is not None:
        cues.append((cloth_frame, ROOT / "src/phase03b/audio/cloth.wav", .68, 432))
    for frame, path, gain, attack in cues:
        sound = read_wave(path)
        start = frame * SAMPLES_PER_FRAME - attack
        end = start + len(sound)
        if start < 0 or end > len(soundtrack) or start < quiet_end and end > quiet_start:
            raise ValueError(f"Geçersiz Foley yerleşimi: {path.name}")
        soundtrack[start:end] += gain * sound
        print(f"{path.name} f{frame} / {frame * SAMPLES_PER_FRAME}. örnek")

    soundtrack *= 10 ** (1.8 / 20)
    peak = float(np.max(np.abs(soundtrack)))
    if peak >= 1:
        raise ValueError("Miks taşma yapıyor.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(destination), "wb") as target:
        target.setparams((1, 2, RATE, len(soundtrack), "NONE", ""))
        target.writeframes(np.rint(soundtrack * 32767).astype("<i2").tobytes())
    print(f"Miks {len(soundtrack) / RATE:.3f} sn, tepe {20*np.log10(peak):.2f} dBFS")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("drivers", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--cloth-frame", type=int)
    parser.add_argument("--frames", type=int)
    options = parser.parse_args()
    mix(options.drivers, options.output, options.cloth_frame, options.frames)
