"""Animate one approved portrait with local, hand-keyed facial controls."""

import argparse
from dataclasses import dataclass, fields
from pathlib import Path
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt, map_coordinates


ROOT = Path(__file__).resolve().parents[2]
PORTRAIT = ROOT / "assets/character/approved_initial_3/02_lalin_expressions_fashion.png"
OUTPUT = ROOT / "outputs/phase01/lalin_face_test.mp4"
WIDTH, HEIGHT = 540, 960
FPS, FRAME_COUNT = 30, 150
X0, Y0, SOURCE_WIDTH = 114.0, -8.0, 228.0
PAD = 44


@dataclass(frozen=True)
class Pose:
    brow_left: float = 0
    brow_right: float = 0
    gaze_x: float = 0
    gaze_y: float = 0
    lid_left: float = 1
    lid_right: float = 1
    cheek: float = 0
    smile: float = 0
    jaw: float = 0
    round_mouth: float = 0
    head_x: float = 0
    head_y: float = 0
    head_angle: float = 0
    shoulder: float = 0


# Frame numbers are zero-based. Breakdowns give gaze and blink their own timing.
KEYS = (
    (0, Pose()),
    (8, Pose()),
    (15, Pose(gaze_x=12, gaze_y=-1, head_angle=-1)),
    (27, Pose(brow_left=-8, brow_right=1, gaze_x=15, gaze_y=-2,
              lid_left=.78, lid_right=.83, cheek=1.6, smile=2, head_x=2, head_angle=-3)),
    (41, Pose(brow_left=-8, brow_right=1, gaze_x=15, gaze_y=-2,
              lid_left=.78, lid_right=.83, cheek=1.6, smile=2, head_x=2, head_angle=-3)),
    (49, Pose(brow_left=-8, brow_right=-2, gaze_x=10, gaze_y=-9,
              lid_left=.86, lid_right=.88, cheek=1.3, smile=1.6, head_angle=-3.5)),
    (56, Pose(brow_left=-5, brow_right=-2, gaze_x=5, gaze_y=-9,
              cheek=1, smile=1.2, head_angle=-3)),
    (64, Pose(brow_left=-2, gaze_x=4, head_angle=-1.5)),
    (68, Pose(brow_left=-1, lid_left=.04, lid_right=.04, cheek=1, head_y=1)),
    (72, Pose(brow_left=-3, brow_right=-3, gaze_x=8, lid_left=.76, lid_right=.80)),
    (79, Pose(brow_left=-8, brow_right=-7, gaze_x=11, gaze_y=1,
              lid_left=1.23, lid_right=1.20, smile=-2.3, jaw=17, round_mouth=1,
              head_y=-3, head_angle=4, shoulder=1.5)),
    (90, Pose(brow_left=-7, brow_right=-6, gaze_x=11, gaze_y=1,
              lid_left=1.20, lid_right=1.18, smile=-2, jaw=15, round_mouth=.9,
              head_y=-2, head_angle=3.5, shoulder=1)),
    (102, Pose(gaze_x=5, lid_left=.88, lid_right=.87, cheek=1.5, smile=2, head_angle=1)),
    (107, Pose(brow_left=-2, brow_right=-1, gaze_x=4, lid_left=.46, lid_right=.43,
               cheek=2.5, smile=3, jaw=4, head_y=1, shoulder=1.5)),
    (114, Pose(brow_left=-4, brow_right=-3, lid_left=.06, lid_right=.08, cheek=4,
               smile=3.5, jaw=18, head_y=-4, head_angle=4.5, shoulder=-3.5)),
    (121, Pose(brow_left=-2, lid_left=.23, lid_right=.19, cheek=2.8,
               smile=3.4, jaw=8, head_y=-1, head_angle=2, shoulder=.4)),
    (127, Pose(brow_left=-3, brow_right=-2, lid_left=.11, lid_right=.12, cheek=3.6,
               smile=3.4, jaw=14, head_y=-3, head_angle=3.5, shoulder=-2.4)),
    (136, Pose(brow_left=-2, gaze_x=5, gaze_y=1, lid_left=.74, lid_right=.78, cheek=2,
               smile=2.8, jaw=1, head_angle=1, shoulder=-.5)),
    (149, Pose(brow_left=-1, lid_left=.95, lid_right=.94, cheek=.8, smile=1)),
)


def ease(value):
    value = np.clip(value, 0, 1)
    return value * value * (3 - 2 * value)


def pose_at(frame):
    for (start, first), (end, last) in zip(KEYS, KEYS[1:]):
        if frame <= end:
            weight = float(ease((frame - start) / (end - start)))
            return Pose(*(getattr(first, f.name) * (1 - weight) + getattr(last, f.name) * weight
                          for f in fields(Pose)))
    return KEYS[-1][1]


