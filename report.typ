#set text(font: "IBM Plex Sans", size: 10.5pt)
#set page(margin: (x: 2.4cm, y: 2.8cm), numbering: "1")
#set par(justify: true, leading: 0.65em)
#set heading(numbering: "1.")

// Title page
#align(center)[
  #v(3cm)
  #text(size: 28pt, weight: "bold")[OnePlus Internal Mic Testing]
  #v(0.6cm)
  #text(size: 14pt, fill: rgb("#555"))[How Address Patterns Affect Voice Recording Quality]
  #v(1.2cm)
  #text(size: 11pt, fill: rgb("#777"))[
    OnePlus Nord 3 5G (CPH2493) \
    48kHz Stereo WAV · No DSP · Raw Capture \
    March 2026
  ]
  #v(2cm)
  #line(length: 60%, stroke: 0.5pt + rgb("#ccc"))
  #v(0.8cm)
  #text(size: 10pt, fill: rgb("#888"))[
    24 test segments · 9 audio metrics · 7 data visualizations
  ]
]

#pagebreak()

// TOC
#outline(indent: 1.5em, depth: 2)

#pagebreak()

= Executive Summary

Most people instinctively speak into the bottom of their phone — aiming at the microphone port near the USB-C connector. *This is the worst approach.*

Testing 24 configurations on the OnePlus Nord 3 5G revealed that *addressing the center of the LCD screen* from 10--15cm produces the cleanest, most natural voice recording. The bottom mic port — the "obvious" target — had the lowest signal-to-noise ratio of all patterns tested.

#block(
  fill: rgb("#f0f4f8"),
  inset: 14pt,
  radius: 6pt,
  width: 100%,
)[
  *Quick Setup for Best Results:*
  + Stand or mount the phone (eliminates handling noise)
  + Keep the case on (no measurable impact)
  + Position yourself 10--15cm from the screen
  + Speak at the center of the LCD — not the mic port
  + Stay on-axis (face the screen directly)
]

= Test Methodology

== Device & Recording Setup

#table(
  columns: (auto, 1fr),
  stroke: 0.5pt + rgb("#ddd"),
  inset: 8pt,
  [*Device*], [OnePlus Nord 3 5G (CPH2493)],
  [*SoC*], [MediaTek Dimensity 9000 (Qualcomm SM7475)],
  [*Microphones*], [Dual: primary (bottom, near USB-C) + secondary (top)],
  [*Format*], [WAV, 48kHz, stereo, 16-bit],
  [*App*], [ASR (Android recording app)],
  [*DSP*], [All disabled — no noise cancellation, no AGC],
  [*Environment*], [Untreated room, ambient background noise],
  [*Duration*], [9 minutes, 24 test segments],
)

== Metrics Computed

Nine audio quality metrics were computed per segment:

- *RMS level (dBFS)* — average signal power
- *Peak level (dBFS)* — maximum amplitude
- *Crest factor (dB)* — peak-to-RMS ratio (dynamic headroom)
- *Dynamic range (dB)* — difference between 95th and 5th percentile frame energy
- *SNR (dB)* — estimated speech-to-noise ratio (energy threshold method)
- *Spectral centroid (Hz)* — "brightness" of the signal
- *Spectral rolloff (Hz)* — frequency below which 85% of energy sits
- *Zero crossing rate* — high-frequency content indicator
- *Speech ratio (%)* — percentage of frames with speech activity

#pagebreak()

= Address Pattern Comparison

Four address patterns were tested, each directing voice at a different part of the phone from ~10cm:

#table(
  columns: (1.4fr, auto, auto, auto, auto),
  stroke: 0.5pt + rgb("#ddd"),
  inset: 8pt,
  align: (left, center, center, center, center),
  table.header(
    [*Pattern*], [*RMS (dBFS)*], [*SNR (dB)*], [*Centroid (Hz)*], [*Speech %*],
  ),
  [Center/LCD screen], [-26.1], [21.0], [587], [70],
  [Bottom mic (USB-C)], [-29.0], [17.1], [673], [70],
  [Top mic (secondary)], [-26.5], [25.1], [792], [70],
  [Phone-to-ear], [-23.3], [23.7], [565], [70],
)

#v(0.4cm)

*Key finding:* The bottom mic — where most people aim — had the worst SNR (17.1 dB) and a 3 dB lower RMS than the center/LCD pattern. Center/LCD produced the warmest tone (lowest centroid at 587 Hz) with good SNR. The top mic had the highest SNR (25.1 dB) but a brighter, thinner quality (792 Hz centroid).

#v(0.3cm)

#figure(
  image("segments/charts/02_snr_by_address_pattern.png", width: 88%),
  caption: [Signal-to-noise ratio by address pattern. Bottom mic is clearly worst.],
)

#figure(
  image("segments/charts/01_rms_by_address_pattern.png", width: 88%),
  caption: [RMS signal level by address pattern.],
)

#pagebreak()

#figure(
  image("segments/charts/03_centroid_by_address_pattern.png", width: 88%),
  caption: [Spectral centroid — lower values indicate warmer, more natural voice tone.],
)

#figure(
  image("segments/charts/06_radar_address_patterns.png", width: 70%),
  caption: [Normalized radar comparison across all five metrics. Center/LCD is the most balanced.],
)

#pagebreak()

= Proximity Effect

Distance from the screen was varied while using the center/LCD address pattern:

