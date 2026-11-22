#!/usr/bin/env python3
"""Shared cutter for the MV samples.

ESSENCE keeps its own build.py. These films are separate 90-second samples.
Rushes live in MV/rushes/ and are not committed. Run a film from build_samples.py.
"""

from __future__ import annotations

import array
import json
import math
import subprocess
import urllib.request
import wave
from pathlib import Path

RUSH = Path(__file__).resolve().parent / "rushes"
UA = "DailyOpenCutMV/1.0 (samples; open footage; https://github.com/learningapp4-create/DailyOpenCut)"

W, H = 1280, 720
FPS = 24
SR = 44100
FONT = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-ExtraBold.ttf"

# Night-city family. Skin stays warm and registered. Machines take the split.
GRADES = {
    "night": (
        "eq=contrast=1.30:brightness=-0.02:saturation=1.26:gamma=0.92,"
        "colorbalance=rs=-0.14:gs=0.04:bs=0.20:rh=0.18:gh=-0.08:bh=0.12"
    ),
    "street": (
        "eq=contrast=1.26:brightness=-0.03:saturation=1.18:gamma=0.92,"
        "colorbalance=rs=0.04:bs=0.10:rh=0.16:gh=-0.04:bh=0.08"
    ),
    "human": (
        "colorchannelmixer=rr=1.20:gg=0.98:bb=0.74,"
        "eq=contrast=1.14:brightness=0.02:gamma=1.04:saturation=1.04"
    ),
    "game": (
        "colorchannelmixer=rr=0.85:rb=0.18:gg=1.05:gb=0.22:bb=0.42:br=0.04,"
        "eq=contrast=1.40:brightness=-0.08:saturation=1.20:gamma=0.76,"
        "colorbalance=rh=0.08:gh=0.02:bh=0.12:bs=-0.06"
    ),
    "crt": (
        "eq=contrast=1.38:brightness=-0.07:saturation=1.30:gamma=0.80,"
        "colorbalance=rs=-0.10:gs=0.08:bs=0.06:rh=0.06:gh=0.14:bh=-0.08"
    ),
    "data": (
        "eq=contrast=1.36:brightness=-0.08:saturation=1.50:gamma=0.80,"
        "colorbalance=bs=0.18:rh=0.06:gh=0.10:bh=-0.08"
    ),
    "neon": (
        "eq=contrast=1.40:brightness=-0.04:saturation=1.45:gamma=0.82,"
        "colorbalance=rs=-0.08:bs=0.10:rh=0.24:gh=-0.12:bh=0.16"
    ),
    "chrome": (
        "eq=contrast=1.30:brightness=-0.05:saturation=1.12:gamma=0.88,"
        "colorbalance=rs=-0.06:gs=0.02:bs=0.12:rh=0.10:gh=-0.02:bh=0.14"
    ),
    "phosphor": (
        "eq=contrast=1.36:brightness=-0.04:saturation=1.40:gamma=0.90,"
        "colorbalance=rs=-0.10:gs=0.08:bs=-0.02:rh=-0.06:gh=0.16:bh=-0.08"
    ),
    "amber": (
        "eq=contrast=1.24:brightness=-0.01:saturation=1.18:gamma=0.96,"
        "colorbalance=rs=0.10:gs=0.02:bs=-0.12:rh=0.20:gh=0.04:bh=-0.14"
    ),
}
ABERRATION = {
    "night": "rgbashift=rh=3:bh=-3",
    "street": "rgbashift=rh=2:bh=-2",
    "game": "rgbashift=rh=3:bh=-3",
    "crt": "rgbashift=rh=3:bh=-3",
    "data": "rgbashift=rh=4:bh=-4",
    "neon": "rgbashift=rh=4:bh=-4",
    "chrome": "rgbashift=rh=3:bh=-3",
    "phosphor": "rgbashift=rh=2:bh=-2",
    "amber": "rgbashift=rh=2:bh=-2",
}
# Display-resolution scanlines. Commas inside geq are escaped for the filtergraph.
SCAN = {
    "game": "geq=lum='lum(X\\,Y)*(0.84+0.16*eq(mod(Y\\,3)\\,0))':cb='cb(X\\,Y)':cr='cr(X\\,Y)'",
    "crt": "geq=lum='lum(X\\,Y)*(0.78+0.22*eq(mod(Y\\,3)\\,0))':cb='cb(X\\,Y)':cr='cr(X\\,Y)'",
    "phosphor": "geq=lum='lum(X\\,Y)*(0.86+0.14*eq(mod(Y\\,2)\\,0))':cb='cb(X\\,Y)':cr='cr(X\\,Y)'",
}


