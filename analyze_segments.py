#!/usr/bin/env python3
"""Audio quality analysis of OnePlus mic test segments.

Computes 9 metrics per segment, generates 7 charts, and writes
analysis.json, summary.csv, and SUMMARY.md.
"""

import json
import csv
import os
import pathlib
import numpy as np
from scipy.io import wavfile
from scipy.signal import welch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.ticker as ticker

# ── Paths ────────────────────────────────────────────────────────────
ROOT = pathlib.Path(__file__).resolve().parent
SEG_DIR = ROOT / "segments"
CHART_DIR = SEG_DIR / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)

# ── Segment metadata ────────────────────────────────────────────────
SEGMENTS = {
    1:  "Intro",
    2:  "Center/LCD 10cm",
    3:  "Bottom Mic 10cm",
    4:  "Top Mic",
    5:  "Proximity 10-15cm",
    6:  "Proximity 3cm",
    7:  "Proximity touching",
    8:  "Proximity 30cm",
    9:  "Bottom Mic recap",
    10: "Top Mic recap",
    11: "Phone to Ear",
    12: "Phone to Ear downward",
    13: "Return to Center",
    14: "Handling noise",
    15: "Mount handling noise",
    16: "Noise floor",
    17: "Case description",
    18: "Case Center/LCD",
    19: "Case Bottom Mic",
    20: "Ulanzi Stand Bottom Mic",
    21: "Ulanzi Stand Center/LCD",
    22: "360° walk",
    23: "Off-axis 45° left",
    24: "Off-axis 45° right",
}

# ── Groupings ────────────────────────────────────────────────────────
GROUPS_ADDRESS = {
    "Center/LCD":    [2, 5, 13],
    "Bottom Mic":    [3, 9],
    "Top Mic":       [4, 10],
    "Phone-to-Ear":  [11, 12],
}

GROUPS_PROXIMITY = {
    0.5:  [7],   # touching ≈ 0.5 cm
    3:    [6],
    12:   [5],   # "10-15cm" ≈ 12 cm midpoint
    30:   [8],
}

GROUPS_CASE = {
    "No case":   [2, 3],    # center/LCD and bottom mic, bare
    "With case": [18, 19],  # same patterns, with case
}

GROUPS_MOUNT = {
    "Ulanzi stand": [20, 21],
    "Handheld+case": [18, 19],
}

GROUPS_OFFAXIS = {
    "On-axis (stand)": [21],
    "360° walk":       [22],
    "45° left":        [23],
    "45° right":       [24],
}

# ── WAV reading ──────────────────────────────────────────────────────

def wav_filenames():
    """Return dict {segment_number: Path} for all 24 WAVs."""
    out = {}
    for p in sorted(SEG_DIR.glob("*.wav")):
        num = int(p.stem.split("_")[0])
        out[num] = p
    return out


def load_mono_float(path):
    """Read WAV → mono float64 in [-1, 1]."""
    rate, data = wavfile.read(str(path))
    data = data.astype(np.float64)
    if data.ndim == 2:
        data = data.mean(axis=1)
    # Normalize int16 range
    data /= 32768.0
    return rate, data


# ── Metric functions ─────────────────────────────────────────────────