def texture_sample(texture, x, y):
    return np.stack([
        map_coordinates(texture[:, :, channel], (y, x), order=1, mode="nearest")
        for channel in range(3)
    ], axis=-1)


def falloff(x, y, cx, cy, rx, ry):
    return ease(1 - ((x - cx) / rx) ** 2 - ((y - cy) / ry) ** 2)


def cubic_points(start, segments):
    points = [start]
    t = np.linspace(0, 1, 21, endpoint=True)[1:, None]
    for control_a, control_b, end in segments:
        segment = ((1 - t) ** 3 * np.array(start)
                   + 3 * (1 - t) ** 2 * t * np.array(control_a)
                   + 3 * (1 - t) * t ** 2 * np.array(control_b)
                   + t ** 3 * np.array(end))
        points.extend(map(tuple, segment))
        start = end
    return points


class Eye:
    def __init__(self, grid_x, center, slope, socket, lash_limits, start, segments):
        self.center = center
        self.slope = slope
        left, right = lash_limits
        self.lash_progress = np.clip((grid_x - left) / (right - left), 0, 1)
        self.bounds = (int(center[0] - 24), int(center[1] - 18), 57, 38)
        x0, y0, width, height = self.bounds
        xx, yy = np.meshgrid(np.arange(width * 4) / 4 + x0, np.arange(height * 4) / 4 + y0)
        shape = Image.new("L", (width * 4, height * 4))
        contour = cubic_points(start, segments)
        ImageDraw.Draw(shape).polygon([((a - x0) * 4, (b - y0) * 4) for a, b in contour], fill=255)
        self.shape = np.asarray(shape, dtype=np.float32) / 255
        self.rim_shadow = 1 - ease(distance_transform_edt(self.shape) / 10)
        self.xx = xx.astype(np.float32)
        self.yy = yy.astype(np.float32)
        self.lid_span = ease(1 - ((grid_x - socket[0]) / socket[1]) ** 2)

    def closure_curve(self, opening):
        return -2.3 * np.sin(np.pi * self.lash_progress) * ease((.36 - opening) / .27)

    def baseline(self, x):
        cx, cy = self.center
        return cy + self.slope * (x - cx)

    def sample_lids(self, x, y, opening):
        baseline = self.baseline(x)
        signed_distance = y - baseline
        distance_from_center = np.abs(signed_distance)
        curve = self.closure_curve(opening)
        signed_distance -= curve * ease(1 - distance_from_center / 22)
        distance = np.abs(signed_distance)
        gap = 1 + (opening - 1) * self.lid_span
        inner = np.where(signed_distance < 0, 13, 9)
        outer = np.where(signed_distance < 0, 29, 22)
        stretched = inner * gap
        # Pin the socket perimeter while the lashes meet along their curved baseline.
        socket_distance = inner + (distance - stretched) * (outer - inner) / (outer - stretched)
        sample_distance = np.where(distance < stretched, distance / gap, socket_distance)
        sample_distance = np.where(distance < outer, sample_distance, distance)
        return baseline + np.copysign(sample_distance, signed_distance)

    def paint_closed_lash(self, face, x, y, opening):
        closure = ease((.21 - opening) / .15)
        if not closure:
            return
        progress = self.lash_progress
        width = .4 + .9 * np.maximum(0, np.sin(np.pi * progress)) ** .8
        line = self.baseline(x) + self.closure_curve(opening)
        edge = ease(progress * 13) * ease((1 - progress) * 13)
        opacity = closure * edge * ease((width + .65 - np.abs(y - line)) / .83)
        face += opacity[:, :, None] * (np.array([43, 21, 16]) - face)

    def replace_iris(self, face, x, y, state):
        if not (state.gaze_x or state.gaze_y):
            return
        cx, cy = self.center
        x0, y0, width, height = self.bounds
        radius = np.hypot((self.xx - cx - state.gaze_x) / 8.6,
                          (self.yy - cy - state.gaze_y) / 8.9)
        iris_mask = ease((1.04 - radius) / .13)
        pupil = ease((.60 - radius) / .10)
        iris_light = ease((1.0 - radius) / .34)
        warm = ease((self.yy - cy - state.gaze_y + 4) / 12)
        rim = np.array([36, 18, 11])
        iris = rim + iris_light[:, :, None] * np.array([53, 26, 12])
        iris += (warm * iris_light)[:, :, None] * np.array([40, 19, 8])
        iris = iris * (1 - pupil[:, :, None]) + pupil[:, :, None] * np.array([14, 8, 7])
        sparkle = ease((1.60 - np.hypot(self.xx - cx - state.gaze_x - 2,
                                        self.yy - cy - state.gaze_y + 4)) / .85)
        iris = iris * (1 - sparkle[:, :, None]) + sparkle[:, :, None] * np.array([250, 240, 227])
        shadow = ease((self.yy - (cy - 6 + self.slope * (self.xx - cx))) / 8)
        sclera = np.array([161, 126, 107]) + shadow[:, :, None] * np.array([76, 98, 103])
        sclera -= self.rim_shadow[:, :, None] * np.array([38, 40, 38])
        eye = sclera * (1 - iris_mask[:, :, None]) + iris * iris_mask[:, :, None]
        left = max(0, PAD + int(np.floor((x0 - X0) * WIDTH / SOURCE_WIDTH)))
        right = min(face.shape[1], PAD + int(np.ceil((x0 + width - X0) * WIDTH / SOURCE_WIDTH)))
        top = max(0, int(np.floor((y0 - Y0 - 15) * WIDTH / SOURCE_WIDTH)))
        bottom = min(face.shape[0], int(np.ceil((y0 + height - Y0 + 15) * WIDTH / SOURCE_WIDTH)))
        region = np.s_[top:bottom, left:right]
        ey = (y[region] - y0) * 4
        ex = (x[region] - x0) * 4
        opacity = map_coordinates(self.shape, (ey, ex), order=1, mode="constant")
        opacity *= float(ease(np.hypot(state.gaze_x, state.gaze_y) / 1.6))
        face[region] += opacity[:, :, None] * (texture_sample(eye, ex, ey) - face[region])


