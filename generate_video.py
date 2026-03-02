#!/usr/bin/env python3
"""Generate analysis video from OnePlus mic test recording.

Creates a 1920x1080 video with:
- Segment labels showing current test configuration
- Cleaned-up subtitles from transcription
- Real-time stereo field visualization (Lissajous + L/R meters)
- Original audio as soundtrack
"""

import json
import glob
import re
import subprocess
import sys
import pathlib
import numpy as np
from scipy.io import wavfile
from PIL import Image, ImageDraw, ImageFont

# ── Config ──────────────────────────────────────────────────────────────
ROOT = pathlib.Path(__file__).resolve().parent
AUDIO_PATH = ROOT / "One Plus audio Testing.wav"
SEG_DIR = ROOT / "segments"
TRANS_PATH = ROOT / "transcription.md"
OUTPUT_PATH = ROOT / "oneplus_mic_test.mp4"

WIDTH, HEIGHT = 1920, 1080
FPS = 30
LISSAJOUS_SAMPLES = 1536

# ── Colors ──────────────────────────────────────────────────────────────
BG = (13, 17, 23)
PANEL_BG = (22, 27, 34)
TEXT_WHITE = (240, 240, 245)
TEXT_GRAY = (155, 160, 172)
TEXT_DIM = (90, 95, 108)
METER_L = (33, 150, 243)
METER_R = (233, 30, 99)
METER_BG = (30, 34, 45)
LISS_BG = (18, 22, 30)
LISS_GRID = (35, 40, 52)
LISS_DOT = (76, 175, 80)
PROGRESS_BG = (30, 34, 45)
PROGRESS_FG = (88, 166, 255)
SUB_BG = (18, 22, 30)

CAT_COLORS = {
    "INTRODUCTION":    (96, 125, 139),
    "ADDRESS PATTERN": (33, 150, 243),
    "PROXIMITY TEST":  (76, 175, 80),
    "PHONE-TO-EAR":    (255, 152, 0),
    "HANDLING NOISE":   (233, 30, 99),
    "NOISE FLOOR":     (156, 39, 176),
    "CASE TEST":       (0, 188, 212),
    "STAND TEST":      (255, 193, 7),
    "360 WALK":        (255, 87, 34),
    "OFF-AXIS":        (63, 81, 181),
}

SEG_CATEGORY = {
    1: "INTRODUCTION",
    2: "ADDRESS PATTERN", 3: "ADDRESS PATTERN", 4: "ADDRESS PATTERN",
    5: "PROXIMITY TEST", 6: "PROXIMITY TEST", 7: "PROXIMITY TEST", 8: "PROXIMITY TEST",
    9: "ADDRESS PATTERN", 10: "ADDRESS PATTERN",
    11: "PHONE-TO-EAR", 12: "PHONE-TO-EAR",
    13: "ADDRESS PATTERN",
    14: "HANDLING NOISE", 15: "HANDLING NOISE",
    16: "NOISE FLOOR",
    17: "CASE TEST", 18: "CASE TEST", 19: "CASE TEST",
    20: "STAND TEST", 21: "STAND TEST",
    22: "360 WALK",
    23: "OFF-AXIS", 24: "OFF-AXIS",
}

# ── Fonts ───────────────────────────────────────────────────────────────
def load_fonts():
    bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    mono = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    if not pathlib.Path(bold).exists():
        bold = regular
    if not pathlib.Path(mono).exists():
        mono = regular
    return {
        "badge":   ImageFont.truetype(bold, 22),
        "title":   ImageFont.truetype(bold, 38),
        "detail":  ImageFont.truetype(regular, 20),
        "sub":     ImageFont.truetype(regular, 28),
        "time":    ImageFont.truetype(mono, 18),
        "meter":   ImageFont.truetype(bold, 16),
        "device":  ImageFont.truetype(regular, 16),
        "liss_label": ImageFont.truetype(bold, 14),
    }