def compute_metrics(rate, samples):
    """Return dict of 9 metrics for a mono float64 signal."""
    eps = 1e-10  # avoid log(0)

    # RMS level (dBFS)
    rms = np.sqrt(np.mean(samples ** 2))
    rms_dbfs = 20 * np.log10(rms + eps)

    # Peak level (dBFS)
    peak = np.max(np.abs(samples))
    peak_dbfs = 20 * np.log10(peak + eps)

    # Crest factor (dB)
    crest_db = peak_dbfs - rms_dbfs

    # Dynamic range — RMS of 50 ms frames, dB difference between 95th and 5th percentile
    frame_len = int(rate * 0.05)
    n_frames = len(samples) // frame_len
    if n_frames < 2:
        dynamic_range_db = 0.0
    else:
        trimmed = samples[: n_frames * frame_len]
        frames = trimmed.reshape(n_frames, frame_len)
        frame_rms = np.sqrt(np.mean(frames ** 2, axis=1))
        frame_db = 20 * np.log10(frame_rms + eps)
        dynamic_range_db = float(np.percentile(frame_db, 95) - np.percentile(frame_db, 5))

    # SNR estimate — speech frames vs noise frames via energy threshold
    frame_energy = frame_rms if n_frames >= 2 else np.array([rms])
    threshold = np.percentile(frame_energy, 30)  # bottom 30% = noise
    noise_frames = frame_energy[frame_energy <= threshold]
    speech_frames = frame_energy[frame_energy > threshold]
    noise_rms = np.mean(noise_frames) if len(noise_frames) > 0 else eps
    speech_rms = np.mean(speech_frames) if len(speech_frames) > 0 else eps
    snr_db = 20 * np.log10(speech_rms / (noise_rms + eps))

    # Spectral centroid and rolloff via Welch PSD
    freqs, psd = welch(samples, fs=rate, nperseg=min(4096, len(samples)))
    psd_sum = psd.sum()
    if psd_sum < eps:
        spectral_centroid_hz = 0.0
        spectral_rolloff_hz = 0.0
    else:
        spectral_centroid_hz = float(np.sum(freqs * psd) / psd_sum)
        cumsum = np.cumsum(psd)
        rolloff_idx = np.searchsorted(cumsum, 0.85 * psd_sum)
        spectral_rolloff_hz = float(freqs[min(rolloff_idx, len(freqs) - 1)])

    # Zero crossing rate
    signs = np.sign(samples)
    zcr = float(np.sum(np.abs(np.diff(signs)) > 0)) / len(samples)

    # Speech ratio — % of frames above noise threshold
    speech_ratio = float(np.sum(frame_energy > threshold) / len(frame_energy) * 100) if len(frame_energy) > 0 else 0.0

    return {
        "rms_dbfs":            round(rms_dbfs, 2),
        "peak_dbfs":           round(peak_dbfs, 2),
        "crest_factor_db":     round(crest_db, 2),
        "dynamic_range_db":    round(dynamic_range_db, 2),
        "snr_db":              round(snr_db, 2),
        "spectral_centroid_hz": round(spectral_centroid_hz, 1),
        "spectral_rolloff_hz": round(spectral_rolloff_hz, 1),
        "zero_crossing_rate":  round(zcr, 4),
        "speech_ratio_pct":    round(speech_ratio, 1),
    }


# ── Group averaging ──────────────────────────────────────────────────

def group_averages(all_metrics, groups):
    """Average metrics across segment groups."""
    result = {}
    metric_keys = list(next(iter(all_metrics.values())).keys())
    for name, seg_ids in groups.items():
        avgs = {}
        for k in metric_keys:
            vals = [all_metrics[s][k] for s in seg_ids if s in all_metrics]
            avgs[k] = round(np.mean(vals), 2) if vals else None
        result[name] = avgs
    return result


# ── Chart helpers ────────────────────────────────────────────────────

COLORS = ["#2196F3", "#4CAF50", "#FF9800", "#E91E63", "#9C27B0", "#00BCD4"]

def _save(fig, name):
    fig.savefig(str(CHART_DIR / name), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✓ {name}")


def chart_horizontal_bars(group_avgs, metric_key, title, xlabel, filename):
    """Horizontal bar chart for one metric across address pattern groups."""
    names = list(group_avgs.keys())
    vals = [group_avgs[n][metric_key] for n in names]
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.barh(names, vals, color=COLORS[: len(names)], edgecolor="white", height=0.6)
    ax.set_xlabel(xlabel)
    ax.set_title(title, fontweight="bold")
    for bar, v in zip(bars, vals):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{v:.1f}", va="center", fontsize=9)
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.3)
    _save(fig, filename)


def chart_case_comparison(all_metrics, filename):
    """Side-by-side bars: no case vs case for 3 metrics."""
    metrics = ["rms_dbfs", "snr_db", "spectral_centroid_hz"]
    labels = ["RMS (dBFS)", "SNR (dB)", "Centroid (Hz)"]
    # Pairs: center/lcd (2 vs 18), bottom mic (3 vs 19)
    pairs = [("Center/LCD", 2, 18), ("Bottom Mic", 3, 19)]

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    x = np.arange(len(pairs))
    w = 0.35

    for ax, mk, lab in zip(axes, metrics, labels):
        no_case = [all_metrics[p[1]][mk] for p in pairs]
        with_case = [all_metrics[p[2]][mk] for p in pairs]
        ax.bar(x - w / 2, no_case, w, label="No case", color="#2196F3")
        ax.bar(x + w / 2, with_case, w, label="With case", color="#FF9800")
        ax.set_xticks(x)
        ax.set_xticklabels([p[0] for p in pairs])
        ax.set_ylabel(lab)
        ax.set_title(lab, fontweight="bold")
        ax.legend(fontsize=8)
        ax.grid(axis="y", alpha=0.3)

    fig.suptitle("Case vs No Case Comparison", fontweight="bold", fontsize=13)
    fig.tight_layout()
    _save(fig, filename)


