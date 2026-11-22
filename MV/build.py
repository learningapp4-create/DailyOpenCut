#!/usr/bin/env python3
"""Cut ESSENCE, a music video about the essence of humanity in machines.

Open footage is downloaded into rushes/ (not committed), graded onto one
frame, and scored with an original piece. Run from this directory:

    python3 build.py

The edit is the SHOTS list. Durations sit on a 3-second bar (80 BPM).
See ART.md before changing the picture or the score.
"""

from __future__ import annotations

import array
import json
import math
import subprocess
import urllib.request
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUSH = ROOT / "rushes"
WORK = ROOT / "work"
UA = "DailyOpenCutMV/1.0 (essence; open footage; https://github.com/learningapp4-create/DailyOpenCut)"

W, H = 1280, 720
FPS = 24
BPM = 80
SR = 44100
TARGET = 180

# Night-city grades. A gaming cyberpunk audience reads cyan shadows and
# magenta highlights as the machine, and unsplit warm skin as the person.
# Do not invent a new grade for a single shot, and do not retouch the score.
GRADES = {
    "machine": (
        "eq=contrast=1.32:brightness=-0.05:saturation=1.22:gamma=0.86,"
        "colorbalance=rs=-0.14:gs=0.05:bs=0.20:rh=0.18:gh=-0.08:bh=0.14"
    ),
    "human": (
        "colorchannelmixer=rr=1.22:gg=0.98:bb=0.72,"
        "eq=contrast=1.16:brightness=0.02:gamma=1.05:saturation=1.05"
    ),
    "warm": (
        "eq=contrast=1.32:brightness=-0.07:saturation=1.18:gamma=0.82,"
        "colorbalance=rs=0.02:bs=0.14:rh=0.20:gh=-0.08:bh=0.02"
    ),
    "data": (
        "eq=contrast=1.35:brightness=-0.08:saturation=1.45:gamma=0.82,"
        "colorbalance=bs=0.22:rh=0.08:gh=0.02:bh=-0.06"
    ),
    "machine_warm": (
        "eq=contrast=1.22:brightness=-0.02:saturation=1.1:gamma=0.92,"
        "colorbalance=rs=0.02:bs=0.12:rh=0.16:gh=-0.04:bh=0.08"
    ),
}
# Small RGB split on the machine world only. Skin stays registered.
ABERRATION = {
    "machine": "rgbashift=rh=3:bh=-3",
    "data": "rgbashift=rh=4:bh=-4",
    "machine_warm": "rgbashift=rh=2:bh=-2",
    "warm": "rgbashift=rh=2:bh=-2",
}

