"""Assemble the four approved-source camera plates and a storyboard preview."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "outputs/episode01"
ROOM = ROOT / "assets/environment/APPROVED_lalin_room_master.png"
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
WIDTH, HEIGHT = 1080, 1920


def viewport(image, camera):
    x, y, height = camera
    scale = height / HEIGHT
    return image.transform((WIDTH, HEIGHT), Image.Transform.AFFINE,
                           (scale, 0, x, 0, scale, y), Image.Resampling.BICUBIC)


def opacity(image, strength):
    layer = image.copy()
    layer.putalpha(layer.getchannel("A").point(lambda alpha: round(alpha * strength)))
    return layer


def camera_frame(room, dark_layer, actor, shot):
    image = viewport(room, shot["camera"]).convert("RGBA")
    if dark_layer is not None and shot["start_darkness"]:
        dim = viewport(dark_layer, shot["camera"])
        image.alpha_composite(opacity(dim, shot["start_darkness"]))
    left, top, zoom = shot["actor"]
    subject = actor.resize((round(actor.width * zoom), round(actor.height * zoom)),
                           Image.Resampling.LANCZOS)
    image.alpha_composite(subject, (left, top))
    return image.convert("RGB")


def storyboard(frames, shots, output):
    width, panel_width = 1280, 320
    canvas = Image.new("RGB", (width, 648), "#24151d")
    draw = ImageDraw.Draw(canvas)
    title = ImageFont.truetype(FONT, 16)
    meta = ImageFont.truetype(FONT, 13)
    light = ["Işık açık", "Işık kısık", "Işık daha kısık", "Ayna ışığı kapalı"]
    start = 0
    for i, (image, shot) in enumerate(zip(frames, shots)):
        x = i * panel_width
        end = start + shot["seconds"]
        canvas.paste(image.resize((panel_width, 569), Image.Resampling.LANCZOS), (x, 54))
        draw.text((x + 12, 9), shot["title"], fill="#fff1e9", font=title)
        draw.text((x + 12, 32), f"{start:02d}–{end:02d} sn", fill="#e9c8be", font=meta)
        draw.text((x + 12, 629), light[i], fill="#e9c8be", font=meta)
        start = end
    canvas.save(output, quality=94)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("actor", type=Path)
    parser.add_argument("--lamp-overlay", type=Path, required=True,
                        help="Native-room RGBA overlay for the large mirror's unlit state.")
    args = parser.parse_args()
    shots = json.loads((HERE / "scene_plan.json").read_text())["shots"]
    room = Image.open(ROOM).convert("RGB")
    lamps = Image.open(args.lamp_overlay).convert("RGBA")
    if lamps.size != room.size:
        parser.error("Işık katmanı oda master'ıyla aynı piksel ölçüsünde olmalı.")
    actor = Image.open(args.actor).convert("RGBA")
    starts = OUT / "starts"
    starts.mkdir(parents=True, exist_ok=True)
    frames = []
    for shot in shots:
        frame = camera_frame(room, lamps, actor, shot)
        frame.save(starts / f"plan{shot['id']:02}.png")
        frames.append(frame)
    storyboard(frames, shots, OUT / "storyboard.jpg")


if __name__ == "__main__":
    main()