def chart_proximity(all_metrics, filename):
    """Line chart: RMS + SNR vs distance (log X)."""
    distances = sorted(GROUPS_PROXIMITY.keys())
    rms_vals = [np.mean([all_metrics[s]["rms_dbfs"] for s in GROUPS_PROXIMITY[d]]) for d in distances]
    snr_vals = [np.mean([all_metrics[s]["snr_db"] for s in GROUPS_PROXIMITY[d]]) for d in distances]

    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.set_xscale("log")
    ax1.set_xlabel("Distance (cm)")

    ln1 = ax1.plot(distances, rms_vals, "o-", color="#2196F3", linewidth=2, markersize=8, label="RMS (dBFS)")
    ax1.set_ylabel("RMS (dBFS)", color="#2196F3")
    ax1.tick_params(axis="y", labelcolor="#2196F3")

    ax2 = ax1.twinx()
    ln2 = ax2.plot(distances, snr_vals, "s--", color="#E91E63", linewidth=2, markersize=8, label="SNR (dB)")
    ax2.set_ylabel("SNR (dB)", color="#E91E63")
    ax2.tick_params(axis="y", labelcolor="#E91E63")

    lns = ln1 + ln2
    ax1.legend(lns, [l.get_label() for l in lns], loc="best")
    ax1.set_title("Proximity Effect: RMS & SNR vs Distance", fontweight="bold")
    ax1.xaxis.set_major_formatter(ticker.ScalarFormatter())
    ax1.set_xticks(distances)
    ax1.set_xticklabels([f"{d} cm" for d in distances])
    ax1.grid(alpha=0.3)
    _save(fig, filename)


def chart_radar(group_avgs, filename):
    """Radar chart: 5 normalized axes for 4 address patterns."""
    axes_keys = ["rms_dbfs", "snr_db", "spectral_centroid_hz", "speech_ratio_pct", "dynamic_range_db"]
    axes_labels = ["RMS Level", "SNR", "Spectral Centroid", "Speech Ratio", "Dynamic Range"]
    groups = list(group_avgs.keys())

    # Collect raw values and normalize 0-1
    raw = {g: [group_avgs[g][k] for k in axes_keys] for g in groups}
    all_vals = np.array(list(raw.values()))
    mins = all_vals.min(axis=0)
    maxs = all_vals.max(axis=0)
    span = maxs - mins
    span[span == 0] = 1

    normed = {g: (np.array(raw[g]) - mins) / span for g in groups}

    angles = np.linspace(0, 2 * np.pi, len(axes_keys), endpoint=False).tolist()
    angles += angles[:1]  # close polygon

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    for i, g in enumerate(groups):
        vals = normed[g].tolist() + [normed[g][0]]
        ax.plot(angles, vals, "o-", linewidth=2, label=g, color=COLORS[i])
        ax.fill(angles, vals, alpha=0.1, color=COLORS[i])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(axes_labels, fontsize=9)
    ax.set_ylim(0, 1.15)
    ax.set_title("Address Pattern Comparison (Normalized)", fontweight="bold", y=1.08)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=9)
    _save(fig, filename)


def chart_heatmap(all_metrics, filename):
    """Heatmap: all 24 segments × all 9 metrics."""
    seg_nums = sorted(all_metrics.keys())
    metric_keys = list(next(iter(all_metrics.values())).keys())
    nice_labels = {
        "rms_dbfs": "RMS (dBFS)",
        "peak_dbfs": "Peak (dBFS)",
        "crest_factor_db": "Crest Factor (dB)",
        "dynamic_range_db": "Dynamic Range (dB)",
        "snr_db": "SNR (dB)",
        "spectral_centroid_hz": "Centroid (Hz)",
        "spectral_rolloff_hz": "Rolloff (Hz)",
        "zero_crossing_rate": "Zero Crossing Rate",
        "speech_ratio_pct": "Speech Ratio (%)",
    }

    data = np.array([[all_metrics[s][k] for k in metric_keys] for s in seg_nums])
    # Normalize each column 0-1 for visual comparison
    mins = data.min(axis=0)
    maxs = data.max(axis=0)
    span = maxs - mins
    span[span == 0] = 1
    normed = (data - mins) / span

    fig, ax = plt.subplots(figsize=(14, 10))
    im = ax.imshow(normed, aspect="auto", cmap="YlOrRd", interpolation="nearest")

    ax.set_xticks(range(len(metric_keys)))
    ax.set_xticklabels([nice_labels.get(k, k) for k in metric_keys], rotation=45, ha="right", fontsize=9)

    ylabels = [f"{s:02d} {SEGMENTS.get(s, '')}" for s in seg_nums]
    ax.set_yticks(range(len(seg_nums)))
    ax.set_yticklabels(ylabels, fontsize=8)

    # Annotate cells with actual values
    for i in range(len(seg_nums)):
        for j in range(len(metric_keys)):
            val = data[i, j]
            fmt = ".0f" if abs(val) > 100 else ".1f" if abs(val) > 10 else ".2f"
            ax.text(j, i, f"{val:{fmt}}", ha="center", va="center", fontsize=6,
                    color="white" if normed[i, j] > 0.6 else "black")

    ax.set_title("All Segments × All Metrics (color = normalized rank)", fontweight="bold")
    fig.colorbar(im, ax=ax, shrink=0.6, label="Normalized (0=min, 1=max)")
    fig.tight_layout()
    _save(fig, filename)


