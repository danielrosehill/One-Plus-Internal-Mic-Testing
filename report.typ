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

== How to Read the Metrics

This report uses several audio measurements to compare recording quality. Here is what each one means and how to interpret it:

#block(
  fill: rgb("#fafafa"),
  inset: 12pt,
  radius: 6pt,
  width: 100%,
)[
  #text(size: 10pt)[
    *RMS Level (dBFS)* — _Closer to 0 is louder_ \
    How loud the recording is on average. Measured in decibels relative to full scale (dBFS). A value of -26 means the average signal is 26 dB below the maximum the microphone can capture. Values closer to 0 mean a louder, stronger signal. Typical speech recordings fall between -30 and -15 dBFS.

    #v(6pt)

    *SNR — Signal-to-Noise Ratio (dB)* — #text(fill: rgb("#2e7d32"))[▲ Higher is better] \
    The most important metric for voice clarity. SNR measures how much louder your voice is compared to the background noise. An SNR of 20 dB means your voice is 100× more powerful than the noise. Higher values mean cleaner, more intelligible speech. Below 15 dB, recordings start to sound noisy. Above 20 dB is good; above 25 dB is excellent.

    #v(6pt)

    *Spectral Centroid (Hz)* — _Context-dependent_ \
    The "center of gravity" of the sound's frequency content — think of it as a brightness dial. Lower values (500--600 Hz) sound warmer and fuller, like a natural speaking voice. Higher values (700--800+ Hz) sound thinner or more nasal. For voice recording, values in the 500--700 Hz range are generally most natural. Very high values can indicate the recording is picking up more room echo than direct voice.

    #v(6pt)

    *Peak Level (dBFS)* — _Should stay below 0_ \
    The loudest single moment in the recording. If this hits 0 dBFS, the recording has clipped (distorted). A healthy peak is between -10 and -3 dBFS — loud enough to be clear but with headroom to spare.

    #v(6pt)

    *Crest Factor (dB)* — _Moderate values are typical_ \
    The difference between the loudest moment (peak) and the average level (RMS). For speech, 10--20 dB is normal. Very low values suggest the audio is compressed or distorted. Very high values suggest occasional loud spikes (like handling noise) against a quiet background.

    #v(6pt)

    *Dynamic Range (dB)* — _Context-dependent_ \
    How much the volume varies throughout the recording. For consistent speech, a moderate dynamic range (5--15 dB) is normal. Very high dynamic range in a speech recording usually indicates a problem — such as handling noise creating loud spikes, or the speaker moving toward and away from the mic.

    #v(6pt)

    *Spectral Rolloff (Hz)* — _Context-dependent_ \
    The frequency below which 85% of the sound energy sits. For voice, this is typically 2,000--6,000 Hz. Lower values mean the recording has mostly low-frequency content. Higher values mean more high-frequency detail is being captured (which can be good for clarity or bad if it's noise).

    #v(6pt)

    *Zero Crossing Rate* — #text(fill: rgb("#2e7d32"))[▲ Higher = more high-frequency content] \
    How often the audio waveform crosses the zero line per sample. Higher values indicate more high-frequency energy in the signal. Useful for distinguishing speech (moderate ZCR) from noise (high ZCR) or silence (very low ZCR).

    #v(6pt)

    *Speech Ratio (%)* — #text(fill: rgb("#2e7d32"))[▲ Higher is better] \
    The percentage of the recording that contains detectable speech activity (as opposed to silence or background noise). A value of 70% means the speaker was actively talking for 70% of the segment. Higher values indicate more continuous speech content.
  ]
]

#pagebreak()

= Address Pattern Comparison

Four address patterns were tested, each directing voice at a different part of the phone from ~10cm:

#table(
  columns: (1.4fr, auto, auto, auto, auto),
  stroke: 0.5pt + rgb("#ddd"),
  inset: 8pt,
  align: (left, center, center, center, center),
  table.header(
    [*Pattern*],
    [*RMS Level* \ #text(size: 8pt, fill: rgb("#666"))[(closer to 0 \ = louder)]],
    [*SNR* \ #text(size: 8pt, fill: rgb("#2e7d32"))[(higher = \ cleaner)]],
    [*Centroid* \ #text(size: 8pt, fill: rgb("#666"))[(lower = \ warmer)]],
    [*Speech %* \ #text(size: 8pt, fill: rgb("#2e7d32"))[(higher = \ more voice)]],
  ),
  [Center/LCD screen], [-26.1 dBFS], [*21.0 dB*], [587 Hz], [70%],
  [Bottom mic (USB-C)], [-29.0 dBFS], [17.1 dB], [673 Hz], [70%],
  [Top mic (secondary)], [-26.5 dBFS], [*25.1 dB*], [792 Hz], [70%],
  [Phone-to-ear], [-23.3 dBFS], [*23.7 dB*], [565 Hz], [70%],
)

#v(0.3cm)

*What this means:*
- *Bottom mic is worst for voice clarity.* Despite being the microphone port, it captured the most noise relative to voice (SNR only 17.1 dB). Speaking at the screen center gives 4 dB better SNR — that means your voice is roughly 2.5× louder relative to the noise.
- *Center/LCD gives the most natural sound.* Its spectral centroid (587 Hz) is closest to what a natural speaking voice sounds like. The top mic's 792 Hz centroid makes recordings sound thinner.
- *Phone-to-ear is loudest* (-23.3 dBFS) because the mouth is very close to the mic, but this isn't a practical recording position.

#v(0.2cm)

#figure(
  image("segments/charts/02_snr_by_address_pattern.png", width: 88%),
  caption: [Signal-to-noise ratio by address pattern (longer bar = cleaner audio). Bottom mic is clearly worst.],
)

#figure(
  image("segments/charts/01_rms_by_address_pattern.png", width: 88%),
  caption: [Average signal volume by address pattern (longer bar = louder recording).],
)

#pagebreak()

#figure(
  image("segments/charts/03_centroid_by_address_pattern.png", width: 88%),
  caption: [Spectral centroid by address pattern. Lower values mean warmer, more natural voice tone. Center/LCD (587 Hz) sounds fullest; Top Mic (792 Hz) sounds thinnest.],
)

