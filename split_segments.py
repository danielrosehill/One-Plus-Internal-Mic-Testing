#!/usr/bin/env python3
"""Split the OnePlus mic test WAV into individual segments and generate JSON metadata."""

import json
import subprocess
import os

REPO = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(REPO, "One Plus audio Testing.wav")
OUT_DIR = os.path.join(REPO, "segments")

SEGMENTS = [
    {
        "segment_number": 1,
        "filename": "01_intro.wav",
        "title": "Introduction & Recording Setup",
        "start": "00:00.0",
        "end": "02:25.0",
        "start_seconds": 0.0,
        "end_seconds": 145.0,
        "address_pattern": None,
        "distance_cm": None,
        "description": "Preamble describing the recording setup, purpose of the test, device info (OnePlus Nord 3 5G), recording app (ASR), and parameters (48kHz WAV stereo, all digital processing disabled).",
        "transcript": "The purpose of this audio file and video is to demonstrate some differences in sound quality and recording quality using a Android smartphone with a somewhat decent internal microphone and providing some voice samples as to how different pickup patterns are going to affect the quality the recording. So before going further, let me just describe the recording parameters that are currently being used for this file and it's RAW format. These might be processed down in in later processing, but this is the original audio recording in wav and recording at 48khz as the as the bit rate audio channel is stereo and using for this particular recording ASR which is my favorite Android recording app and all the digital controls have been disabled for noise cancellation, auto gain control, anything like that. So this is attempting to really just get it at a pretty raw condition. The reason that I'm doing this is I've started an AI podcast AI generated podcast in which I send in prompts which make it into the podcast through a production pipeline and initially intended mostly to be recording the prompts in a proper recording environment with the desktop microphone and all the rest of the gear, but ended up over time recording it predominantly on my phone. Initially I built a web app to do this directly, but then I found that much better results were achieved using a standalone recording app and then uploading the file into the production process that way. It also means that it's not online dependent. The results have been fairly good sometimes and it's made me think that the question of how to actually use a smartphone for as a microphone is rarely discussed. We usually just think of these as not good sources for audio quality, but as the microphone quality put into them gets better, I think it's worth just as you test a microphone testing this phone. So to describe firstly the current recording setup, what I'm going to demonstrate is the difference in quality through a few specific address patterns in type. Firstly in address type.",
        "case_on": False,
        "mount": None,
    },
    {
        "segment_number": 2,
        "filename": "02_center_lcd_10cm.wav",
        "title": "Center/LCD Screen Address (~10cm)",
        "start": "02:25.0",
        "end": "02:48.0",
        "start_seconds": 145.0,
        "end_seconds": 168.0,
        "address_pattern": "Center/LCD screen",
        "distance_cm": 10,
        "description": "Speaking into the center of the phone from about 10cm, targeting the center point of the LCD screen. Discusses how this address pattern might actually be better than addressing the bottom mic directly.",
        "transcript": "So this is. I'm actually speaking into the center of the phone from about 10 centimeters. I'm speaking literally as if I'm targeting the center point of the LCD screen. I assumed always that this didn't make any sense, but learning a bit about the microphone placement here, it might actually be a better pickup pattern or address pattern technically than using what I assumed was the best.",
        "case_on": False,
        "mount": None,
    },
    {
        "segment_number": 3,
        "filename": "03_bottom_mic_10cm.wav",
        "title": "Bottom Microphone Address (~10cm)",
        "start": "02:48.0",
        "end": "03:13.0",
        "start_seconds": 168.0,
        "end_seconds": 193.0,
        "address_pattern": "Bottom microphone (primary, near USB-C)",
        "distance_cm": 10,
        "description": "Directing voice at the primary microphone at the bottom of the phone, next to the USB Type-C port, from about 10cm.",
        "transcript": "And I'm going to switch to my previous assumption and that is what I'm doing now. So I've just moved the. I moved my mouth. My mouth is about 10 centimeters from the device, but I'm directing my voice now instead of at the LCD screen. I'm speaking directly into the microphone at the bottom of the screen, just next to the USB type C port, which is the primary microphone on this device.",
        "case_on": False,
        "mount": None,
    },
    {
        "segment_number": 4,
        "filename": "04_top_mic.wav",
        "title": "Top Microphone (Secondary)",
        "start": "03:13.0",
        "end": "03:24.0",
        "start_seconds": 193.0,
        "end_seconds": 204.0,
        "address_pattern": "Top microphone (secondary)",
        "distance_cm": 10,
        "description": "Addressing the top of the device where the secondary microphone is located.",
        "transcript": "And what I'm going to do now is flip over to the top. And now I'm addressing the top of the device where the secondary microphone is located.",
        "case_on": False,
        "mount": None,
    },
    {
        "segment_number": 5,
        "filename": "05_proximity_10-15cm.wav",
        "title": "Proximity Test — 10–15cm",
        "start": "03:24.0",
        "end": "03:38.0",
        "start_seconds": 204.0,
        "end_seconds": 218.0,
        "address_pattern": "Center/LCD screen",
        "distance_cm": 12,
        "description": "Proximity test from approximately 10–15cm from the phone, addressing the center/screen.",
        "transcript": "What I'm going to do now I've shifted back to the center and I'm going to just a couple of experiments in proximity, a proximity effect. So currently at estimate, I'm about, as I say, 10 to maybe 15 centimeters from the phone.",
        "case_on": False,
        "mount": None,
    },
    {
        "segment_number": 6,
        "filename": "06_proximity_3cm.wav",
        "title": "Proximity Test — ~3cm",
        "start": "03:38.0",
        "end": "03:45.0",
        "start_seconds": 218.0,
        "end_seconds": 225.0,
        "address_pattern": "Center/LCD screen",
        "distance_cm": 3,
        "description": "Speaking right about 3cm away from the screen — very close proximity test.",
        "transcript": "And now I'm literally speaking right about 3cm away from the screen. Now I'm literally almost touching the screen.",
        "case_on": False,
        "mount": None,
    },
    {
        "segment_number": 7,
        "filename": "07_proximity_touching.wav",
        "title": "Proximity Test — Almost Touching",
        "start": "03:45.0",
        "end": "03:47.0",
        "start_seconds": 225.0,
        "end_seconds": 227.0,
        "address_pattern": "Center/LCD screen",
        "distance_cm": 0.5,
        "description": "Almost touching the screen — closest possible proximity test.",
        "transcript": "This is about as close as I can come.",
        "case_on": False,
        "mount": None,
    },
    {
        "segment_number": 8,
        "filename": "08_proximity_30cm.wav",
        "title": "Proximity Test — ~30cm Comfortable Distance",
        "start": "03:47.0",
        "end": "03:57.0",
        "start_seconds": 227.0,
        "end_seconds": 237.0,
        "address_pattern": "Center/LCD screen",
        "distance_cm": 30,
        "description": "Speaking from a comfortable recording distance of about 30cm from the screen. Describes this as 'address pattern one'.",
        "transcript": "Now I'm at a more comfortable recording distance. I've about 30cm between myself and the screen. And this is what we can call address pattern one, addressing the screen.",
        "case_on": False,
        "mount": None,
    },
    {
        "segment_number": 9,
        "filename": "09_bottom_mic_recap.wav",
        "title": "Address Pattern 2 Recap — Bottom Mic",
        "start": "03:57.0",
        "end": "04:01.0",
        "start_seconds": 237.0,
        "end_seconds": 241.0,
        "address_pattern": "Bottom microphone (primary, near USB-C)",
        "distance_cm": None,
        "description": "Brief recap of address pattern two — speaking directly to the bottom of the phone.",
        "transcript": "And now I'm moving back to address pattern two, speaking directly to the bottom of the phone.",
        "case_on": False,
        "mount": None,
    },
    {
        "segment_number": 10,
        "filename": "10_top_mic_recap.wav",
        "title": "Address Pattern 3 Recap — Top Mic",
        "start": "04:01.0",
        "end": "04:05.0",
        "start_seconds": 241.0,
        "end_seconds": 245.0,
        "address_pattern": "Top microphone (secondary)",
        "distance_cm": None,
        "description": "Brief recap of address pattern three — speaking to the top of the phone.",
        "transcript": "And finally address pattern three, speaking to the top of the phone.",
        "case_on": False,
        "mount": None,
    },
    {
        "segment_number": 11,
        "filename": "11_phone_to_ear.wav",
        "title": "Phone Held to Ear (Pattern 4)",
        "start": "04:05.0",
        "end": "04:38.0",
        "start_seconds": 245.0,
        "end_seconds": 278.0,
        "address_pattern": "Phone to ear — speaking away from mic",
        "distance_cm": None,
        "description": "Phone held to ear as if making a call. Speaking away from the microphone, voice directed naturally forward/toward the wall.",
        "transcript": "What I'm going to do now is put the phone up to my ear as if I were using it conventionally as a, as a phone. And the pickup is going to be, instead of me speaking towards the microphone, I'm going to be speaking away from the microphone with a tremor. Okay, so this is pickup pattern four. I'm speaking away from the phone as if I was taking a call, holding it up to my ear physically and targeting. Well, I guess when you, when you speak on the phone, you don't tend to think where your voice is going, just speaking naturally kind of to the wall.",
        "case_on": False,
        "mount": None,
    },
    {
        "segment_number": 12,
        "filename": "12_phone_to_ear_downward.wav",
        "title": "Phone to Ear — Voice Directed Downward",
        "start": "04:38.0",
        "end": "04:44.0",
        "start_seconds": 278.0,
        "end_seconds": 284.0,
        "address_pattern": "Phone to ear — voice directed downward",
        "distance_cm": None,
        "description": "Phone held to ear with voice specifically directed downward toward the ground.",
        "transcript": "Now I'm speaking very specifically downwards towards the ground. Was the phone still held to my ear?",
        "case_on": False,
        "mount": None,
    },
    {
        "segment_number": 13,
        "filename": "13_return_to_center.wav",
        "title": "Return to Center Address",
        "start": "04:44.0",
        "end": "04:50.0",
        "start_seconds": 284.0,
        "end_seconds": 290.0,
        "address_pattern": "Center/LCD screen",
        "distance_cm": 10,
        "description": "Returning to handheld center address after the phone-to-ear tests.",
        "transcript": "And now we're back to the me not holding the phone to my ear and addressing the center of the microphone.",
        "case_on": False,
        "mount": None,
    },
    {
        "segment_number": 14,
        "filename": "14_handling_noise.wav",
        "title": "Handling Noise Test",
        "start": "04:50.0",
        "end": "05:14.0",
        "start_seconds": 290.0,
        "end_seconds": 314.0,
        "address_pattern": None,
        "distance_cm": None,
        "description": "Handling noise test — moving the phone around, putting it in pocket and back, to test microphone sensitivity to handling noise.",
        "transcript": "Okay, part two, handling noise rejection. So what I'm going to do for the next 10 seconds is just broadly handle the phone. I'm going to be just moving it around. I'll put in my pocket and back, in fact, so we can see how sensitive the microphones are to handling noise.",
        "case_on": False,
        "mount": None,
    },
    {
        "segment_number": 15,
        "filename": "15_mount_handling_noise.wav",
        "title": "Phone on Mount — Transferred Handling Noise",
        "start": "05:14.0",
        "end": "05:56.0",
        "start_seconds": 314.0,
        "end_seconds": 356.0,
        "address_pattern": None,
        "distance_cm": None,
        "description": "Phone placed in a mount (used as a microphone stand). Testing how well the phone rejects handling noise transferred through the mount. Shaking the mount to test vibration transfer.",
        "transcript": "Okay, now what I'm going to do is take the phone, the OnePlus, and I'm going to pop it into the amount that I have, which I'm experimenting with as a sort of microphone stand. It's clipped in now and I'm going to, instead of handling the phone, I'm going to handle the mount it's on in order to see how well it rejects transferred Handling noise. So we can see a little bit. If I really shake it, the vibrations are transferring into the case, but pretty good rejection overall.",
        "case_on": False,
        "mount": "Generic mount (used as mic stand)",
    },
    {
        "segment_number": 16,
        "filename": "16_noise_floor.wav",
        "title": "Room Noise Floor Profile",
        "start": "05:56.0",
        "end": "06:21.0",
        "start_seconds": 356.0,
        "end_seconds": 381.0,
        "address_pattern": None,
        "distance_cm": None,
        "description": "Capturing the ambient room noise floor. Untreated room with background sounds (soda opening, fridge hum). Brief commentary followed by silence to capture the noise floor.",
        "transcript": "Here is what the noise floor profile sounds like. Recording this in an untreated room, average apartment and you're going to hear some background noises like someone opening some soda, pouring some soda, a fridge in the background. So fairly, fairly good, fairly clean noise floor.",
        "case_on": False,
        "mount": None,
    },
    {
        "segment_number": 17,
        "filename": "17_case_description.wav",
        "title": "Describing the Phone Case",
        "start": "06:21.0",
        "end": "07:01.0",
        "start_seconds": 381.0,
        "end_seconds": 421.0,
        "address_pattern": None,
        "distance_cm": None,
        "description": "Describing the phone case before testing its impact on recording quality. Black hard shell case with cutouts for top and bottom microphones.",
        "transcript": "And final test is I think this would be an important one for most of us use our androids in cases without thinking about the difference it might make to the recording quality. I'm looking at the case that I have just to describe it. It's a black hard shell type case that just pops over the handset and it has a little cutout for the microphone at the top and the bottom. So it's designed with that in mind. Not all phone cases have those little gaps, but nevertheless, well, we'll see if it makes any appreciable difference whatsoever. Maybe it won't. So I'm going to just pop the phone into the case now.",
        "case_on": False,
        "mount": None,
    },
    {
        "segment_number": 18,
        "filename": "18_case_center_lcd.wav",
        "title": "With Case — Center/LCD Address (Pattern 1)",
        "start": "07:01.0",
        "end": "07:12.0",
        "start_seconds": 421.0,
        "end_seconds": 432.0,
        "address_pattern": "Center/LCD screen",
        "distance_cm": 10,
        "description": "With case on — repeating address pattern 1, speaking towards the center of the LCD screen.",
        "transcript": "Okay, the OnePlus is cased. Now when you're going back to speaking, pick up pattern number one. Speaking towards the center of the LCD screen, pick up pattern number two.",
        "case_on": True,
        "mount": None,
    },
    {
        "segment_number": 19,
        "filename": "19_case_bottom_mic.wav",
        "title": "With Case — Bottom Mic Address (Pattern 2)",
        "start": "07:12.0",
        "end": "07:25.0",
        "start_seconds": 432.0,
        "end_seconds": 445.0,
        "address_pattern": "Bottom microphone (primary, near USB-C)",
        "distance_cm": 10,
        "description": "With case on — repeating address pattern 2, speaking directly at the bottom microphone.",
        "transcript": "Addressing directly the bottom of the phone. Now I'm going to try just a couple more experiments with long, long sensitivity about 10 centimeters from the handset. In fact, for this test I'll put it into the. Into the case again or into the into.",
        "case_on": True,
        "mount": None,
    },
    {
        "segment_number": 20,
        "filename": "20_ulanzi_stand_bottom_mic.wav",
        "title": "On Ulanzi Stand — Bottom Mic Address",
        "start": "07:34.0",
        "end": "07:55.0",
        "start_seconds": 454.0,
        "end_seconds": 475.0,
        "address_pattern": "Bottom microphone (primary, near USB-C)",
        "distance_cm": 10,
        "description": "Phone placed on Ulanzi selfie stick / stand at full extension (~2m). Addressing the bottom microphone.",
        "transcript": "Okay, now the OnePlus is in the. It's a stand from Ulanzi that's I think kind of intended as a selfie stick. It's about 2 meters. It's at its full extension, which is actually pretty nice use for this, this gadget. So I'm addressing the bottom of the microphone in the, in its while it's up here.",
        "case_on": True,
        "mount": "Ulanzi selfie stick/stand (~2m full extension)",
    },
    {
        "segment_number": 21,
        "filename": "21_ulanzi_stand_center_lcd.wav",
        "title": "On Ulanzi Stand — Center/LCD Address",
        "start": "07:55.0",
        "end": "08:09.0",
        "start_seconds": 475.0,
        "end_seconds": 489.0,
        "address_pattern": "Center/LCD screen",
        "distance_cm": 10,
        "description": "Phone on Ulanzi stand — addressing the center/LCD screen. Notes that waveforms in ASR look significantly better when addressing the screen.",
        "transcript": "Now I'm back to the center address pattern addressing literally the LCD screen. And I'm just looking at the waveforms in ASR. They look significantly better when I'm addressing the screen which has already flipped my understanding of the, of this on its head.",
        "case_on": True,
        "mount": "Ulanzi selfie stick/stand (~2m full extension)",
    },
    {
        "segment_number": 22,
        "filename": "22_360_walk.wav",
        "title": "360° Walk Around the Phone",
        "start": "08:09.0",
        "end": "08:42.0",
        "start_seconds": 489.0,
        "end_seconds": 522.0,
        "address_pattern": "360° walk (varying angles)",
        "distance_cm": None,
        "description": "Walking a full 360° around the phone while recording in stereo. Notes positions at 180°, 270° (90° left), and return to starting point.",
        "transcript": "What I'm actually going to do now is as we're recording in stereo, I'm going to Walk360 from where I am now and come all the way back to this starting point. Starting three, two, one. Now I'm just going to keep talking about nothing in particular, but I will note my position. I'm now 180 degrees off axis the way to the back of the phone. I'm now 270 degrees off axis. In other words, I'm 90 degrees to the left. And now I'm slowly coming back to my starting point here, directing my voice at the screen.",
        "case_on": True,
        "mount": "Ulanzi selfie stick/stand (~2m full extension)",
    },
    {
        "segment_number": 23,
        "filename": "23_off_axis_45_left.wav",
        "title": "45° Off-Axis Left",
        "start": "08:42.0",
        "end": "08:50.0",
        "start_seconds": 522.0,
        "end_seconds": 530.0,
        "address_pattern": "45° off-axis left",
        "distance_cm": None,
        "description": "Subtle off-axis test — speaking from 45 degrees to the left of center.",
        "transcript": "Let's try a little bit more subtle off axis. Testing. 45 degrees to the left. Speaking to the center of the phone.",
        "case_on": True,
        "mount": "Ulanzi selfie stick/stand (~2m full extension)",
    },
    {
        "segment_number": 24,
        "filename": "24_off_axis_45_right.wav",
        "title": "45° Off-Axis Right",
        "start": "08:50.0",
        "end": "08:59.0",
        "start_seconds": 530.0,
        "end_seconds": 539.0,
        "address_pattern": "45° off-axis right",
        "distance_cm": None,
        "description": "Subtle off-axis test — speaking from 45 degrees to the right of center.",
        "transcript": "And 45 degrees to the. Coming at it from the other side. Addressing the phone this way and seeing exactly how that does for the audio quality.",
        "case_on": True,
        "mount": "Ulanzi selfie stick/stand (~2m full extension)",
    },
]