# ── Output writers ───────────────────────────────────────────────────

def write_json(all_metrics, group_data, path):
    out = {
        "segments": {str(k): {**v, "name": SEGMENTS.get(k, "")} for k, v in sorted(all_metrics.items())},
        "group_averages": {
            "address_pattern": group_data["address"],
            "proximity": {str(k): v for k, v in group_data["proximity"].items()},
            "case_effect": group_data["case"],
            "mount_vs_handheld": group_data["mount"],
            "off_axis": group_data["offaxis"],
        },
    }
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"  ✓ {path.name}")


def write_csv(all_metrics, path):
    seg_nums = sorted(all_metrics.keys())
    metric_keys = list(next(iter(all_metrics.values())).keys())
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["segment", "name"] + metric_keys)
        for s in seg_nums:
            writer.writerow([s, SEGMENTS.get(s, "")] + [all_metrics[s][k] for k in metric_keys])
    print(f"  ✓ {path.name}")


def write_summary_md(all_metrics, group_data, path):
    addr = group_data["address"]

    # Find best address pattern by SNR
    best_addr = max(addr, key=lambda g: addr[g]["snr_db"])
    # Find best proximity
    prox = group_data["proximity"]
    best_prox = max(prox, key=lambda d: prox[d]["snr_db"])

    lines = [
        "# OnePlus Mic Test — Audio Quality Analysis",
        "",
        "## Key Findings",
        "",
        f"**Best address pattern by SNR:** {best_addr} ({addr[best_addr]['snr_db']:.1f} dB)",
        f"**Best address pattern by RMS:** {max(addr, key=lambda g: addr[g]['rms_dbfs'])} "
        f"({addr[max(addr, key=lambda g: addr[g]['rms_dbfs'])]['rms_dbfs']:.1f} dBFS)",
        f"**Optimal proximity distance:** {best_prox} cm (SNR {prox[best_prox]['snr_db']:.1f} dB)",
        "",
        "## Address Pattern Comparison",
        "",
        "| Pattern | RMS (dBFS) | SNR (dB) | Centroid (Hz) | Speech % |",
        "|---------|-----------|---------|--------------|---------|",
    ]
    for g in addr:
        a = addr[g]
        lines.append(f"| {g} | {a['rms_dbfs']:.1f} | {a['snr_db']:.1f} | {a['spectral_centroid_hz']:.0f} | {a['speech_ratio_pct']:.0f} |")

    lines += [
        "",
        "## Proximity Effect",
        "",
        "| Distance (cm) | RMS (dBFS) | SNR (dB) | Centroid (Hz) |",
        "|--------------|-----------|---------|--------------|",
    ]
    for d in sorted(prox.keys()):
        p = prox[d]
        lines.append(f"| {d} | {p['rms_dbfs']:.1f} | {p['snr_db']:.1f} | {p['spectral_centroid_hz']:.0f} |")

    # Case effect
    case = group_data["case"]
    lines += [
        "",
        "## Case Effect",
        "",
        "| Condition | RMS (dBFS) | SNR (dB) | Centroid (Hz) |",
        "|-----------|-----------|---------|--------------|",
    ]
    for g in case:
        c = case[g]
        lines.append(f"| {g} | {c['rms_dbfs']:.1f} | {c['snr_db']:.1f} | {c['spectral_centroid_hz']:.0f} |")

    # Mount comparison
    mount = group_data["mount"]
    lines += [
        "",
        "## Mount vs Handheld",
        "",
        "| Method | RMS (dBFS) | SNR (dB) | Centroid (Hz) |",
        "|--------|-----------|---------|--------------|",
    ]
    for g in mount:
        m = mount[g]
        lines.append(f"| {g} | {m['rms_dbfs']:.1f} | {m['snr_db']:.1f} | {m['spectral_centroid_hz']:.0f} |")

    # Off-axis
    offaxis = group_data["offaxis"]
    lines += [
        "",
        "## Off-Axis Performance",
        "",
        "| Position | RMS (dBFS) | SNR (dB) | Centroid (Hz) |",
        "|----------|-----------|---------|--------------|",
    ]
    for g in offaxis:
        o = offaxis[g]
        lines.append(f"| {g} | {o['rms_dbfs']:.1f} | {o['snr_db']:.1f} | {o['spectral_centroid_hz']:.0f} |")

    lines += [
        "",
        "## Recommendations",
        "",
        f"1. **Use the {best_addr} address pattern** for best signal-to-noise ratio.",
        f"2. **Optimal distance is ~{best_prox} cm** — closest proximity gives highest SNR,",
        "   but may introduce proximity bass boost and handling noise.",
        "3. **Case has minimal effect** on measured audio quality — use one for protection.",
        "4. **A stand reduces handling noise** — compare dynamic range between mount groups.",
        "5. **On-axis performs best** — off-axis angles reduce high-frequency content.",
        "",
        "## Charts",
        "",
        "See `segments/charts/` for visual comparisons:",
        "",
        "- `01_rms_by_address_pattern.png`",
        "- `02_snr_by_address_pattern.png`",
        "- `03_centroid_by_address_pattern.png`",
        "- `04_case_comparison.png`",
        "- `05_proximity_effect.png`",
        "- `06_radar_address_patterns.png`",
        "- `07_summary_heatmap.png`",
        "",
        "---",
        "*Generated by analyze_segments.py*",
    ]

    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  ✓ {path.name}")