FOOTAGE = [
    {
        "id": "landeron",
        "file": "landeron.webm",
        "url": "https://upload.wikimedia.org/wikipedia/commons/d/dc/Landeron_189_Chronograph_movement.webm",
        "page": "https://commons.wikimedia.org/wiki/File:Landeron_189_Chronograph_movement.webm",
        "author": "Erik Sutterud",
        "license": "CC BY 3.0",
        "licenseUrl": "https://creativecommons.org/licenses/by/3.0",
        "what": "Macro of a Landeron 189 chronograph movement",
    },
    {
        "id": "actuator",
        "file": "actuator.ogv",
        "url": "https://upload.wikimedia.org/wikipedia/commons/a/af/Hard_Disk_Actuator.ogv",
        "page": "https://commons.wikimedia.org/wiki/File:Hard_Disk_Actuator.ogv",
        "author": "Fletcher6",
        "license": "CC BY 4.0",
        "licenseUrl": "https://creativecommons.org/licenses/by/4.0",
        "what": "Hard-disk actuator arm",
    },
    {
        "id": "gear",
        "file": "gear.webm",
        "url": "https://upload.wikimedia.org/wikipedia/commons/7/7a/Preston_Mill_gear_in_action.webm",
        "page": "https://commons.wikimedia.org/wiki/File:Preston_Mill_gear_in_action.webm",
        "author": "Magnus Hagdorn",
        "license": "CC BY-SA 2.0",
        "licenseUrl": "https://creativecommons.org/licenses/by-sa/2.0",
        "what": "Preston Mill gear in action",
    },
    {
        "id": "baxter",
        "file": "baxter.webm",
        "url": "https://upload.wikimedia.org/wikipedia/commons/4/4a/Baxter_full.webm",
        "page": "https://commons.wikimedia.org/wiki/File:Baxter_full.webm",
        "author": "Muhannad Alomari, David C. Hogg, and Anthony G. Cohn",
        "license": "CC BY 4.0",
        "licenseUrl": "https://creativecommons.org/licenses/by/4.0",
        "what": "Baxter robot moving objects with two arms",
    },
    {
        "id": "hands",
        "file": "hands.webm",
        "url": "https://upload.wikimedia.org/wikipedia/commons/c/c9/Hands_short_film.webm",
        "page": "https://commons.wikimedia.org/wiki/File:Hands_short_film.webm",
        "author": "Ramin Mazur",
        "license": "CC BY 3.0",
        "licenseUrl": "https://creativecommons.org/licenses/by/3.0",
        "what": "Hands, from the short film Hands",
    },
    {
        "id": "piano",
        "file": "piano.ogv",
        "url": "https://upload.wikimedia.org/wikipedia/commons/f/f1/Temporal-Control-and-Hand-Movement-Efficiency-in-Skilled-Music-Performance-pone.0050901.s001.ogv",
        "page": "https://commons.wikimedia.org/wiki/File:Temporal-Control-and-Hand-Movement-Efficiency-in-Skilled-Music-Performance-pone.0050901.s001.ogv",
        "author": "Werner Goebl and Caroline Palmer",
        "license": "CC BY 2.5",
        "licenseUrl": "https://creativecommons.org/licenses/by/2.5",
        "what": "Pianists' hands reconstructed as motion data",
    },
    {
        "id": "press",
        "file": "press.webm",
        "url": "https://upload.wikimedia.org/wikipedia/commons/1/15/Printing_in_a_letterpress.webm",
        "page": "https://commons.wikimedia.org/wiki/File:Printing_in_a_letterpress.webm",
        "author": "Subhashish Panigrahi",
        "license": "CC BY-SA 4.0",
        "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0",
        "what": "Letterpress printing in Cuttack",
    },
    {
        "id": "sew",
        "file": "sew.webm",
        "url": "https://upload.wikimedia.org/wikipedia/commons/8/87/Singer_sewing_machine_at_G%C3%B6tebortgs_Remfabrik.webm",
        "page": "https://commons.wikimedia.org/wiki/File:Singer_sewing_machine_at_G%C3%B6tebortgs_Remfabrik.webm",
        "author": "Magdalena Akerstrom",
        "license": "CC BY 3.0",
        "licenseUrl": "https://creativecommons.org/licenses/by/3.0",
        "what": "Singer sewing machine at Göteborgs Remfabrik",
    },
    {
        "id": "hdd",
        "file": "hdd.webm",
        "url": "https://upload.wikimedia.org/wikipedia/commons/c/cf/HDD_Startup_and_Shutdown.webm",
        "page": "https://commons.wikimedia.org/wiki/File:HDD_Startup_and_Shutdown.webm",
        "author": "ZOKIDIN",
        "license": "CC BY-SA 4.0",
        "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0",
        "what": "Open hard drive, platters and coil",
    },
    {
        "id": "window",
        "file": "windowbot.webm",
        "url": "https://upload.wikimedia.org/wikipedia/commons/3/3d/Window_cleaning_robot_in_action_seen_through_window.webm",
        "page": "https://commons.wikimedia.org/wiki/File:Window_cleaning_robot_in_action_seen_through_window.webm",
        "author": "Pittigrilli",
        "license": "CC BY-SA 4.0",
        "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0",
        "what": "Window-cleaning robot, and the street in the glass",
    },
    {
        "id": "projector",
        "file": "projector.ogv",
        "url": "https://upload.wikimedia.org/wikipedia/commons/b/b8/35_mm_projection.theora.ogv",
        "page": "https://commons.wikimedia.org/wiki/File:35_mm_projection.theora.ogv",
        "author": "Fanny Schertzer",
        "license": "CC BY-SA 3.0",
        "licenseUrl": "https://creativecommons.org/licenses/by-sa/3.0",
        "what": "Threading a 35 mm projector",
    },
]

