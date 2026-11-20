"""Composite one episode shot with the approved room and timed mirror bulbs."""

import argparse
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from frames import HEIGHT, ROOM, WIDTH, camera_frame, viewport


HERE = Path(__file__).resolve().parent
PLAN = HERE / "scene_plan.json"
OVERLAY = HERE / "art/mirror_off_overlay.png"
WORK = Path("/tmp/lalin-episode01")
FRAME_BYTES = WIDTH * HEIGHT * 3

# Soft motion limits measured on the source cutout at its native size.
# The three dialogue crops leave the foreground fingers below the jaw still.
HEAD_REGION = (
    (164, 7), (311, 0), (337, 29), (351, 72), (376, 114),
    (378, 156), (366, 177), (343, 186), (327, 173), (311, 176),
    (288, 188), (265, 195), (226, 193), (183, 195), (161, 187),
    (137, 156), (138, 106), (149, 62),
)


def actor_alpha(actor, shot):
    x, y, zoom = shot["actor"]
    layer = Image.new("L", (WIDTH, HEIGHT), 0)
    size = (round(actor.width * zoom), round(actor.height * zoom))
    layer.paste(actor.getchannel("A").resize(size, Image.Resampling.LANCZOS), (x, y))
    return layer


def motion_matte(actor, shot, lamps):
    x, y, zoom = shot["actor"]
    alpha = actor_alpha(actor, shot)
    wide = shot["id"] == 1
    expanded = alpha.filter(ImageFilter.MaxFilter(17 if wide else 11))
    feathered = np.asarray(expanded.filter(ImageFilter.GaussianBlur(6)), dtype=np.float32) / 255
    if wide:
        # Let the adjusting arm and hair move. Blend toward the fixed image
        # over the lower jacket and waist.
        rows = (np.arange(HEIGHT, dtype=np.float32) - y) / zoom
        region = 1 - np.clip((rows - 402) / 91, 0, 1)
        region = (region * region * (3 - 2 * region))[:, None]
    else:
        head = Image.new("L", (WIDTH, HEIGHT), 0)
        # The reply take brings an extra hand toward the right temple.
        # Its pixels sit outside the face and must stay outside the matte.
        anchors = HEAD_REGION
        if shot["id"] == 3:
            anchors = [(min(px, 338) if py > 76 else px, py) for px, py in anchors]
        points = [(round(x + px * zoom), round(y + py * zoom)) for px, py in anchors]
        ImageDraw.Draw(head).polygon(points, fill=255)
        region = np.asarray(head.filter(ImageFilter.GaussianBlur(12)), dtype=np.float32) / 255

    # A feather outside the silhouette must not reveal an unchanged Wan bulb
    # wherever the local light overlay is visible on the room.
    lamp_alpha = np.asarray(viewport(lamps, shot["camera"]).getchannel("A"), dtype=np.float32) / 255
    actor_pixels = np.asarray(alpha, dtype=np.float32) / 255
    lamp_exclusion = np.clip(lamp_alpha * 6, 0, 1) * (1 - actor_pixels)
    return feathered * region * (1 - lamp_exclusion)


def bounds(mask):
    rows = np.flatnonzero(mask.any(axis=1))
    columns = np.flatnonzero(mask.any(axis=0))
    return np.s_[rows[0]:rows[-1] + 1, columns[0]:columns[-1] + 1]


class Shot:
    def __init__(self, shot, actor, room, lamps):
        self.lit = np.array(camera_frame(room, lamps, actor, {**shot, "start_darkness": 0}))
        off = np.asarray(camera_frame(room, lamps, actor, {**shot, "start_darkness": 1}))
        self.light_box = bounds(np.any(self.lit != off, axis=-1))
        self.light_lit = self.lit[self.light_box].astype(np.float32)
        self.light_delta = off[self.light_box].astype(np.float32) - self.light_lit
        self.light_frames, self.light_values = zip(*shot["light_cues"])
        matte = motion_matte(actor, shot, lamps)
        self.motion_box = bounds(matte > 1 / 255)
        self.motion_alpha = matte[self.motion_box][..., None]
        self.darkness = None
        self.plate = self.lit.copy()

    def frame(self, index, motion):
        darkness = np.interp(index, self.light_frames, self.light_values)
        if darkness != self.darkness:
            self.plate[self.light_box] = np.rint(self.light_lit + darkness * self.light_delta)
            self.darkness = darkness

        image = self.plate.copy()
        area = self.motion_box
        base = image[area].astype(np.float32)
        image[area] = np.rint(base + self.motion_alpha * (motion[area] - base))
        return image


