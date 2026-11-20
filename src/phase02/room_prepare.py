"""Prepare two optical views and interaction layers from the approved room master."""

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt, gaussian_filter


ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "assets/environment/APPROVED_lalin_room_master.png"
ART = ROOT / "src/phase02/art"
SIZE = (540, 960)
WALK_BOX = (512, 120, 860, 120 + 348 * 16 / 9)
VANITY_BOX = (985, 0, 1410, 425 * 16 / 9)
LIPSTICK_BOX = (1306, 418, 1334, 510)
LIPSTICK_GRIP = (1320.5, 472.5)
LIPSTICK_BASE = (1320.5, 507.8)


def trace(start, segments):
    points = [start]
    for a, b, end in segments:
        for step in range(1, 13):
            t = step / 12
            s = 1 - t
            points.append(tuple(
                s ** 3 * start[i] + 3 * s * s * t * a[i]
                + 3 * s * t * t * b[i] + t ** 3 * end[i]
                for i in (0, 1)
            ))
        start = end
    return points


def matte(box, points):
    left, top, right, bottom = box
    size = (right - left, bottom - top)
    resolution = 6
    high = Image.new("L", (size[0] * resolution, size[1] * resolution))
    ImageDraw.Draw(high).polygon([
        ((x - left) * resolution, (y - top) * resolution) for x, y in points
    ], fill=255)
    return high.resize(size, Image.Resampling.LANCZOS)


def lipstick(master):
    # Exterior cap, a wider body, then the rounded gold base. Keep the adjacent
    # open lipstick and the horizontal tube in the native set plate.
    points = trace((1312.0, 421.0), [
        ((1316, 420.6), (1326, 421.1), (1328.2, 422.0)),
        ((1329.4, 423), (1329.5, 440), (1329.4, 448.6)),
        ((1329.6, 450.2), (1330.0, 451), (1330.4, 452.2)),
        ((1330.8, 467.6), (1330.3, 493.2), (1330.4, 504.8)),
        ((1329.7, 507.4), (1325.0, 507.6), (1321.5, 507.7)),
        ((1316.1, 507.6), (1311.0, 507.3), (1310.3, 505.3)),
        ((1309.8, 493), (1309.5, 465), (1309.9, 452.0)),
        ((1310.2, 449.8), (1311.1, 448.9), (1311.1, 448.2)),
        ((1311.2, 438.7), (1310.6, 423.3), (1312.0, 421.0)),
    ])
    alpha = matte(LIPSTICK_BOX, points)
    artwork = np.asarray(master.crop(LIPSTICK_BOX), dtype=np.uint8).copy()
    # Pull opaque edge color outward to prevent peach halo on new backgrounds.
    edge = np.asarray(alpha) < 245
    nearest = distance_transform_edt(edge, return_distances=False, return_indices=True)
    artwork[edge] = artwork[tuple(index[edge] for index in nearest)]
    prop = Image.fromarray(artwork)
    prop.putalpha(alpha)
    return prop


def smooth(value):
    value = np.clip(value, 0, 1)
    return value * value * (3 - 2 * value)