# length is output seconds. Keep it on the bar (multiples of 3).
# over: screen-blend this plate on top. The hands film is shot on black, so
# screen blend lets skin float inside the machine.
SHOTS = [
    dict(id="open", footage="landeron", start=38.0, length=6, grade="machine", x=0.50, y=0.46, drift=0.06, punch=360, fade_in=0.8),
    dict(id="finger", footage="actuator", start=1.0, length=6, grade="machine", x=0.48, y=0.42, drift=-0.06, punch=420),
    # The mill is a sunlit barn under this grade. The watch returns on another wheel.
    dict(id="jewel", footage="landeron", start=20.0, length=6, grade="machine", x=0.62, y=0.38, drift=0.04, punch=480),
    # Both arms and the gripper. The face screen drops out. A wall strip stays at the right, because a tighter crop loses the arm while it moves.
    dict(id="arms", footage="baxter", start=12.0, length=6, speed=1.25, grade="machine", x=0.34, y=0.30, punch=1300, precrop="iw*0.78:ih:iw*0.11:0"),
    dict(id="reach", footage="hands", start=39.0, length=6, grade="human", x=0.48, y=0.46, punch=180),
    dict(id="data", footage="piano", start=2.0, length=6, grade="data", x=0.50, y=0.38, drift=0.04, punch=240),
    dict(id="press", footage="press", start=0.3, length=3, grade="warm", x=0.46, y=0.42, punch=480),
    # Later pass on the rollers. The camera slips toward the wall in the last half second. The face stays out.
    dict(id="printer", footage="press", start=14.5, length=3, grade="warm", x=0.32, y=0.48, punch=1200),
    dict(id="thread", footage="sew", start=0.8, length=3, grade="warm", x=0.55, y=0.62, punch=1100),
    dict(id="through", footage="landeron", start=55.0, length=6, grade="machine", x=0.52, y=0.44, drift=0.05, punch=400,
         over=dict(footage="hands", start=76.0, grade="human", x=0.50, y=0.42, punch=160)),
    dict(id="organ", footage="hdd", start=3.5, length=6, grade="machine", x=0.50, y=0.30, punch=360),
    # The robot on the glass. The man, the cars, and the shop lettering stay out.
    dict(id="glass", footage="window", start=19.0, length=3, grade="machine", x=0.48, y=0.62, punch=1400),
    # Hands on the gate. The face and the warning sign stay out. The hands leave in the last second; the mechanism stays.
    dict(id="gate", footage="projector", start=32.0, length=6, grade="warm", x=0.26, y=0.62, punch=1000),
    dict(id="hold", footage="hands", start=199.0, length=6, grade="human", x=0.50, y=0.44, punch=200),
    dict(id="palm", footage="actuator", start=3.5, length=6, grade="machine", x=0.46, y=0.40, drift=0.04, punch=480,
         over=dict(footage="hands", start=118.0, grade="human", x=0.50, y=0.48, punch=200)),
    dict(id="memory", footage="landeron", start=8.0, length=6, speed=0.9, grade="machine_warm", x=0.48, y=0.50, drift=-0.04, punch=300),
    dict(id="water", footage="hands", start=223.5, length=6, grade="human", x=0.50, y=0.46, punch=80, fade_out=2.2),
]


def run(cmd: list[str]) -> None:
    done = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if done.returncode != 0:
        tail = done.stderr.decode(errors="replace")[-2500:]
        raise SystemExit(f"command failed:\n{' '.join(cmd[:6])}\n{tail}")