class Renderer:
    def __init__(self):
        self.texture = np.asarray(Image.open(PORTRAIT).convert("RGB"), dtype=np.float32)
        scale = SOURCE_WIDTH / WIDTH
        self.full_x, self.full_y = np.meshgrid(
            np.arange(-PAD, WIDTH + PAD, dtype=np.float32) * scale + X0,
            np.arange(HEIGHT, dtype=np.float32) * scale + Y0,
        )
        self.animated_rows = int((325 - Y0) / scale)
        self.face_rows = int((233 - Y0) / scale)
        self.x = self.full_x[:self.face_rows]
        self.y = self.full_y[:self.face_rows]
        self.base = texture_sample(self.texture, self.full_x, self.full_y)
        self.head_weight = ease((259 - self.full_y[:self.animated_rows]) / 77)
        self.shoulder = falloff(self.full_x[:self.animated_rows], self.full_y[:self.animated_rows],
                                287, 268, 100, 47)
        self.left_brow = falloff(self.x, self.y, 181, 83, 46, 24)
        self.right_brow = falloff(self.x, self.y, 245, 71, 39, 25)
        self.left_cheek = falloff(self.x, self.y, 197, 137, 34, 24)
        self.right_cheek = falloff(self.x, self.y, 266, 125, 20, 20)
        self.chin = falloff(self.x, self.y, 236, 183, 45, 30)
        self.lip_left = falloff(self.x, self.y, 205, 157, 27, 20)
        self.lip_right = falloff(self.x, self.y, 255, 142, 25, 18)
        self.pucker = falloff(self.x, self.y, 229, 154, 45, 25)
        self.left_eye = Eye(self.x, (179.1, 122.4), -.17, (178, 49), (151, 208),
                            (165, 124), (
                                ((173, 113.5), (191, 112), (205, 119.2)),
                                ((192, 123), (178, 130.4), (168, 129.3)),
                                ((165.8, 129.2), (164.4, 126.5), (165, 124)),
                            ))
        self.right_eye = Eye(self.x, (239.5, 105.8), -.33, (248, 42), (233, 278),
                             (234, 112), (
                                 ((238, 103), (248, 94.5), (261.6, 97)),
                                 ((268.7, 98.3), (263, 104.7), (255.4, 108)),
                                 ((248, 111.5), (240.5, 112.3), (234, 112)),
                             ))

    def mouth_split(self, x, y, jaw, round_mouth):
        # Split the source at its existing lip seam and reveal the painted interior.
        edge_x = [197, 203, 211, 221, 233, 245, 253, 259]
        edge_y = [155.7, 157.7, 158.1, 155.8, 152.7, 148.9, 145.5, 139.7]
        seam = np.interp(x, edge_x, edge_y)
        progress = np.clip((x - edge_x[0]) / (edge_x[-1] - edge_x[0]), 0, 1)
        profile = np.maximum(0, np.sin(np.pi * progress)) ** (.9 + round_mouth * 1.65)
        split = profile * jaw
        upper_edge = seam - split * .21
        lower_edge = seam + split * .79
        moved_up = split * .21 * ease(1 - (upper_edge - y) / 16)
        moved_down = split * .79 * ease(1 - (y - lower_edge) / 34)
        source_y = np.where(y < upper_edge, y + moved_up, y - moved_down)
        interior = ease((y - upper_edge) / .65) * ease((lower_edge - y) / .65)
        depth = np.clip((y - upper_edge) / np.maximum(split, 1), 0, 1)
        tongue = ease((depth - .66) * 3) * ease((profile - .45) * 2)
        color = np.array([54, 15, 17]) + tongue[:, :, None] * np.array([68, 21, 28])
        teeth_width = ease((progress - .12) * 8) * ease((.91 - progress) * 8)
        teeth_depth = split * .34 * teeth_width
        teeth = (ease((upper_edge + teeth_depth - y) / 1.05)
                 * ease((jaw - 4) / 5) * (1 - round_mouth))
        color += teeth[:, :, None] * (np.array([238, 204, 174]) - color)
        return source_y.astype(np.float32), interior, color

    def expression(self, state):
        inward = state.round_mouth * (self.x - 229) * self.pucker
        x = self.x + .40 * inward
        y = (self.y - state.brow_left * self.left_brow - state.brow_right * self.right_brow
             + state.cheek * (self.left_cheek + .8 * self.right_cheek)
             + state.smile * (.55 * self.lip_left + self.lip_right)
             - state.jaw * .23 * self.chin - .13 * inward)
        before_lids = y
        for eye, lid in ((self.left_eye, state.lid_left), (self.right_eye, state.lid_right)):
            if lid != 1:
                y = eye.sample_lids(x, y, lid)
        y, interior, inside_color = self.mouth_split(x, y, state.jaw, state.round_mouth)
        face = texture_sample(self.texture, x, y)
        self.left_eye.replace_iris(face, x, y, state)
        self.right_eye.replace_iris(face, x, y, state)
        self.left_eye.paint_closed_lash(face, x, before_lids, state.lid_left)
        self.right_eye.paint_closed_lash(face, x, before_lids, state.lid_right)
        return (face + interior[:, :, None] * (inside_color - face)).astype(np.float32)

    def frame(self, index):
        state = pose_at(index)
        canvas = self.base.copy()
        canvas[:self.face_rows] = self.expression(state)
        angle = np.deg2rad(state.head_angle)
        cos, sin = np.cos(angle), np.sin(angle)
        pivot_x, pivot_y = 230, 216
        xx, yy = self.full_x[:self.animated_rows], self.full_y[:self.animated_rows]
        dx, dy = xx - pivot_x, yy - pivot_y
        inverse_x = (dx - state.head_x) * cos + (dy - state.head_y) * sin
        inverse_y = -(dx - state.head_x) * sin + (dy - state.head_y) * cos
        scale = WIDTH / SOURCE_WIDTH
        lookup_x = (xx + self.head_weight * (inverse_x - dx) - X0) * scale + PAD
        lookup_y = (yy + self.head_weight * (inverse_y - dy) - self.shoulder * state.shoulder - Y0) * scale
        canvas[:self.animated_rows] = texture_sample(canvas, lookup_x, lookup_y)
        return np.rint(np.clip(canvas[:, PAD:PAD + WIDTH], 0, 255)).astype(np.uint8)