def run(cmd: list[str]) -> None:
    done = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if done.returncode != 0:
        tail = done.stderr.decode(errors="replace")[-2500:]
        raise SystemExit(f"command failed:\n{' '.join(cmd[:8])}\n{tail}")


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
    if shot.get("void") == "white":
        # A blown-out studio background drops to black. The object stays.
        parts.append("format=rgb24")
        parts.append(
            "geq="
            "r='if(gt(r(X\\,Y)\\,236)*gt(g(X\\,Y)\\,236)*gt(b(X\\,Y)\\,236)\\,0\\,r(X\\,Y))':"
            "g='if(gt(r(X\\,Y)\\,236)*gt(g(X\\,Y)\\,236)*gt(b(X\\,Y)\\,236)\\,0\\,g(X\\,Y))':"
            "b='if(gt(r(X\\,Y)\\,236)*gt(g(X\\,Y)\\,236)*gt(b(X\\,Y)\\,236)\\,0\\,b(X\\,Y))'"
        )
    parts.append(GRADES[grade])
    parts.append(f"scale={box_w}:{box_h}:force_original_aspect_ratio=increase")
    parts.append(
        "crop=1280:720:"
        f"x='trunc((in_w-out_w)*({bias_x:.4f}+{drift:.4f}*t/{length:.3f})/2)*2':"
        f"y='trunc((in_h-out_h)*{bias_y:.4f}/2)*2'"
    )
    parts.append("unsharp=5:5:0.45:5:5:0.0")
    if grade in ABERRATION:
        parts.append(ABERRATION[grade])
    if grade in SCAN:
        parts.append(SCAN[grade])
    parts.append("vignette=PI/5")
    parts.append(f"trim=duration={length:.3f}")
    parts.append("setpts=PTS-STARTPTS")
    if shot.get("fade_in"):
        parts.append(f"fade=t=in:st=0:d={float(shot['fade_in']):.3f}:color=black")
    if shot.get("fade_out"):
        fade = float(shot["fade_out"])
        parts.append(f"fade=t=out:st={length - fade:.3f}:d={fade:.3f}:color=black")
    parts.append("noise=alls=5:allf=t")
    parts.append("format=yuv420p")
    parts.append("setsar=1")
    return ",".join(parts)


def render_plate(footage: list[dict], shot: dict, grade: str, dest: Path, frames: int | None = None) -> None:
    src = download(next(item for item in footage if item["id"] == shot["footage"]))
    cmd = [
        "ffmpeg", "-y", "-i", str(src),
        "-vf", plate_filter(shot, grade),
        "-an", "-r", str(FPS),
    ]
    if frames:
        cmd += ["-frames:v", str(frames)]
        cmd += ["-q:v", "3", str(dest)]
    else:
        cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", str(dest)]
    run(cmd)


def check_timeline(film: dict) -> float:
    footage = {item["id"]: item for item in film["footage"]}
    total = 0.0
    for shot in film["shots"]:
        length = float(shot["length"])
        if abs(length / 3 - round(length / 3)) > 1e-6:
            raise SystemExit(f"{film['id']} {shot['id']} is off the 3-second bar")
        speed = float(shot.get("speed", 1))
        need = float(shot["start"]) + length * speed + 0.15
        src = footage[shot["footage"]]
        if need > float(src["duration"]) + 0.05:
            raise SystemExit(
                f"{film['id']} {shot['id']} needs {need:.2f}s of {shot['footage']} "
                f"but the rush is {src['duration']}s"
            )
        total += length
    if abs(total - 90) > 0.01:
        raise SystemExit(f"{film['id']} timeline is {total}s, want 90")
    return total