def decoding(path, fps, count, selected_frame=None):
    filters = f"fps={fps}"
    if selected_frame is not None:
        filters += f",select=eq(n\\,{selected_frame})"
    return [
        "ffmpeg", "-v", "error", "-nostdin", "-threads", "1", "-i", str(path),
        "-map", "0:v:0", "-an", "-vf", filters, "-fps_mode", "passthrough",
        "-frames:v", str(count), "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-threads", "1", "pipe:1",
    ]


def motion_frame(pipe, index):
    payload = pipe.read(FRAME_BYTES)
    if len(payload) != FRAME_BYTES:
        raise RuntimeError(f"Wan klibinde {index}. kare eksik veya piksel ölçüsü yanlış.")
    return np.frombuffer(payload, dtype=np.uint8).reshape(HEIGHT, WIDTH, 3)


def verify_dimensions(path):
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height", "-of", "csv=p=0:s=x", str(path)],
        check=True, capture_output=True, text=True,
    )
    if probe.stdout.strip() != f"{WIDTH}x{HEIGHT}":
        raise RuntimeError(f"Beklenen Wan klibi {WIDTH}×{HEIGHT} dikey olmalı.")


def render(path, output, shot, fps, count, still):
    if output.exists():
        raise FileExistsError(output)
    verify_dimensions(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if still is not None:
        with subprocess.Popen(decoding(path, fps, 1, still), stdout=subprocess.PIPE) as decoder:
            composed = shot.frame(still, motion_frame(decoder.stdout, still))
            if decoder.wait():
                raise RuntimeError("Wan karesi çözülemedi.")
        Image.fromarray(composed).save(output)
        return

    with TemporaryDirectory(prefix="episode01-shot-", dir=output.parent) as temp:
        draft = Path(temp) / "picture.mp4"
        command = [
            "ffmpeg", "-v", "error", "-nostdin", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-video_size", f"{WIDTH}x{HEIGHT}", "-framerate", str(fps), "-i", "pipe:0",
            "-an", "-c:v", "libx264", "-threads", "2", "-filter_threads", "1",
            "-vf", "scale=out_color_matrix=bt709:out_range=tv",
            "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p", "-color_range", "tv",
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
            "-movflags", "+faststart", str(draft),
        ]
        with subprocess.Popen(decoding(path, fps, count), stdout=subprocess.PIPE) as decoder:
            with subprocess.Popen(command, stdin=subprocess.PIPE) as encoder:
                for index in range(count):
                    composed = shot.frame(index, motion_frame(decoder.stdout, index))
                    encoder.stdin.write(composed.tobytes())
                encoder.stdin.close()
                if encoder.wait() or decoder.wait():
                    raise RuntimeError("Plan kodlaması tamamlanamadı.")
        draft.replace(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shot", type=int, choices=range(1, 5), required=True)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--actor", type=Path, default=WORK / "actor.png")
    parser.add_argument("--still", type=int, help="Tek kareyi PNG olarak çıkarır. Kare numarası 0'dan başlar.")
    parser.add_argument("--frames", type=int, help="Plan başından teslim edilecek kare sayısı.")
    args = parser.parse_args()
    plan = json.loads(PLAN.read_text())
    details = next(shot for shot in plan["shots"] if shot["id"] == args.shot)
    fps = plan["fps"]
    count = details["seconds"] * fps
    if args.frames is not None:
        if not 1 <= args.frames <= count:
            parser.error(f"--frames 1–{count} arasında olmalı.")
        count = args.frames
    name = f"plan{args.shot:02}"
    path = args.input or WORK / "wan" / f"{name}.mp4"
    output = args.output or WORK / "picture" / f"{name}{'.png' if args.still is not None else '.mp4'}"
    if args.still is not None and not 0 <= args.still < count:
        parser.error(f"Kare numarası 0–{count - 1} arasında olmalı.")

    with Image.open(args.actor) as source, Image.open(ROOM) as room, Image.open(OVERLAY) as lamps:
        shot = Shot(details, source.convert("RGBA"), room.convert("RGB"), lamps.convert("RGBA"))
    render(path, output, shot, fps, count, args.still)


if __name__ == "__main__":
    main()