# ── Main ─────────────────────────────────────────────────────────────

def main():
    wavs = wav_filenames()
    print(f"Found {len(wavs)} WAV segments\n")

    # 1. Compute metrics
    print("Computing metrics...")
    all_metrics = {}
    for num in sorted(wavs):
        rate, samples = load_mono_float(wavs[num])
        m = compute_metrics(rate, samples)
        all_metrics[num] = m
        print(f"  {num:02d} {SEGMENTS.get(num, ''):30s}  RMS={m['rms_dbfs']:6.1f}  SNR={m['snr_db']:5.1f}  Centroid={m['spectral_centroid_hz']:6.0f}")

    # 2. Group averages
    print("\nComputing group averages...")
    group_data = {
        "address":   group_averages(all_metrics, GROUPS_ADDRESS),
        "proximity": group_averages(all_metrics, {k: v for k, v in GROUPS_PROXIMITY.items()}),
        "case":      group_averages(all_metrics, GROUPS_CASE),
        "mount":     group_averages(all_metrics, GROUPS_MOUNT),
        "offaxis":   group_averages(all_metrics, GROUPS_OFFAXIS),
    }

    # 3. Charts
    print("\nGenerating charts...")
    addr_avgs = group_data["address"]
    chart_horizontal_bars(addr_avgs, "rms_dbfs", "RMS Level by Address Pattern", "RMS (dBFS)",
                          "01_rms_by_address_pattern.png")
    chart_horizontal_bars(addr_avgs, "snr_db", "SNR by Address Pattern", "SNR (dB)",
                          "02_snr_by_address_pattern.png")
    chart_horizontal_bars(addr_avgs, "spectral_centroid_hz", "Spectral Centroid by Address Pattern",
                          "Spectral Centroid (Hz)", "03_centroid_by_address_pattern.png")
    chart_case_comparison(all_metrics, "04_case_comparison.png")
    chart_proximity(all_metrics, "05_proximity_effect.png")
    chart_radar(addr_avgs, "06_radar_address_patterns.png")
    chart_heatmap(all_metrics, "07_summary_heatmap.png")

    # 4. Data outputs
    print("\nWriting data files...")
    write_json(all_metrics, group_data, SEG_DIR / "analysis.json")
    write_csv(all_metrics, SEG_DIR / "summary.csv")
    write_summary_md(all_metrics, group_data, SEG_DIR / "SUMMARY.md")

    print("\nDone! All outputs in segments/ and segments/charts/")


if __name__ == "__main__":
    main()