def render_video(renderer, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="lalin-face-", dir=output.parent) as temporary:
        staged = Path(temporary) / "face.mp4"
        command = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS),
            "-i", "-", "-an", "-c:v", "libx264", "-threads", "2", "-preset", "medium",
            "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(staged),
        ]
        with subprocess.Popen(command, stdin=subprocess.PIPE) as encoder:
            try:
                for frame in range(FRAME_COUNT):
                    encoder.stdin.write(renderer.frame(frame).tobytes())
            finally:
                encoder.stdin.close()
            if encoder.wait() != 0:
                raise RuntimeError("FFmpeg video çıktısını yazamadı.")
        staged.replace(output)


def main():
    parser = argparse.ArgumentParser(description="Lalin Faz 01 mimik testi")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--still", type=int, metavar="FRAME", help="Tek kareyi PNG olarak yazar.")
    args = parser.parse_args()
    if args.still is None:
        if args.output.suffix.lower() != ".mp4":
            parser.error("Video çıktısı için .mp4 uzantılı bir yol girin.")
        render_video(Renderer(), args.output)
    else:
        if not 0 <= args.still < FRAME_COUNT or args.output.suffix.lower() != ".png":
            parser.error("--still için 0–149 arasında kare ve .png çıktı yolu girin.")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(Renderer().frame(args.still)).save(args.output)


if __name__ == "__main__":
    main()