#figure(
  image("segments/charts/06_radar_address_patterns.png", width: 70%),
  caption: [Radar comparison — each axis is a different quality metric, normalized so the outermost ring is the best score. A shape that covers more area is better overall. Center/LCD (blue) is the most balanced.],
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
    [*Distance*],
    [*RMS Level* \ #text(size: 8pt, fill: rgb("#666"))[(closer to 0 = louder)]],
    [*SNR* \ #text(size: 8pt, fill: rgb("#2e7d32"))[(higher = cleaner)]],
    [*Centroid* \ #text(size: 8pt, fill: rgb("#666"))[(lower = warmer)]],
  ),
  [0.5 cm (touching)], [-27.3 dBFS], [*23.7 dB*], [588 Hz],
  [3 cm], [*-22.1 dBFS*], [19.3 dB], [573 Hz],
  [10--15 cm], [-25.7 dBFS], [*22.7 dB*], [656 Hz],
  [30 cm], [-27.2 dBFS], [18.4 dB], [801 Hz],
)

#v(0.3cm)

*What this means:*
- *3cm is the loudest* (-22.1 dBFS) but not the cleanest — mouth sounds, breathing, and bass boost from being too close reduce the SNR to 19.3 dB.
- *10--15cm is the sweet spot.* SNR is strong (22.7 dB) and the tone is natural. This is roughly a hand's length from the phone.
- *30cm is too far.* Both volume and clarity drop off noticeably, and the centroid rises to 801 Hz, meaning the recording picks up more room reflections than direct voice.
- *Touching distance* had high SNR (23.7 dB) but is impractical and risks clipping on louder syllables.

#figure(
  image("segments/charts/05_proximity_effect.png", width: 88%),
  caption: [Blue line = volume (RMS), pink line = clarity (SNR). The 10--15cm zone offers the best combination of both.],
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
    [*Condition*],
    [*RMS Level* \ #text(size: 8pt, fill: rgb("#666"))[(closer to 0 = louder)]],
    [*SNR* \ #text(size: 8pt, fill: rgb("#2e7d32"))[(higher = cleaner)]],
    [*Centroid* \ #text(size: 8pt, fill: rgb("#666"))[(lower = warmer)]],
  ),
  [No case], [-26.2 dBFS], [21.0 dB], [628 Hz],
  [With case], [-25.9 dBFS], [*27.8 dB*], [772 Hz],
)

#v(0.3cm)

*What this means:*
- *The case makes virtually no difference* to recording volume (only 0.3 dB, which is inaudible).
- The case actually measured _slightly better_ for SNR (27.8 vs 21.0 dB), possibly due to the case dampening some handling vibrations.
- The centroid shift (628→772 Hz) suggests the case introduces a subtle brightness, but this is minor and unlikely to be noticeable in practice.
- *Bottom line:* As long as your case has cutouts around the mic ports, keep it on. There is no reason to remove it for recording.

#figure(
  image("segments/charts/04_case_comparison.png", width: 95%),
  caption: [Three metrics compared with and without case. Blue = no case, orange = with case. Differences are minimal.],
)

#pagebreak()

= Mount vs. Handheld

#table(
  columns: (auto, auto, auto, auto),
  stroke: 0.5pt + rgb("#ddd"),
  inset: 8pt,
  align: (left, center, center, center),
  table.header(
    [*Method*],
    [*RMS Level* \ #text(size: 8pt, fill: rgb("#666"))[(closer to 0 = louder)]],
    [*SNR* \ #text(size: 8pt, fill: rgb("#2e7d32"))[(higher = cleaner)]],
    [*Centroid* \ #text(size: 8pt, fill: rgb("#666"))[(lower = warmer)]],
  ),
  [Ulanzi stand], [-26.5 dBFS], [21.9 dB], [841 Hz],
  [Handheld + case], [-25.9 dBFS], [*27.8 dB*], [772 Hz],
)

#v(0.3cm)

*What this means:*
- The numbers above don't tell the full story. The primary benefit of a mount is *eliminating handling noise* — the low-frequency rumble and thumps that occur when you hold, shift, or tap the phone.
- Handling noise (segment 14) showed the highest dynamic range spikes in the entire test — sudden loud bursts that overwhelm the speech signal.
- Even a basic stand (tested with a Ulanzi selfie stick at full extension) showed good vibration rejection. Only hard shaking transferred through.
- *If you're recording anything longer than a quick voice memo, use a stand.* Even a phone propped against a book is better than holding it.

= Off-Axis Performance

"Off-axis" means speaking at an angle to the phone rather than directly at the screen.

#table(
  columns: (auto, auto, auto, auto),
  stroke: 0.5pt + rgb("#ddd"),
  inset: 8pt,
  align: (left, center, center, center),
  table.header(
    [*Position*],
    [*RMS Level* \ #text(size: 8pt, fill: rgb("#666"))[(closer to 0 = louder)]],
    [*SNR* \ #text(size: 8pt, fill: rgb("#2e7d32"))[(higher = cleaner)]],
    [*Centroid* \ #text(size: 8pt, fill: rgb("#666"))[(lower = warmer)]],
  ),
  [On-axis (facing screen)], [*-25.6 dBFS*], [17.2 dB], [691 Hz],
  [360° walk around], [-30.1 dB], [22.3 dB], [610 Hz],
  [45° left of center], [-30.0 dBFS], [22.8 dB], [650 Hz],
  [45° right of center], [-30.4 dBFS], [20.5 dB], [712 Hz],
)

#v(0.3cm)

*What this means:*
- *On-axis is loudest* by a significant margin — about 4--5 dB louder than any off-axis position. That's roughly 2--3× the signal power.
- Moving even 45° off-axis causes a noticeable drop in volume.
- The 360° walk test showed the stereo image shifting as the speaker circled the phone — the left and right channels trade dominance depending on which side of the phone is closer.
- *Face the screen when recording.* Even small angles cost you signal.

#pagebreak()

= Full Segment Heatmap

The heatmap below shows all 24 test segments measured across all 9 metrics. Each cell is color-coded: *darker/redder = higher value relative to other segments* for that metric. This lets you spot patterns at a glance.

#block(
  fill: rgb("#fff8e1"),
  inset: 10pt,
  radius: 6pt,
  width: 100%,
)[
  #text(size: 9.5pt)[
    *How to read this chart:* Each row is a test segment. Each column is a metric. The color shows how that segment compares to all others for that metric — it does _not_ mean "good" or "bad" on its own. For example, a dark cell in the SNR column means that segment had one of the highest SNR values (which is good), while a dark cell in the Dynamic Range column during the handling noise test means high variability (which is bad — it indicates noise spikes).
  ]
]

#v(0.3cm)

#figure(
  image("segments/charts/07_summary_heatmap.png", width: 100%),
  caption: [All 24 segments × 9 metrics. Notice how handling noise (row 14) and noise floor (row 16) stand out from the speech segments. The numbers in each cell are the actual measured values.],
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

  + *Address the center of the screen, not the mic port.* The bottom mic port — where most people instinctively aim — had the worst signal-to-noise ratio (17.1 dB). Center/LCD address gives 4 dB better SNR, which means your voice is roughly 2.5× louder relative to background noise.

  + *Keep 10--15cm distance from the screen.* About a hand's length. Close enough for strong signal, far enough to avoid the bass boost and mouth noise that comes from being too close. At 3cm, distortion increases. At 30cm, signal falls off and recordings sound thin.

  + *Use a stand or mount.* Handling noise — the thumps and rumble from holding the phone — is the single biggest quality killer in phone recordings. Any basic phone stand, tripod, or even propping the phone against something stable will help.

  + *Use your phone case.* No measurable degradation with a case that has mic port cutouts. Volume within 0.3 dB (inaudible difference). SNR was actually slightly higher with the case on.

  + *Stay on-axis — face the screen directly.* Moving even 45° off-center drops your signal by ~4 dB (roughly half the power). Moving behind the phone is worst.

  + *Optimal setup summary:* Phone on a stand, case on, about a hand's length from the screen, speaking directly at the LCD center.
]

#v(0.6cm)

#block(
  fill: rgb("#e3f2fd"),
  inset: 14pt,
  radius: 6pt,
  width: 100%,
)[
  == Quick Reference Card

  #table(
    columns: (1fr, 1fr),
    stroke: none,
    inset: 6pt,
    [*Do*], [*Don't*],
    [Speak at the screen center], [Speak into the bottom mic port],
    [Stay 10--15cm away], [Get closer than 3cm or farther than 30cm],
    [Use a stand or mount], [Hold the phone in your hand],
    [Keep your case on], [Remove your case for recording],
    [Face the screen directly], [Speak from the side or behind],
  )
]

#v(1cm)

#align(center)[
  #text(size: 9pt, fill: rgb("#999"))[
    Analysis generated from 24 WAV segments using scipy, numpy, and matplotlib. \
    Full data available in `segments/analysis.json` and `segments/summary.csv`. \
    Video with stereo field visualization: `generate_video.py`
  ]
]