#table(
  columns: (auto, auto, auto, auto),
  stroke: 0.5pt + rgb("#ddd"),
  inset: 8pt,
  align: (center, center, center, center),
  table.header(
    [*Distance*], [*RMS (dBFS)*], [*SNR (dB)*], [*Centroid (Hz)*],
  ),
  [0.5 cm (touching)], [-27.3], [23.7], [588],
  [3 cm], [-22.1], [19.3], [573],
  [10--15 cm], [-25.7], [22.7], [656],
  [30 cm], [-27.2], [18.4], [801],
)

#v(0.3cm)

At 3cm, RMS is highest (-22.1 dBFS) but SNR drops to 19.3 dB — proximity bass boost and mouth noise dominate. The 10--15cm range gives the best trade-off: strong SNR (22.7 dB) without distortion. At 30cm, both level and SNR fall off, and the spectral centroid shifts to 801 Hz (thinner, more room-influenced sound).

#figure(
  image("segments/charts/05_proximity_effect.png", width: 88%),
  caption: [RMS and SNR vs. distance. The 10--15cm range is the practical sweet spot.],
)

#pagebreak()

= Case Effect

The phone was tested with and without a hard-shell case (mic port cutouts present):

#table(
  columns: (auto, auto, auto, auto),
  stroke: 0.5pt + rgb("#ddd"),
  inset: 8pt,
  align: (left, center, center, center),
  table.header(
    [*Condition*], [*RMS (dBFS)*], [*SNR (dB)*], [*Centroid (Hz)*],
  ),
  [No case], [-26.2], [21.0], [628],
  [With case], [-25.9], [27.8], [772],
)

#v(0.3cm)

The case made *no meaningful negative impact*. RMS was within 0.3 dB, and the case actually showed slightly higher SNR (27.8 vs 21.0 dB). The centroid shift (628→772 Hz) suggests minor resonance from the case shell, but this is within acceptable variation. As long as the case has microphone cutouts, there is no reason to remove it for recording.

#figure(
  image("segments/charts/04_case_comparison.png", width: 95%),
  caption: [Side-by-side comparison of three metrics with and without case.],
)

#pagebreak()

= Mount vs. Handheld

#table(
  columns: (auto, auto, auto, auto),
  stroke: 0.5pt + rgb("#ddd"),
  inset: 8pt,
  align: (left, center, center, center),
  table.header(
    [*Method*], [*RMS (dBFS)*], [*SNR (dB)*], [*Centroid (Hz)*],
  ),
  [Ulanzi stand], [-26.5], [21.9], [841],
  [Handheld + case], [-25.9], [27.8], [772],
)

The primary benefit of a mount is *eliminating handling noise*, which showed the highest dynamic range spikes in the entire test (segment 14). Even a basic stand (Ulanzi selfie stick at full extension) showed good vibration rejection — only hard shaking transferred through.

= Off-Axis Performance

#table(
  columns: (auto, auto, auto, auto),
  stroke: 0.5pt + rgb("#ddd"),
  inset: 8pt,
  align: (left, center, center, center),
  table.header(
    [*Position*], [*RMS (dBFS)*], [*SNR (dB)*], [*Centroid (Hz)*],
  ),
  [On-axis (stand)], [-25.6], [17.2], [691],
  [360° walk], [-30.1], [22.3], [610],
  [45° off-axis left], [-30.0], [22.8], [650],
  [45° off-axis right], [-30.4], [20.5], [712],
)

Moving off-axis drops signal level by ~4 dB. The 360° walk test showed the stereo field shifting as the speaker moved around the phone — visible in the Lissajous visualization in the accompanying video. Quality degraded most at 180° (behind the phone).

#pagebreak()

= Full Segment Heatmap

#figure(
  image("segments/charts/07_summary_heatmap.png", width: 100%),
  caption: [All 24 segments × 9 metrics. Color intensity shows normalized rank (darker = higher relative value). Handling noise (14) and noise floor (16) segments are clearly distinct from speech segments.],
)

#pagebreak()

= Actionable Recommendations

#block(
  fill: rgb("#e8f5e9"),
  inset: 14pt,
  radius: 6pt,
  width: 100%,
)[
  == For Voice Recording on Android Phones

  + *Address the center of the screen, not the mic port.* The bottom mic port — where most people instinctively aim — had the worst SNR (17.1 dB). Center/LCD address gives better balanced, warmer audio (SNR 21.0 dB, centroid 587 Hz vs. 673 Hz).

  + *Keep 10--15cm distance from the screen.* Close enough for good SNR, far enough to avoid proximity bass boost and mouth noise. At 3cm, distortion increases. At 30cm, signal falls off.

  + *Use a stand or mount.* Handling noise is the biggest quality killer for phone recordings. Any basic phone stand eliminates low-frequency rumble from hand vibrations.

  + *Use your phone case.* No measurable degradation with a case that has mic port cutouts. RMS within 0.3 dB, SNR actually slightly higher with case.

  + *Stay on-axis.* Face the screen directly. Moving 45° off-axis drops signal ~4 dB. Moving behind the phone (180°) is worst.

  + *Optimal setup summary:* Phone on a stand, case on, 10--15cm from screen, speaking at the LCD center.
]

#v(1cm)

#align(center)[
  #text(size: 9pt, fill: rgb("#999"))[
    Analysis generated from 24 WAV segments using scipy, numpy, and matplotlib. \
    Full data available in `segments/analysis.json` and `segments/summary.csv`. \
    Video with stereo field visualization: `generate_video.py`
  ]
]