def render_film(film: dict, proof: bool = False) -> None:
    check_timeline(film)
    root: Path = film["root"]
    work = root / "work"
    work.mkdir(parents=True, exist_ok=True)
    if proof:
        wanted = set(film.get("proof", [film["shots"][0]["id"]]))
        for shot in film["shots"]:
            if shot["id"] not in wanted:
                continue
            dest = Path(f"/tmp/proof-{film['id']}-{shot['id']}.jpg")
            print(f"proof {film['id']} {shot['id']}")
            render_plate(film["footage"], shot, shot["grade"], dest, frames=1)
        return

    segments = []
    for shot in film["shots"]:
        dest = work / f"{shot['id']}.mp4"
        print(f"{film['id']} {shot['id']} ({shot['length']}s)")
        render_plate(film["footage"], shot, shot["grade"], dest)
        segments.append(dest)

    listing = work / "concat.txt"
    listing.write_text("".join(f"file '{path}'\n" for path in segments))
    silent = work / "picture.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(silent)])

    score = work / "score.wav"
    print(f"{film['id']} score")
    write_score(score, 90.0, film["score"])

    title = title_filter(film["title"], film["title_colors"])
    out = root / film["file"]
    print(f"{film['id']} master")
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
    poster = root / "poster.jpg"
    run([
        "ffmpeg", "-y", "-ss", str(film["poster"]), "-i", str(out),
        "-frames:v", "1", "-q:v", "3", str(poster),
    ])
    probed = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(out),
    ])
    actual = float(probed.strip())
    write_cut_js(film, actual)
    write_page(film)
    print(f"wrote {out.relative_to(root.parent)} {actual:.2f}s {out.stat().st_size / 1e6:.1f}MB")


def title_filter(text: str, colors: tuple[str, str]) -> str:
    alpha = (
        "alpha='if(lt(t\\,7.2)\\,0\\,if(lt(t\\,8.1)\\,(t-7.2)/0.9\\,"
        "if(lt(t\\,11.4)\\,1\\,if(lt(t\\,12.4)\\,(12.4-t)/1.0\\,0))))'"
    )
    size = 34 if len(text) <= 6 else 28

    def layer(color: str, dx: int) -> str:
        return (
            f"drawtext=fontfile={FONT}:text='{text}':fontsize={size}:"
            f"fontcolor={color}:x=(w-text_w)/2{dx:+d}:y=h*0.78:{alpha}"
        )

    cyan, magenta = colors
    return ",".join([
        layer(f"{cyan}@0.9", -4),
        layer(f"{magenta}@0.75", 4),
        layer("white@0.96", 0),
    ])


def write_score(path: Path, duration: float, spec: dict) -> None:
    n = int(duration * SR)
    left = array.array("f", [0.0]) * n
    right = array.array("f", [0.0]) * n
    bpm = float(spec.get("bpm", 80))
    beat = 60 / bpm
    kind = spec.get("kind", "sine")

    drones = spec["drones"]
    for i in range(n):
        t = i / SR
        trem = 0.84 + 0.16 * math.sin(2 * math.pi * spec.get("trem", 0.08) * t)
        acc = 0.0
        for freq, amp in drones:
            acc += amp * trem * math.sin(2 * math.pi * freq * i / SR)
        left[i] += acc
        right[i] += acc

    def pulse(freq, t0, dur, amp, decay, pan):
        n0 = int(t0 * SR)
        n1 = min(n, int((t0 + dur) * SR))
        for i in range(max(0, n0), n1):
            tt = (i - n0) / SR
            sample = amp * math.exp(-tt / decay) * math.sin(2 * math.pi * freq * i / SR)
            left[i] += sample * (1 - pan)
            right[i] += sample * pan

    heart_hz = float(spec.get("heart", 48))
    t = 0.0
    while t < duration - 0.05:
        accent = 0.30 if (round(t / beat) % 4 in (0, 2)) else 0.18
        if t > duration - 6:
            accent *= 0.5
        pulse(heart_hz, t, 0.26, accent, 0.05, 0.5)
        if spec.get("tick") and t < duration - 6:
            pulse(spec["tick"], t, 0.012, spec.get("tick_amp", 0.04), 0.004, 0.7)
            if spec.get("rain"):
                pulse(spec["tick"] * 1.5, t + 0.05, 0.01, 0.02, 0.003, 0.3)
        if spec.get("hat") and spec["hat"][0] <= t < duration - 6:
            pulse(spec["hat"][1], t + beat * 0.5, 0.06, 0.028, 0.018, 0.35)
        t += beat

    tones = spec["tones"]
    enter = float(spec.get("enter", 18))
    step_beats = float(spec.get("step", 1))
    amp0 = float(spec.get("amp", 0.07))

    def voice(freq, t0, dur, amp, pan):
        n0 = int(t0 * SR)
        n1 = min(n, int((t0 + dur) * SR))
        attack, release = 0.02, min(0.18, dur * 0.4)
        for i in range(max(0, n0), n1):
            tt = (i - n0) / SR
            if tt < attack:
                env = tt / attack
            elif tt > dur - release:
                env = max(0.0, (dur - tt) / release)
            else:
                env = 1.0
            phase = 2 * math.pi * freq * i / SR
            if kind == "chip":
                body = math.sin(phase) + 0.38 * math.sin(3 * phase) + 0.14 * math.sin(5 * phase)
            elif kind == "glow":
                body = math.sin(phase) + 0.08 * math.sin(2 * phase)
            else:
                body = math.sin(phase) + 0.18 * math.sin(2 * phase)
            sample = amp * env * body
            left[i] += sample * (1 - pan)
            right[i] += sample * pan

    k = 0
    t0 = enter
    while t0 < duration - 4:
        freq = tones[k % len(tones)]
        dur = beat * step_beats * 0.92
        amp = amp0 * (0.55 if t0 > duration - 18 else 1)
        voice(freq, t0, dur, amp, 0.36)
        voice(freq * 1.003, t0, dur, amp * 0.65, 0.64)
        k += 1
        t0 += beat * step_beats

    peak = 1e-6
    for i in range(n):
        t = i / SR
        if t < 1.0:
            gain = t / 1.0
        elif t > duration - 3.2:
            gain = max(0.0, (duration - t) / 3.2)
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