def time_to_seconds(t: str) -> float:
    """Convert 'MM:SS.s' to seconds."""
    parts = t.split(":")
    minutes = int(parts[0])
    seconds = float(parts[1])
    return minutes * 60 + seconds


def split_segment(seg: dict) -> None:
    """Use ffmpeg to extract a segment from the source WAV."""
    out_path = os.path.join(OUT_DIR, seg["filename"])
    start = time_to_seconds(seg["start"])
    end = time_to_seconds(seg["end"])
    duration = end - start

    cmd = [
        "ffmpeg", "-y",
        "-i", SOURCE,
        "-ss", f"{start:.3f}",
        "-t", f"{duration:.3f}",
        "-c", "copy",
        out_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"  Created: {seg['filename']} ({duration:.1f}s)")


def write_metadata(seg: dict) -> None:
    """Write a JSON metadata file for the segment."""
    start_s = time_to_seconds(seg["start"])
    end_s = time_to_seconds(seg["end"])
    duration = end_s - start_s

    meta = {
        "filename": seg["filename"],
        "segment_number": seg["segment_number"],
        "title": seg["title"],
        "address_pattern": seg["address_pattern"],
        "distance_cm": seg["distance_cm"],
        "start_time": start_s,
        "end_time": end_s,
        "duration_seconds": round(duration, 2),
        "description": seg["description"],
        "transcript": seg["transcript"],
        "case_on": seg["case_on"],
        "mount": seg["mount"],
    }

    json_name = seg["filename"].replace(".wav", ".json")
    json_path = os.path.join(OUT_DIR, json_name)
    with open(json_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"  Created: {json_name}")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    print(f"Source: {SOURCE}")
    print(f"Output: {OUT_DIR}")
    print(f"Segments: {len(SEGMENTS)}\n")

    for seg in SEGMENTS:
        print(f"[{seg['segment_number']:02d}] {seg['title']}")
        split_segment(seg)
        write_metadata(seg)
        print()

    print("Done! All segments exported.")


if __name__ == "__main__":
    main()
