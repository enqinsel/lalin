"""Extract independently controllable cutouts from the approved 02 portrait."""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / "assets/character/approved_initial_3/02_lalin_expressions_fashion.png"
ART = HERE / "art/face"
BOX = (75, 0, 329, 284)
ANCHOR = (224, 204)
S = 4

portrait = Image.open(SOURCE).convert("RGB").crop(BOX)
parts = {}


def contour(knots):
    # Closed Catmull-Rom contour over traced source landmarks.
    points = np.asarray(knots, dtype=float)
    t = np.linspace(0, 1, 12, endpoint=False)[:, None]
    for i, b in enumerate(points):
        a, c, d = points[i-1], points[(i+1) % len(points)], points[(i+2) % len(points)]
        yield from .5 * (2*b + (c-a)*t + (2*a-5*b+4*c-d)*t*t + (-a+3*b-3*c+d)*t*t*t)


def mask(knots, feather=0):
    large = Image.new("L", (portrait.width*S, portrait.height*S))
    ImageDraw.Draw(large).polygon([((x-BOX[0])*S, y*S) for x, y in contour(knots)], fill=255)
    if feather:
        large = large.filter(ImageFilter.GaussianBlur(feather*S))
    return large.resize(portrait.size, Image.Resampling.LANCZOS)


def save(name, color, alpha, pivot=ANCHOR):
    bounds = alpha.getbbox()
    rgba = color.convert("RGBA")
    rgba.putalpha(alpha)
    rgba.crop(bounds).save(ART / f"{name}.png")
    parts[name] = {"file": f"{name}.png",
                   "offset": [bounds[0] + BOX[0] - pivot[0], bounds[1] - pivot[1]],
                   "pivot": [pivot[0] - ANCHOR[0], pivot[1] - ANCHOR[1]]}


def remove_paper(alpha):
    # The opaque reference has cream paper in the gaps under the glasses
    # and along the outer hair silhouette.
    lightest = np.asarray(portrait, dtype=np.float32).min(axis=2)
    foreground = np.clip((223 - lightest) / 35, 0, 1)
    return Image.fromarray((np.asarray(alpha) * foreground).astype(np.uint8))


def skin_plate(removed, edges):
    pixels = np.asarray(portrait, dtype=np.float32)
    removal = np.maximum.reduce([np.asarray(a, dtype=np.float32) / 255 for a in removed])
    repair = removal > .15
    filtered = pixels.copy()
    for _ in range(325):
        average = (np.roll(filtered, 1, 0) + np.roll(filtered, -1, 0)
                   + np.roll(filtered, 1, 1) + np.roll(filtered, -1, 1)) * .25
        filtered[repair] = average[repair]
    strength = np.maximum(removal, gaussian_filter(repair.astype(np.float32), .63))
    retouch = pixels * (1-strength[:, :, None]) + filtered * strength[:, :, None]
    save("head_skin", Image.fromarray(np.uint8(np.clip(retouch, 0, 255))), edges)


def main():
    ART.mkdir(parents=True, exist_ok=True)
    head = mask([(94, 184), (102, 158), (111, 115), (124, 79), (141, 52),
                 (130, 50), (129, 30), (146, 22), (177, 16), (193, 23),
                 (218, 18), (251, 7), (260, 10), (269, 47), (283, 67),
                 (300, 104), (312, 145), (319, 182), (320, 206),
                 (298, 216), (276, 199), (253, 196), (245, 225), (208, 220),
                 (187, 198), (167, 204), (141, 202), (118, 217), (112, 200)])
    hair_left = mask([(126, 138), (157, 137), (167, 163), (192, 196),
                      (198, 223), (187, 239), (157, 240), (133, 249),
                      (113, 260), (107, 279), (105, 257), (110, 230),
                      (112, 210), (106, 182)])
    hair_right = mask([(260, 153), (302, 141), (316, 170), (320, 203),
                       (319, 235), (313, 263), (307, 274), (283, 269),
                       (264, 258), (260, 229)])
    save("hair_far", portrait, remove_paper(hair_left), (150, 167))
    save("hair_near", portrait, remove_paper(hair_right), (288, 174))

    specs = [
        ("left", (178, 121),
         [(150,118),(163,113),(179,108),(192,109),(209,117),(208,122),
          (194,127),(175,134),(159,132),(146,126)],
         [(164,123),(173,116),(188,114),(204,119),(193,123),(177,129),(168,130)],
         [(156,89),(160,83),(174,80),(192,80),(199,86),(198,89),(173,89)],
         (181, 86)),
        ("right", (249, 104),
         [(228,110),(229,102),(238,93),(256,88),(272,84),(276,87),
          (269,100),(262,108),(247,114),(234,116)],
         [(234,111),(242,102),(250,97),(263,97),(265,101),(255,108),(245,111)],
         [(225,81),(227,73),(243,66),(253,64),(260,68),(265,74),(256,72),(239,78)],
         (243, 73)),
    ]
    removed = []
    cream = Image.new("RGB", portrait.size, (240, 218, 198))
    for name, pivot, shell, opening, brow, brow_pivot in specs:
        footprint = mask(shell, .9)
        white = mask(opening, .18)
        cutout = np.asarray(footprint, dtype=np.float32) * (1-np.asarray(white)/255)
        save(f"eye_{name}_liner", portrait, Image.fromarray(cutout.astype(np.uint8)), pivot)
        save(f"eye_{name}_mask", cream, white, pivot)
        brow_alpha = mask(brow, .45)
        save(f"brow_{name}", portrait, brow_alpha, brow_pivot)
        removed.extend((mask(shell, 1.7), mask(brow, 1.5)))

    mouth = [(194,155),(201,153),(210,153),(223,148),(235,143),
             (250,142),(261,138),(260,144),(253,151),(244,161),
             (231,166),(217,164),(204,160)]
    save("lips", portrait, mask(mouth, .65), (228, 151))
    removed.append(mask(mouth, 1.1))
    skin_plate(removed, remove_paper(head))
    (ART / "layout.json").write_text(json.dumps(parts, indent=2) + "\n")


if __name__ == "__main__":
    main()