# ── Data loaders ────────────────────────────────────────────────────────
def load_segments():
    segments = []
    for f in sorted(glob.glob(str(SEG_DIR / "*.json"))):
        d = json.load(open(f))
        if d.get("segment_number") and d.get("start_time") is not None:
            segments.append(d)
    segments.sort(key=lambda s: s["start_time"])
    return segments


def parse_subtitles(path):
    text = path.read_text()
    pattern = r'\*\*\[(\d+:\d+\.\d+)\s*[—–-]\s*(\d+:\d+\.\d+)\]\*\*\s*(.*?)(?=\n\n|\*\*\[|\Z)'
    subs = []
    for m in re.finditer(pattern, text, re.DOTALL):
        s, e, content = m.groups()
        subs.append((_ts(s), _ts(e), content.strip().replace('\n', ' ')))
    return subs


def _ts(s):
    p = s.split(":")
    return float(p[0]) * 60 + float(p[1])


def load_audio():
    rate, data = wavfile.read(str(AUDIO_PATH))
    data = data.astype(np.float64) / 32768.0
    if data.ndim == 1:
        return rate, data, data.copy()
    return rate, data[:, 0], data[:, 1]


# ── Audio pre-computation ───────────────────────────────────────────────
def precompute_levels(rate, left, right, fps):
    total_frames = int(len(left) / rate * fps)
    win = int(rate * 0.03)  # 30ms window

    l_levels = np.zeros(total_frames)
    r_levels = np.zeros(total_frames)
    balance = np.zeros(total_frames)

    for i in range(total_frames):
        c = int(i / fps * rate)
        s = max(0, c - win // 2)
        e = min(len(left), s + win)
        if e <= s:
            continue
        l_rms = np.sqrt(np.mean(left[s:e] ** 2))
        r_rms = np.sqrt(np.mean(right[s:e] ** 2))
        l_levels[i] = l_rms
        r_levels[i] = r_rms
        total = l_rms + r_rms
        balance[i] = (r_rms - l_rms) / total if total > 1e-10 else 0

    # Smooth with EMA
    alpha = 0.35
    for i in range(1, total_frames):
        l_levels[i] = alpha * l_levels[i] + (1 - alpha) * l_levels[i - 1]
        r_levels[i] = alpha * r_levels[i] + (1 - alpha) * r_levels[i - 1]
        balance[i] = alpha * balance[i] + (1 - alpha) * balance[i - 1]

    return l_levels, r_levels, balance


# ── Lookup helpers ──────────────────────────────────────────────────────
def seg_at(segments, t):
    for s in segments:
        if s["start_time"] <= t < s["end_time"]:
            return s
    return None


def sub_at(subs, t):
    for s, e, txt in subs:
        if s <= t <= e:
            return txt
    return ""


# ── Text wrapping ───────────────────────────────────────────────────────
def wrap(text, font, max_w, draw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_centered(draw, y, text, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text(((WIDTH - w) // 2, y), text, fill=fill, font=font)


# ── Frame renderer ──────────────────────────────────────────────────────
def render_frame(t, total_dur, seg, subtitle, l_lev, r_lev, bal,
                 left, right, rate, fonts, prev_seg_num):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    # ── Device watermark ──
    draw.text((WIDTH - 340, 20),
              "OnePlus Nord 3 5G  |  48kHz Stereo",
              fill=TEXT_DIM, font=fonts["device"])

    # ── Header: category badge + title + details ──
    if seg:
        sn = seg["segment_number"]
        cat = SEG_CATEGORY.get(sn, "")
        cat_col = CAT_COLORS.get(cat, (100, 100, 100))
        title = seg.get("title", "")

        # Segment counter
        draw.text((40, 30), f"Segment {sn}/24", fill=TEXT_DIM, font=fonts["detail"])

        # Category badge
        if cat:
            badge_text = f"  {cat}  "
            bb = draw.textbbox((0, 0), badge_text, font=fonts["badge"])
            bw = bb[2] - bb[0] + 16
            bh = bb[3] - bb[1] + 12
            bx = (WIDTH - bw) // 2
            by = 50
            draw.rounded_rectangle((bx, by, bx + bw, by + bh), radius=6, fill=cat_col)
            draw.text((bx + 8, by + 4), badge_text, fill=TEXT_WHITE, font=fonts["badge"])

        # Title
        text_centered(draw, 100, title, fonts["title"], TEXT_WHITE)

        # Config detail line
        parts = []
        d = seg.get("distance_cm")
        if d is not None:
            parts.append(f"~{d}cm")
        ap = seg.get("address_pattern", "")
        if ap:
            parts.append(ap)
        co = seg.get("case_on")
        if co is not None:
            parts.append("With case" if co else "No case")
        mt = seg.get("mount")
        if mt:
            parts.append(mt.split("(")[0].strip())
        detail = "  \u2022  ".join(parts)
        if detail:
            text_centered(draw, 150, detail, fonts["detail"], TEXT_GRAY)

        # Transition flash — brief tinted bar when segment changes
        if prev_seg_num is not None and sn != prev_seg_num:
            draw.rectangle((0, 195, WIDTH, 200), fill=cat_col)
    else:
        draw.text((40, 30), "Between segments", fill=TEXT_DIM, font=fonts["detail"])

    # ── L/R Level Meters (horizontal, from center) ──
    meter_cx = WIDTH // 2
    meter_y = 220
    meter_h = 36
    max_bar = 380

    # Background track
    draw.rounded_rectangle(
        (meter_cx - max_bar - 12, meter_y,
         meter_cx + max_bar + 12, meter_y + meter_h),
        radius=6, fill=METER_BG
    )

    # L bar (grows left from center)
    l_bar_w = int(min(1.0, l_lev * 9) * max_bar)
    if l_bar_w > 2:
        # Gradient approximation: brighter near tip
        draw.rounded_rectangle(
            (meter_cx - l_bar_w, meter_y + 3,
             meter_cx - 3, meter_y + meter_h // 2 - 1),
            radius=3, fill=METER_L
        )

    # R bar (grows right from center)
    r_bar_w = int(min(1.0, r_lev * 9) * max_bar)
    if r_bar_w > 2:
        draw.rounded_rectangle(
            (meter_cx + 3, meter_y + meter_h // 2 + 1,
             meter_cx + r_bar_w, meter_y + meter_h - 3),
            radius=3, fill=METER_R
        )

    # Center divider
    draw.rectangle(
        (meter_cx - 1, meter_y, meter_cx + 1, meter_y + meter_h),
        fill=TEXT_DIM
    )

    # Labels + dB readout
    l_db = 20 * np.log10(l_lev + 1e-10)
    r_db = 20 * np.log10(r_lev + 1e-10)
    draw.text((meter_cx - max_bar - 80, meter_y + 2),
              f"L {l_db:+.0f}dB", fill=METER_L, font=fonts["meter"])
    draw.text((meter_cx + max_bar + 20, meter_y + meter_h - 20),
              f"R {r_db:+.0f}dB", fill=METER_R, font=fonts["meter"])

    # ── Stereo Balance Indicator ──
    bal_y = meter_y + meter_h + 18
    bal_w = 500
    bal_x = (WIDTH - bal_w) // 2

    draw.rounded_rectangle(
        (bal_x, bal_y, bal_x + bal_w, bal_y + 6),
        radius=3, fill=METER_BG
    )
    # Center tick
    draw.rectangle(
        (bal_x + bal_w // 2 - 1, bal_y - 5,
         bal_x + bal_w // 2 + 1, bal_y + 11),
        fill=TEXT_DIM
    )
    # Ball
    bx = bal_x + bal_w // 2 + int(bal * bal_w * 0.45)
    bx = max(bal_x + 6, min(bal_x + bal_w - 6, bx))
    bc = METER_L if bal < -0.05 else METER_R if bal > 0.05 else TEXT_WHITE
    draw.ellipse((bx - 7, bal_y - 4, bx + 7, bal_y + 10), fill=bc)
    draw.text((bal_x - 18, bal_y - 4), "L", fill=TEXT_DIM, font=fonts["liss_label"])
    draw.text((bal_x + bal_w + 6, bal_y - 4), "R", fill=TEXT_DIM, font=fonts["liss_label"])

    # ── Lissajous Stereo Field Display ──
    liss_size = 380
    liss_x = (WIDTH - liss_size) // 2
    liss_y = bal_y + 35

    # Background panel
    draw.rounded_rectangle(
        (liss_x - 10, liss_y - 10,
         liss_x + liss_size + 10, liss_y + liss_size + 10),
        radius=8, fill=LISS_BG
    )

    # Grid: cross + diagonals
    cx = liss_x + liss_size // 2
    cy = liss_y + liss_size // 2
    draw.line([(liss_x, cy), (liss_x + liss_size, cy)], fill=LISS_GRID, width=1)
    draw.line([(cx, liss_y), (cx, liss_y + liss_size)], fill=LISS_GRID, width=1)
    # M/S diagonals
    off = liss_size // 2 - 10
    draw.line([(cx - off, cy - off), (cx + off, cy + off)], fill=(28, 32, 42), width=1)
    draw.line([(cx - off, cy + off), (cx + off, cy - off)], fill=(28, 32, 42), width=1)

    # Axis labels
    draw.text((liss_x + liss_size + 14, cy - 8), "+R", fill=METER_R, font=fonts["liss_label"])
    draw.text((liss_x - 26, cy - 8), "-L", fill=METER_L, font=fonts["liss_label"])
    draw.text((cx - 4, liss_y - 22), "+", fill=TEXT_DIM, font=fonts["liss_label"])
    draw.text((cx - 4, liss_y + liss_size + 6), "-", fill=TEXT_DIM, font=fonts["liss_label"])

    # Plot audio samples as Lissajous dots
    center_sample = int(t * rate)
    half = LISSAJOUS_SAMPLES // 2
    s_start = max(0, center_sample - half)
    s_end = min(len(left), s_start + LISSAJOUS_SAMPLES)

    if s_end > s_start + 10:
        l_chunk = left[s_start:s_end]
        r_chunk = right[s_start:s_end]

        # Auto-scale: normalize chunk so peak fills ~80% of display
        peak = max(np.max(np.abs(l_chunk)), np.max(np.abs(r_chunk)), 1e-6)
        scale = (liss_size * 0.40) / peak

        # Subsample for performance: ~300 dots
        step = max(1, len(l_chunk) // 300)
        points = []
        for i in range(0, len(l_chunk), step):
            px = int(cx + l_chunk[i] * scale)
            py = int(cy - r_chunk[i] * scale)
            px = max(liss_x + 2, min(liss_x + liss_size - 2, px))
            py = max(liss_y + 2, min(liss_y + liss_size - 2, py))
            points.append((px, py))

        # Draw dots — 2x2 for visibility
        for px, py in points:
            draw.rectangle((px, py, px + 1, py + 1), fill=LISS_DOT)

    # Label
    draw.text((liss_x - 10, liss_y + liss_size + 16),
              "STEREO FIELD", fill=TEXT_DIM, font=fonts["liss_label"])
    # Stereo width indicator
    if s_end > s_start + 10:
        mid = (l_chunk + r_chunk) / 2
        side = (l_chunk - r_chunk) / 2
        mid_rms = np.sqrt(np.mean(mid ** 2))
        side_rms = np.sqrt(np.mean(side ** 2))
        width_pct = min(100, int(side_rms / (mid_rms + 1e-10) * 100))
        draw.text((liss_x + liss_size - 70, liss_y + liss_size + 16),
                  f"Width: {width_pct}%", fill=TEXT_DIM, font=fonts["liss_label"])

    # ── Subtitle ──
    sub_y_start = liss_y + liss_size + 50
    if subtitle:
        lines = wrap(subtitle, fonts["sub"], WIDTH - 240, draw)
        lines = lines[:3]
        line_h = 36
        total_h = len(lines) * line_h + 20
        # Background panel
        draw.rounded_rectangle(
            (100, sub_y_start - 10,
             WIDTH - 100, sub_y_start + total_h),
            radius=8, fill=SUB_BG
        )
        for i, line in enumerate(lines):
            y = sub_y_start + i * line_h
            # Shadow
            text_centered(draw, y + 1, line, fonts["sub"], (0, 0, 0))
            text_centered(draw, y, line, fonts["sub"], TEXT_WHITE)

    # ── Progress bar + timestamp ──
    prog_y = HEIGHT - 50
    bar_x, bar_w = 100, WIDTH - 200
    draw.rounded_rectangle(
        (bar_x, prog_y, bar_x + bar_w, prog_y + 5),
        radius=2, fill=PROGRESS_BG
    )
    frac = t / total_dur if total_dur > 0 else 0
    pw = int(frac * bar_w)
    if pw > 2:
        draw.rounded_rectangle(
            (bar_x, prog_y, bar_x + pw, prog_y + 5),
            radius=2, fill=PROGRESS_FG
        )
    # Playhead dot
    draw.ellipse(
        (bar_x + pw - 5, prog_y - 4, bar_x + pw + 5, prog_y + 9),
        fill=PROGRESS_FG
    )

    el = f"{int(t // 60):02d}:{int(t % 60):02d}"
    tot = f"{int(total_dur // 60):02d}:{int(total_dur % 60):02d}"
    text_centered(draw, prog_y + 12, f"{el} / {tot}", fonts["time"], TEXT_GRAY)

    return img


# ── Main ────────────────────────────────────────────────────────────────
def main():
    print("Loading fonts...")
    fonts = load_fonts()

    print("Loading audio...")
    rate, left, right = load_audio()
    total_dur = len(left) / rate
    total_frames = int(total_dur * FPS)
    print(f"  {total_dur:.1f}s  →  {total_frames} frames @ {FPS}fps")

    print("Loading segments...")
    segments = load_segments()
    print(f"  {len(segments)} segments")

    print("Parsing subtitles...")
    subs = parse_subtitles(TRANS_PATH)
    print(f"  {len(subs)} subtitle entries")

    print("Pre-computing stereo levels...")
    l_levels, r_levels, balance = precompute_levels(rate, left, right, FPS)
    print("  done")

    print(f"\nRendering → {OUTPUT_PATH.name}")
    print(f"  {WIDTH}x{HEIGHT} @ {FPS}fps, ~{total_dur:.0f}s\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}", "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-i", str(AUDIO_PATH),
        "-c:v", "libx264", "-preset", "medium", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-pix_fmt", "yuv420p",
        str(OUTPUT_PATH),
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    prev_seg_num = None

    try:
        for fn in range(total_frames):
            t = fn / FPS
            seg = seg_at(segments, t)
            sub = sub_at(subs, t)
            ll = l_levels[fn] if fn < len(l_levels) else 0
            rl = r_levels[fn] if fn < len(r_levels) else 0
            bl = balance[fn] if fn < len(balance) else 0

            img = render_frame(
                t, total_dur, seg, sub, ll, rl, bl,
                left, right, rate, fonts, prev_seg_num
            )
            proc.stdin.write(img.tobytes())

            prev_seg_num = seg["segment_number"] if seg else prev_seg_num

            if fn % (FPS * 10) == 0:
                pct = fn / total_frames * 100
                el = f"{int(t // 60):02d}:{int(t % 60):02d}"
                print(f"  {pct:5.1f}%  {el}/{int(total_dur // 60):02d}:{int(total_dur % 60):02d}")

    except BrokenPipeError:
        pass
    finally:
        proc.stdin.close()
        stderr = proc.stderr.read()
        proc.wait()

    if proc.returncode == 0:
        mb = OUTPUT_PATH.stat().st_size / (1024 * 1024)
        print(f"\nDone!  {OUTPUT_PATH}  ({mb:.1f} MB)")
    else:
        print(f"\nFFmpeg error (code {proc.returncode}):")
        print(stderr.decode()[-800:])
        sys.exit(1)


if __name__ == "__main__":
    main()