def write_cut_js(film: dict, duration: float) -> None:
    used = []
    seen = set()
    for shot in film["shots"]:
        if shot["footage"] not in seen:
            seen.add(shot["footage"])
            used.append(next(item for item in film["footage"] if item["id"] == shot["footage"]))
    credits = [{
        "title": "Original score",
        "author": "written for this film",
        "license": "CC BY-SA 4.0",
        "url": "https://creativecommons.org/licenses/by-sa/4.0",
    }]
    for item in used:
        credits.append({
            "title": item["what"],
            "author": item["author"],
            "license": item["license"],
            "url": item["page"],
        })
    payload = {
        "title": film["title"],
        "theme": film["theme"],
        "file": film["file"],
        "poster": "poster.jpg",
        "durationSeconds": round(duration, 2),
        "targetSeconds": 90,
        "sample": True,
        "movement": film["kicker"],
        "movementTitle": film["line"],
        "version": 1,
        "rendered": "2026-11-22",
        "filmLicense": "CC BY-SA 4.0",
        "credits": credits,
    }
    text = "window.CUT = " + json.dumps(payload, indent=2) + ";\n"
    (film["root"] / "cut.js").write_text(text)


def write_page(film: dict) -> None:
    accent = film["accent"]
    glow = film["glow"]
    links = []
    for slug, label in PAGES:
        href = "../index.html" if slug == "essence" else f"../{slug}/"
        if slug == film["id"]:
            links.append(f'<a href="{href}" aria-current="page">{label}</a>')
        else:
            links.append(f'<a href="{href}">{label}</a>')
    nav = "\n      ".join(links)
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{film["title"]} — {film["theme"]}</title>
  <meta name="description" content="{film["title"]}, a 90-second sample. {film["theme"]}.">
  <style>
    :root {{
      --bg: #07080c;
      --paper: #e7f4f3;
      --dim: #8aa4aa;
      --amber: {accent};
      --line: #1c2430;
    }}
    * {{ box-sizing: border-box; }}
    html {{ color-scheme: dark; }}
    body {{
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(900px 420px at 50% -10%, {glow}, transparent 60%),
        radial-gradient(700px 380px at 80% 120%, rgba(255, 43, 214, 0.07), transparent 55%),
        var(--bg);
      color: var(--paper);
      font-family: "Iowan Old Style", Palatino, Georgia, serif;
    }}
    main {{
      width: min(960px, calc(100% - 32px));
      margin: 0 auto;
      padding: 48px 0 72px;
    }}
    .samples {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px 14px;
      margin: 0 0 22px;
      font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
      font-size: 11px;
      letter-spacing: 0.16em;
    }}
    .samples a {{ color: var(--dim); text-decoration: none; }}
    .samples a[aria-current="page"] {{ color: var(--amber); }}
    .kicker {{
      margin: 0 0 18px;
      font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
      font-size: 11px;
      letter-spacing: 0.22em;
      text-transform: uppercase;
      color: var(--dim);
    }}
    h1 {{
      margin: 0;
      font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
      font-weight: 650;
      font-size: clamp(2.2rem, 7vw, 3.8rem);
      letter-spacing: 0.16em;
      line-height: 1;
    }}
    .theme {{
      margin: 14px 0 28px;
      color: var(--dim);
      font-style: italic;
      font-size: 1.05rem;
    }}
    video {{
      display: block;
      width: 100%;
      background: #000;
      border: 1px solid var(--line);
    }}
    .meter {{ margin-top: 18px; }}
    .meter-labels {{
      display: flex;
      justify-content: space-between;
      font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
      font-size: 12px;
      letter-spacing: 0.08em;
      color: var(--dim);
    }}
    .track {{ margin-top: 8px; height: 2px; background: #2a2724; }}
    .fill {{ height: 100%; width: 100%; background: var(--amber); }}
    .movement {{ margin: 14px 0 0; font-size: 1rem; }}
    .note {{
      margin: 10px 0 0;
      color: var(--dim);
      font-size: 0.95rem;
      line-height: 1.45;
    }}
    details {{ margin-top: 28px; }}
    summary {{
      cursor: pointer;
      color: var(--dim);
      font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
      font-size: 12px;
      letter-spacing: 0.14em;
      text-transform: uppercase;
    }}
    ul {{ list-style: none; padding: 0; margin: 16px 0 0; }}
    li {{ margin: 0 0 12px; line-height: 1.4; }}
    li a {{ color: var(--paper); }}
    .lic {{ color: var(--dim); }}
    .fine {{ color: var(--dim); font-size: 0.92rem; line-height: 1.5; }}
  </style>
</head>
<body>
  <main>
    <nav class="samples" aria-label="Samples">
      {nav}
    </nav>
    <p class="kicker">{film["kicker"]}</p>
    <h1>{film["title"]}</h1>
    <p class="theme">{film["theme"]}</p>
    <video controls playsinline preload="metadata" poster="poster.jpg" aria-label="{film["title"]}, a 90-second sample">
      <source src="{film["file"]}" type="video/mp4">
    </video>
    <div class="meter" aria-hidden="true">
      <div class="meter-labels"><span id="now">1:30</span><span>sample</span></div>
      <div class="track"><div class="fill" id="fill"></div></div>
    </div>
    <p class="movement" id="movement">{film["line"]}</p>
    <p class="note">Open footage, recut, with a score written for the picture. A finished minute and a half.</p>
    <details>
      <summary>Footage and score</summary>
      <ul id="credits"></ul>
      <p class="fine" id="fine"></p>
    </details>
  </main>
  <script src="cut.js"></script>
  <script>
    (function () {{
      var cut = window.CUT;
      if (!cut) return;
      function clock(seconds) {{
        seconds = Math.round(seconds);
        return Math.floor(seconds / 60) + ":" + String(seconds % 60).padStart(2, "0");
      }}
      document.getElementById("now").textContent = clock(cut.durationSeconds);
      var list = document.getElementById("credits");
      (cut.credits || []).forEach(function (item) {{
        var li = document.createElement("li");
        var link = document.createElement("a");
        link.href = item.url;
        link.textContent = item.title;
        li.appendChild(link);
        li.appendChild(document.createTextNode(" — " + item.author + " "));
        var lic = document.createElement("span");
        lic.className = "lic";
        lic.textContent = item.license;
        li.appendChild(lic);
        list.appendChild(li);
      }});
      document.getElementById("fine").textContent =
        "Picture only was taken from the footage. None of the original sound is in the film. The video file is " +
        cut.filmLicense + " because some of the footage is share-alike. This page is part of DailyOpenCut.";
    }})();
  </script>
</body>
</html>
"""
    (film["root"] / "index.html").write_text(page)


PAGES = (
    ("essence", "ESSENCE"),
    ("kowloon", "KOWLOON"),
    ("ninety", "NINETY"),
    ("chrome", "CHROME"),
    ("phosphor", "PHOSPHOR"),
)
