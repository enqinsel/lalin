"""Prepare the existing voice recordings as frame-length Wan drivers and mix stems."""

import argparse
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RATE = 48000


def prepare(directory):
    shots = json.loads((HERE / "scene_plan.json").read_text())["shots"]
    directory.mkdir(parents=True, exist_ok=True)
    for shot in shots:
        speech = shot["speech"]
        first, last = speech["trim"]
        offset = round(speech["delay"] * RATE)
        length = shot["seconds"] * RATE
        if offset + round((last - first) * RATE) > length:
            raise ValueError(f"Replik plan {shot['id']} süresini aşıyor.")
        filters = (
            f"atrim=start={first}:end={last},asetpts=PTS-STARTPTS,"
            f"aresample={RATE},adelay={offset}S:all=1,apad,atrim=end_sample={length}"
        )
        name = f"plan{shot['id']:02}"
        wave = directory / (name + ".wav")
        subprocess.run([
            "ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", str(ROOT / speech["path"]),
            "-af", filters, "-ac", "1", "-c:a", "pcm_s16le", str(wave),
        ], check=True)
        subprocess.run([
            "ffmpeg", "-v", "error", "-y", "-i", str(wave), "-c:a", "libmp3lame",
            "-b:a", "192k", str(directory / (name + ".mp3")),
        ], check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    prepare(parser.parse_args().directory)