def download(item: dict) -> Path:
    RUSH.mkdir(exist_ok=True)
    dest = RUSH / item["file"]
    if dest.exists() and dest.stat().st_size > 1000:
        return dest
    print(f"download {item['file']}")
    req = urllib.request.Request(item["url"], headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as response, dest.open("wb") as handle:
        while True:
            chunk = response.read(1 << 20)
            if not chunk:
                break
            handle.write(chunk)
    return dest


def plate_filter(shot: dict, grade: str) -> str:
    speed = float(shot.get("speed", 1))
    length = float(shot["length"])
    start = float(shot["start"])
    src = length * speed + 0.2
    punch = int(shot.get("punch", 280))
    box_w = W + punch
    box_h = H + int(punch * H / W)
    bias_x = float(shot.get("x", 0.5))
    bias_y = float(shot.get("y", 0.5))
    drift = float(shot.get("drift", 0))
    # Stay inside the crop window.
    if bias_x + drift > 0.98:
        drift = 0.98 - bias_x
    if bias_x + drift < 0.02:
        drift = 0.02 - bias_x
    parts = [
        f"trim=start={start:.3f}:end={start + src:.3f}",
        "setpts=PTS-STARTPTS",
        f"setpts=PTS/{speed:.4f}",
        f"fps={FPS}",
    ]
    if shot.get("precrop"):
        parts.append(f"crop={shot['precrop']}")
    parts.append(GRADES[grade])
    parts.append(f"scale={box_w}:{box_h}:force_original_aspect_ratio=increase")
    parts.append(
        "crop=1280:720:"
        f"x='trunc((in_w-out_w)*({bias_x:.4f}+{drift:.4f}*t/{length:.3f})/2)*2':"
        f"y='trunc((in_h-out_h)*{bias_y:.4f}/2)*2'"
    )
    parts.append("unsharp=5:5:0.4:5:5:0.0")
    if grade in ABERRATION:
        parts.append(ABERRATION[grade])
    parts.append("vignette=PI/6")
    parts.append(f"trim=duration={length:.3f}")
    parts.append("setpts=PTS-STARTPTS")
    if shot.get("fade_in"):
        parts.append(f"fade=t=in:st=0:d={float(shot['fade_in']):.3f}:color=black")
    if shot.get("fade_out"):
        fade = float(shot["fade_out"])
        parts.append(f"fade=t=out:st={length - fade:.3f}:d={fade:.3f}:color=black")
    parts.append("noise=alls=4:allf=t")
    parts.append("format=yuv420p")
    parts.append("setsar=1")
    return ",".join(parts)


def render_plate(shot: dict, grade: str, dest: Path) -> None:
    src = download(next(item for item in FOOTAGE if item["id"] == shot["footage"]))
    run([
        "ffmpeg", "-y", "-i", str(src),
        "-vf", plate_filter(shot, grade),
        "-an", "-r", str(FPS),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p",
        str(dest),
    ])


def render_shot(shot: dict, dest: Path) -> None:
    if "over" not in shot:
        render_plate(shot, shot["grade"], dest)
        return
    base = WORK / f"{shot['id']}_base.mp4"
    over = WORK / f"{shot['id']}_over.mp4"
    render_plate(shot, shot["grade"], base)
    over_shot = dict(shot["over"])
    over_shot["length"] = shot["length"]
    render_plate(over_shot, over_shot.get("grade", "human"), over)
    run([
        "ffmpeg", "-y", "-i", str(base), "-i", str(over),
        # Screen in RGB. In YUV the same mode paints the frame magenta.
        "-filter_complex",
        "[0:v]format=gbrp[b];[1:v]format=gbrp[o];[b][o]blend=all_mode=screen:shortest=1,format=yuv420p,setsar=1",
        "-an", "-r", str(FPS),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p",
        str(dest),
    ])


def note(freq: float, t0: float, dur: float, amp: float, left, right, pan: float) -> None:
    n0 = int(t0 * SR)
    n1 = min(len(left), int((t0 + dur) * SR))
    attack, release = 0.035, min(0.16, dur * 0.45)
    for i in range(n0, n1):
        tt = (i - n0) / SR
        if tt < attack:
            env = tt / attack
        elif tt > dur - release:
            env = max(0.0, (dur - tt) / release)
        else:
            env = 1.0
        body = math.sin(2 * math.pi * freq * i / SR)
        air = math.sin(2 * math.pi * freq * 2 * i / SR)
        sample = amp * env * (body + 0.22 * air)
        left[i] += sample * (1 - pan)
        right[i] += sample * pan


def pulse(freq: float, t0: float, dur: float, amp: float, decay: float, left, right, pan: float) -> None:
    n0 = int(t0 * SR)
    n1 = min(len(left), int((t0 + dur) * SR))
    for i in range(n0, n1):
        tt = (i - n0) / SR
        sample = amp * math.exp(-tt / decay) * math.sin(2 * math.pi * freq * i / SR)
        left[i] += sample * (1 - pan)
        right[i] += sample * pan


def write_score(path: Path, duration: float) -> None:
    n = int(duration * SR)
    left = array.array("f", [0.0]) * n
    right = array.array("f", [0.0]) * n
    beat = 60 / BPM

    # Drone: the room the machine and the body share.
    for i in range(n):
        t = i / SR
        trem = 0.86 + 0.14 * math.sin(2 * math.pi * 0.07 * t)
        a = 0.026 * trem * math.sin(2 * math.pi * 110.0 * i / SR)
        e = 0.015 * trem * math.sin(2 * math.pi * 164.81 * i / SR)
        left[i] += a + e
        right[i] += a + e

    # Heart on every beat, a watch-tick beside it. Both stop thinning at 1:24,
    # and the tick leaves entirely for the last bar.
    t = 0.0
    while t < duration - 0.05:
        heart = 0.36 if (round(t / beat) % 4 in (0, 2)) else 0.24
        if t > duration - 6:
            heart *= 0.55
        pulse(52, t, 0.28, heart, 0.055, left, right, 0.5)
        pulse(90, t, 0.08, heart * 0.25, 0.02, left, right, 0.5)
        if t < duration - 6:
            pulse(2100, t, 0.015, 0.045, 0.004, left, right, 0.68)
        if 24 <= t < duration - 6:
            pulse(640, t + beat * 0.5, 0.08, 0.03, 0.02, left, right, 0.38)
        t += beat

    # Melody enters with the first hand. Quarters, then longer notes as the
    # picture starts to hold. A minor pentatonic, low, two cents sharp on the right.
    a3, c4, d4, e4, g4, a4, c5 = 220.00, 261.63, 293.66, 329.63, 392.00, 440.00, 523.25
    quarters = [
        (24, [a3, c4, e4, g4, a4, g4, e4, d4], 0.075),
        (30, [e4, d4, c4, a3, c4, d4, e4, g4], 0.072),
        (36, [a4, g4, e4, c4, d4, e4, g4, e4], 0.07),
        (42, [c4, e4, g4, a4, g4, e4, d4, c4], 0.068),
        (60, [a3, c4, e4, a4, g4, e4, d4, c4], 0.062),
        (66, [e4, g4, a4, c5, a4, g4, e4, d4], 0.055),
    ]
    for start, tones, amp in quarters:
        for k, freq in enumerate(tones):
            t0 = start + k * beat
            note(freq, t0, beat * 0.92, amp, left, right, 0.38)
            note(freq * 1.003, t0, beat * 0.92, amp * 0.7, left, right, 0.62)
    halves = [
        (48, [a3, e4, c4, a3], 0.06),
        (54, [d4, e4, g4, e4], 0.055),
        (72, [a3, c4, e4, a3], 0.045),
        (78, [d4, e4], 0.035),
    ]
    for start, tones, amp in halves:
        step = 6 / len(tones)
        for k, freq in enumerate(tones):
            t0 = start + k * step
            note(freq, t0, step * 0.96, amp, left, right, 0.38)
            note(freq * 1.003, t0, step * 0.96, amp * 0.65, left, right, 0.62)

    peak = 1e-6
    for i in range(n):
        t = i / SR
        if t < 1.2:
            gain = t / 1.2
        elif t > duration - 3.5:
            gain = max(0.0, (duration - t) / 3.5)
        else:
            gain = 1.0
        left[i] *= gain
        right[i] *= gain
        peak = max(peak, abs(left[i]), abs(right[i]))
    scale = 0.9 / peak
    with wave.open(str(path), "w") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(SR)
        packed = array.array("h")
        for i in range(n):
            packed.append(max(-32767, min(32767, int(left[i] * scale * 32767))))
            packed.append(max(-32767, min(32767, int(right[i] * scale * 32767))))
        handle.writeframes(packed.tobytes())


def write_cut_js(duration: float, used: list[dict]) -> None:
    credits = [
        {
            "title": "Original score",
            "author": "written for this film",
            "license": "CC BY-SA 4.0",
            "url": "https://creativecommons.org/licenses/by-sa/4.0",
        }
    ]
    for item in used:
        credits.append({
            "title": item["what"],
            "author": item["author"],
            "license": item["license"],
            "url": item["page"],
        })
    payload = {
        "title": "ESSENCE",
        "theme": "the essence of humanity in machines",
        "file": "essence.mp4",
        "poster": "poster.jpg",
        "durationSeconds": round(duration, 2),
        "targetSeconds": TARGET,
        "movement": "I",
        "movementTitle": "the machine remembers a hand",
        "version": 7,
        "rendered": "2026-11-22",
        "filmLicense": "CC BY-SA 4.0",
        "credits": credits,
    }
    text = "window.CUT = " + json.dumps(payload, indent=2) + ";\n"
    (ROOT / "cut.js").write_text(text)


def main() -> None:
    WORK.mkdir(exist_ok=True)
    duration = 0.0
    for shot in SHOTS:
        length = float(shot["length"])
        if abs(length / 3 - round(length / 3)) > 1e-6:
            raise SystemExit(f"{shot['id']} is {length}s, off the 3-second bar")
        duration += length
    print(f"timeline {duration:.0f}s / {TARGET}s target")

    segments = []
    for shot in SHOTS:
        dest = WORK / f"{shot['id']}.mp4"
        print(f"shot {shot['id']} ({shot['length']}s)")
        render_shot(shot, dest)
        segments.append(dest)

    listing = WORK / "concat.txt"
    listing.write_text("".join(f"file '{path}'\n" for path in segments))
    silent = WORK / "picture.mp4"
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
        "-c", "copy", str(silent),
    ])

    score = WORK / "score.wav"
    print("score")
    write_score(score, duration)

    alpha = (
        "alpha='if(lt(t\\,7.2)\\,0\\,if(lt(t\\,8.1)\\,(t-7.2)/0.9\\,"
        "if(lt(t\\,11.4)\\,1\\,if(lt(t\\,12.4)\\,(12.4-t)/1.0\\,0))))'"
    )
    font = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-ExtraBold.ttf"

    def title_layer(color: str, dx: int) -> str:
        return (
            f"drawtext=fontfile={font}:text='ESSENCE':fontsize=36:"
            f"fontcolor={color}:x=(w-text_w)/2{dx:+d}:y=h*0.78:{alpha}"
        )

    title = ",".join([
        title_layer("0x5CE1E6@0.9", -4),
        title_layer("0xFF2BD6@0.8", 4),
        title_layer("white@0.96", 0),
    ])
    out = ROOT / "essence.mp4"
    print("master")
    run([
        "ffmpeg", "-y", "-i", str(silent), "-i", str(score),
        "-vf", title,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "27", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k",
        "-movflags", "+faststart",
        "-shortest",
        str(out),
    ])
    poster = ROOT / "poster.jpg"
    # The first double exposure: skin inside the watch.
    run([
        "ffmpeg", "-y", "-ss", "48", "-i", str(out),
        "-frames:v", "1", "-q:v", "3", str(poster),
    ])
    probed = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(out),
    ])
    actual = float(probed.strip())
    used_ids = []
    for shot in SHOTS:
        used_ids.append(shot["footage"])
        if "over" in shot:
            used_ids.append(shot["over"]["footage"])
    used = [item for item in FOOTAGE if item["id"] in dict.fromkeys(used_ids)]
    write_cut_js(actual, used)
    print(f"wrote {out.name} {actual:.2f}s {out.stat().st_size / 1e6:.1f}MB")


if __name__ == "__main__":
    main()