def remove_lipstick(master):
    source = np.asarray(master, dtype=np.float32)
    x0, y0, x1, y1 = 1308, 419, 1335, 550
    yy, xx = np.mgrid[y0:y1, x0:x1]
    # A hand-painted patch matched to the wall and counter. The color changes
    # on the rows below are the low edge of the wall and the polished countertop.
    rows = (419, 425, 434, 448, 455, 468, 480, 488, 496, 501, 505, 508, 512, 546)
    colors = np.array([
        (249, 174, 145), (248, 182, 151), (248, 173, 141), (249, 175, 142),
        (248, 174, 141), (240, 171, 141), (231, 155, 121), (226, 143, 107),
        (231, 143, 98), (226, 151, 116), (247, 204, 161),
        (252, 228, 205), (253, 244, 233), (254, 244, 233),
    ])
    painted = np.stack([
        np.interp(yy, rows, colors[:, i]) for i in range(3)
    ], axis=-1)
    wall_variation = gaussian_filter(source[y0:y1, 1332:1334].mean(axis=1), (1.3, 0))
    wall_variation -= gaussian_filter(wall_variation, (4.0, 0))
    painted += np.clip(wall_variation[:, None], -4, 4) * smooth((474 - yy) / 12)[..., None]

    # Paint the small gold bottle and mirror base hidden behind the removable tube.
    # Both are anchored to their already visible edges in the source.
    donor_x = np.clip(1308 - (xx - 1308) // 2, 1302, 1308)
    donor = source[yy, donor_x]
    bottle = smooth((1316 - xx) / 5) * smooth((yy - 451) / 7) * smooth((490 - yy) / 3.5)
    tray = smooth((1319 - xx) / 7) * smooth((yy - 484) / 4) * smooth((506 - yy) / 4)
    continuation = np.maximum(bottle, tray)[..., None]
    painted = painted * (1 - continuation) + donor * continuation

    left = np.interp(yy, (419, 421, 446, 451, 506, 512), (1310, 1308, 1308, 1307, 1307, 1308))
    right = np.interp(yy, (419, 421, 446, 451, 475, 480, 506, 513), (1330, 1332, 1332, 1333, 1334, 1335, 1335, 1335))
    # The tube below this edge stays on the counter. Feather up to its top
    # contour to remove the first visible portion of the upright tube's reflection.
    tube_top = np.interp(xx, (1308, 1315, 1320, 1328, 1335), (512, 513, 513, 514, 515))
    coverage = (smooth((xx - left + 1) / 1.6) * smooth((right - xx) / 1.7)
                * smooth((yy - 418) / 1.6) * smooth((tube_top - yy) / 2))
    # Continuing counter paint below the horizontal tube removes the longer,
    # partially occluded upright reflection without touching the horizontal tube.
    reflection_top = np.interp(xx, (1308, 1315, 1325, 1335), (528.5, 528.5, 530, 532))
    reflection_bottom = np.interp(xx, (1308, 1315, 1323, 1335), (546, 547.5, 548, 548.5))
    reflection = (smooth((xx - 1307) / 3) * smooth((1335 - xx) / 2.8)
                  * smooth((yy - reflection_top) / 4) * smooth((reflection_bottom - yy) / 3))
    reflection_tone = np.clip((xx - 1308) / 27, 0, 1)[..., None]
    left_counter = source[yy, 1305]
    right_counter = source[yy, 1337]
    reflection_paint = left_counter * (1 - reflection_tone) + right_counter * reflection_tone
    tint = (smooth((xx - 1308) / 12) * smooth((1336 - xx) / 12))[..., None]
    reflection_paint -= tint * np.array([0, 16, 19])
    painted = np.where((yy > 525)[..., None], reflection_paint, painted)
    blend = np.maximum(coverage, reflection)[..., None]
    clean = source[y0:y1, x0:x1] * (1 - blend) + painted * blend
    result = master.copy()
    result.paste(Image.fromarray(np.round(np.clip(clean, 0, 255)).astype(np.uint8)), (x0, y0))
    return result


def chair(master):
    # Source outline of the existing velvet vanity chair. Points run around
    # the back, seat and exposed legs, and stop where the cat's cushion occludes it.
    points = trace((826, 508), [
        ((826, 496), (830, 490), (841, 488)),
        ((865, 482), (892, 487), (909, 494)),
        ((939, 504), (984, 511), (995, 543)),
        ((1016, 556), (1035, 567), (1040, 595)),
        ((1044, 609), (1045, 626), (1044, 637)),
        ((1108, 631), (1189, 643), (1200, 666)),
        ((1206, 686), (1204, 717), (1189, 730)),
        ((1190, 742), (1193, 750), (1194, 763)),
        ((1190, 765), (1184, 765), (1180, 766)),
        ((1178, 756), (1176, 742), (1173, 737)),
        ((1139, 744), (1078, 752), (1055, 752)),
        ((1055, 772), (1055, 796), (1056, 808)),
        ((1052, 810), (1047, 811), (1042, 810)),
        ((1043, 791), (1040, 770), (1040, 753)),
        ((1025, 753), (1009, 752), (1003, 752)),
        ((992, 803), (986, 874), (978, 918)),
        ((974, 922), (970, 922), (966, 918)),
        ((968, 873), (983, 805), (986, 751)),
        ((952, 746), (923, 743), (912, 734)),
        ((900, 775), (880, 847), (869, 876)),
        ((865, 881), (858, 881), (856, 877)),
        ((867, 842), (886, 769), (900, 732)),
        ((891, 730), (883, 721), (874, 706)),
        ((867.5, 692), (863, 673), (859, 655)),
        ((854.7, 638), (850.5, 620), (847, 604)),
        ((842.5, 583), (836.3, 559), (831.4, 540)),
        ((827, 525), (824.8, 516), (826, 508)),
    ])
    bounds = (821, 481, 1208, 925)
    patch = master.crop(bounds)
    patch.putalpha(matte(bounds, points))
    cutout = Image.new("RGBA", master.size)
    cutout.paste(patch, bounds[:2])
    return cutout


def viewport(source, box):
    return source.transform(SIZE, Image.Transform.EXTENT, box, Image.Resampling.BICUBIC)


def shot_point(point, box):
    scale = SIZE[0] / (box[2] - box[0])
    return [round((point[0] - box[0]) * scale, 3), round((point[1] - box[1]) * scale, 3)]


def main():
    ART.mkdir(parents=True, exist_ok=True)
    with Image.open(MASTER) as source:
        master = source.convert("RGB")
    clean = remove_lipstick(master)
    occluder = chair(master)
    clean.save(ART / "room_clean_plate.png")
    viewport(master, WALK_BOX).save(ART / "room_walk.png")
    viewport(clean, VANITY_BOX).save(ART / "room_vanity.png")
    viewport(occluder, WALK_BOX).save(ART / "room_walk_foreground.png")
    viewport(occluder, VANITY_BOX).save(ART / "room_vanity_foreground.png")
    lipstick(master).save(ART / "lipstick.png")

    vanity_scale = SIZE[0] / (VANITY_BOX[2] - VANITY_BOX[0])
    origin = LIPSTICK_BOX[:2]
    layout = {
        "source": str(MASTER.relative_to(ROOT)),
        "screen_wh": SIZE,
        "walk": {
            "source_xyxy": WALK_BOX,
            "background": "room_walk.png",
            "foreground": "room_walk_foreground.png",
            "heel_contact_path_xy": [[125, 850], [390, 860]],
            "heel_contact_band_y": [844, 876],
        },
        "vanity": {
            "source_xyxy": VANITY_BOX,
            "background": "room_vanity.png",
            "foreground": "room_vanity_foreground.png",
            "lipstick": {
                "texture": "lipstick.png",
                "source_xyxy": LIPSTICK_BOX,
                "scale": round(vanity_scale, 9),
                "texture_top_left_xy": shot_point(origin, VANITY_BOX),
                "base_xy": shot_point(LIPSTICK_BASE, VANITY_BOX),
                "grip_xy": shot_point(LIPSTICK_GRIP, VANITY_BOX),
                "grip_pivot_px": [LIPSTICK_GRIP[i] - origin[i] for i in (0, 1)],
            },
            "small_mirror_center_xy": shot_point((1284, 370), VANITY_BOX),
        },
    }
    (ART / "room_layout.json").write_text(json.dumps(layout, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
