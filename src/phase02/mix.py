"""Mux the Phase 02 shot and its frame-keyed recorded foley."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SAMPLE_RATE = 48_000
VOICE_DIRECTORY = ROOT / "assets" / "voice"
FOLEY_DIRECTORY = HERE / "audio"
DEFAULT_OUTPUT = ROOT / "outputs" / "phase02" / "lalin_pilot.mp4"


def check_picture(video, fps, frames):
    command = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=codec_name,r_frame_rate,avg_frame_rate,nb_frames",
        "-of", "json", str(video),
    ]
    streams = json.loads(subprocess.check_output(command, text=True))["streams"]
    if not streams or streams[0]["codec_name"] != "h264":
        raise ValueError("Girdi H.264 video içermeli. Önce sahne görüntüsünü H.264 olarak kodlayın.")
    stream = streams[0]
    rates = {stream.get("r_frame_rate"), stream.get("avg_frame_rate")}
    if rates != {f"{fps}/1"}:
        raise ValueError(f"Girdi ve olay çizelgesi {fps} fps hızında eşleşmiyor.")
    count = stream.get("nb_frames")
    if count not in (None, "N/A", str(frames)):
        raise ValueError(f"Video {count} kare. Olay çizelgesi {frames} kare bekliyor.")


def resolve_audio(cue, foley_directory=FOLEY_DIRECTORY):
    name = cue["audio"]
    if name in ("raina", "raina_laugh"):
        stem = "raina_pilot_line" if name == "raina" else name
        for extension in (".wav", ".mp3"):
            recording = VOICE_DIRECTORY / (stem + extension)
            if recording.is_file():
                return recording
        print(f"Raina kaydı eksik: {stem}. Foley miksajı devam ediyor.", file=sys.stderr)
        return None
    if not name.endswith(".wav") or Path(name).name != name:
        raise ValueError(f"Geçersiz foley dosya adı: {name}")
    recording = foley_directory / name
    if not recording.is_file():
        raise FileNotFoundError(recording)
    return recording


def mix(video, output, event_file, foley_directory=FOLEY_DIRECTORY):
    timeline = json.loads(event_file.read_text())
    fps, frames = timeline["fps"], timeline["frames"]
    if not isinstance(fps, int) or fps <= 0 or SAMPLE_RATE % fps:
        raise ValueError("Olay çizelgesinde 48 kHz ile tam örneğe bölünen bir kare hızı gerekli.")
    if not isinstance(frames, int) or frames <= 0:
        raise ValueError("Olay çizelgesinde pozitif kare sayısı gerekli.")
    if output.exists():
        raise FileExistsError(f"Çıktı zaten var. Ayrı bir hedef seçin: {output}")
    check_picture(video, fps, frames)

    samples_per_frame = SAMPLE_RATE // fps
    audio_inputs = []
    filters = []
    tracks = []
    for cue in timeline["events"]:
        frame, gain, attack = cue["frame"], cue["gain"], cue["attack_sample"]
        if not isinstance(frame, int) or not 0 <= frame < frames:
            raise ValueError(f"Görüntü dışında ses olayı: {frame}")
        if not isinstance(attack, int) or not 0 <= attack <= frame * samples_per_frame:
            raise ValueError(f"Geçersiz ses başlangıcı: {cue}")
        if not isinstance(gain, (int, float)) or not 0 <= gain <= 2:
            raise ValueError(f"Geçersiz ses düzeyi: {gain}")
        path = resolve_audio(cue, foley_directory)
        if path is None:
            continue
        audio_inputs += ["-i", str(path)]
        delay = frame * samples_per_frame - attack
        index = len(tracks) + 1
        tracks.append(f"[cue{index}]")
        filters.append(
            f"[{index}:a]aresample={SAMPLE_RATE},"
            f"aformat=sample_fmts=fltp:channel_layouts=mono,"
            f"asetpts=PTS-STARTPTS,volume={gain},adelay={delay}S:all=1{tracks[-1]}"
        )
    if not tracks:
        raise ValueError("Miksaj için kullanılabilir ses kaydı yok.")
    filters.append(
        f"{''.join(tracks)}amix=inputs={len(tracks)}:normalize=0:dropout_transition=0,"
        f"apad,atrim=end_sample={frames * samples_per_frame},"
        "alimiter=limit=0.89:attack=5:release=50:latency=1:level=0[audio]"
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="lalin-mix-", dir=output.parent) as temporary:
        staged = Path(temporary) / "pilot.mp4"
        command = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(video),
            *audio_inputs, "-filter_complex", ";".join(filters),
            "-map", "0:v:0", "-map", "[audio]", "-c:v", "copy",
            "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(staged),
        ]
        subprocess.run(command, check=True)
        os.link(staged, output)


def main():
    parser = argparse.ArgumentParser(description="Lalin Faz 02 kareye bağlı FFmpeg miksajı")
    parser.add_argument("video", type=Path, help="Sessiz H.264 görüntü")
    parser.add_argument("--events", type=Path, default=HERE / "events.json")
    parser.add_argument("--foley-directory", type=Path, default=FOLEY_DIRECTORY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.output.suffix.lower() != ".mp4":
        parser.error("Çıktı yolu .mp4 ile bitmeli.")
    try:
        mix(args.video, args.output, args.events, args.foley_directory)
    except (KeyError, OSError, ValueError, subprocess.SubprocessError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
