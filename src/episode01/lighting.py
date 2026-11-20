"""Build a localized unlit-bulb overlay for the approved vanity room."""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "assets/environment/APPROVED_lalin_room_master.png"
OUTPUT = Path(__file__).resolve().parent / "art/mirror_off_overlay.png"

# Centers and radii, in pixels of the 1672×941 room master.
BULBS = (
    (1470.1, 95.1, 16.1, 16.9),
    (1533.0, 93.3, 16.9, 16.9),
    (1587.5, 125.7, 17.4, 17.9),
    (1416.9, 133.1, 15.4, 16.1),
    (1624.0, 185.4, 18.3, 17.8),
    (1382.0, 188.0, 15.2, 15.0),
    (1361.1, 252.6, 14.3, 16.2),
    (1354.0, 320.8, 14.0, 14.5),
    (1357.6, 385.3, 14.2, 14.5),
    (1619.6, 407.9, 17.4, 17.8),
    (1374.5, 444.9, 14.5, 15.4),
)

# Smaller visible highlights belonging to those bulbs, including the
# partial one between the jewelry box and the foreground telephone.
REFLECTIONS = (
    (1414.7, 195.9, 5.5, 10.2),
    (1394.5, 258.4, 4.0, 10.4),
    (1387.2, 323.2, 4.1, 10.8),
    (1376.1, 383.6, 3.2, 16.0),
    (1391.2, 383.4, 4.0, 9.7),
    (1393.3, 438.0, 7.9, 16.6),
    (1468.0, 497.5, 8.6, 12.8),
    (1651.6, 181.3, 4.0, 10.8),
    (1668.0, 259.0, 3.0, 13.8),
    (1654.3, 341.8, 3.0, 12.2),
    (1666.1, 341.3, 3.2, 12.8),
    (1604.0, 463.6, 3.0, 10.6),
)


def smoothstep(value):
    t = np.clip(value, 0, 1)
    return t * t * (3 - 2 * t)


def paint_glass(original, result, coverage, bulb, reflected=False):
    cx, cy, rx, ry = bulb
    width = original.shape[1]
    height = original.shape[0]
    left = max(0, int(cx - 2.2 * rx))
    right = min(width, int(cx + 2.2 * rx) + 1)
    top = max(0, int(cy - 2.2 * ry))
    bottom = min(height, int(cy + 2.2 * ry) + 1)
    region = np.s_[top:bottom, left:right]
    y, x = np.ogrid[top:bottom, left:right]
    dx = (x - cx) / rx
    dy = (y - cy) / ry
    radius = np.sqrt(dx * dx + dy * dy)
    source = original[region]

    # The small reflected lights inherit the shape of the highlights in
    # the painting. This protects foreground nails, glass and phone edges.
    original_white = smoothstep((source.min(axis=-1) - 164) / 78)
    core = smoothstep((1.15 - radius) / 0.23) * original_white
    glow = smoothstep((2.03 - radius) / 1.14)
    if reflected:
        glow *= original_white * 0.20
    else:
        warm_yellow = smoothstep((source[..., 0] - source[..., 2] - 26) / 67)
        warm_yellow *= smoothstep((source[..., 0] - source[..., 1] - 12) / 29)
        glow *= warm_yellow * 0.53

    tinted_frame = source * np.array([0.72, 0.63, 0.63])
    composite(result[region], coverage[region], tinted_frame, glow)

    # A weak environment reflection on shaded opal glass. The falloff
    # changes within the globe so the off state retains its volume.
    depth = np.sqrt(np.maximum(0, 1 - radius * radius))
    key_light = np.clip(0.52 * depth - 0.21 * dx - 0.27 * dy, 0, 1)
    glint = np.exp(-(((dx + 0.35) / 0.25) ** 2 + ((dy + 0.42) / 0.18) ** 2))
    unlit = (
        np.array([106, 88, 69])
        + key_light[..., None] * np.array([70, 64, 61])
        + glint[..., None] * np.array([43, 45, 44])
    )
    composite(result[region], coverage[region], unlit, core)


def composite(destination, coverage, foreground, alpha):
    destination *= 1 - alpha[..., None]
    destination += foreground * alpha[..., None]
    coverage += (1 - coverage) * alpha


def create_overlay(master):
    original = np.asarray(master.convert("RGB"), dtype=np.float64)
    result = original.copy()
    coverage = np.zeros(original.shape[:2], dtype=np.float64)
    for bulb in BULBS:
        paint_glass(original, result, coverage, bulb)
    for bulb in REFLECTIONS:
        paint_glass(original, result, coverage, bulb, reflected=True)

    alpha = np.round(255 * coverage)
    touched = alpha > 0
    layer = np.zeros((*master.size[::-1], 4), dtype=np.uint8)
    layer[:, :, 3] = alpha.astype(np.uint8)
    target = original[touched] + (result[touched] - original[touched]) * (
        255 / alpha[touched, None]
    )
    layer[touched, :3] = np.round(np.clip(target, 0, 255)).astype(np.uint8)
    return Image.fromarray(layer)


def make_preview(master, layer, path):
    # Same optical vertical crop used in the vanity storyboard.
    box = (1003, 0, 1003 + 941 * 1080 / 1920, 941)
    bright = master.convert("RGBA")
    off = Image.alpha_composite(bright, layer)
    panel = Image.new("RGB", (810, 510), "#1b1418")
    draw = ImageDraw.Draw(panel)
    for index, (label, state) in enumerate((
        ("AÇIK", bright), ("KISIK %65", Image.blend(bright, off, .65)), ("KAPALI", off)
    )):
        stage = state.transform((270, 480), Image.Transform.EXTENT, box, Image.Resampling.BICUBIC)
        panel.paste(stage.convert("RGB"), (270 * index, 30))
        draw.text((270 * index + 12, 9), label, fill="white")
    path.parent.mkdir(parents=True, exist_ok=True)
    panel.save(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--master", type=Path, default=MASTER)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--preview", type=Path, help="Optional three-state vertical comparison.")
    args = parser.parse_args()

    with Image.open(args.master) as master:
        if master.size != (1672, 941):
            parser.error("the overlay is calibrated for the approved 1672×941 room")
        layer = create_overlay(master)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        layer.save(args.output, optimize=True)
        if args.preview:
            make_preview(master, layer, args.preview)


if __name__ == "__main__":
    main()
