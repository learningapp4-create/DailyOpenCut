#!/usr/bin/env python3
"""Cut four 90-second samples beside ESSENCE.

    python3 build_samples.py            # all four
    python3 build_samples.py kowloon    # one film
    python3 build_samples.py --proof    # one frame of the proof shots

Each film is its own page. The score is original. ESSENCE is not touched.
"""

from __future__ import annotations

import sys
from pathlib import Path

from studio import render_film

ROOT = Path(__file__).resolve().parent
BY = "https://creativecommons.org/licenses/by/3.0"
BY4 = "https://creativecommons.org/licenses/by/4.0"
SA2 = "https://creativecommons.org/licenses/by-sa/2.0"
SA4 = "https://creativecommons.org/licenses/by-sa/4.0"
CC0 = "https://creativecommons.org/publicdomain/zero/1.0/"


def clip(id_, file, url, author, license, license_url, what, duration):
    page = "https://commons.wikimedia.org/wiki/File:" + url.rsplit("/", 1)[-1]
    return {
        "id": id_,
        "file": file,
        "url": url,
        "page": page,
        "author": author,
        "license": license,
        "licenseUrl": license_url,
        "what": what,
        "duration": duration,
    }


FOOTAGE = [
    clip("skyline", "skyline.webm",
         "https://upload.wikimedia.org/wikipedia/commons/f/f5/Hong_Kong_Skyline_at_Night.webm",
         "andrew_annemarie (Trekking Asia)", "CC BY-SA 2.0", SA2,
         "Hong Kong skyline at night, Victoria Harbour", 93.17),
    clip("ssprain", "ssprain.webm",
         "https://upload.wikimedia.org/wikipedia/commons/3/36/Rainy_night_in_Sham_Shui_Po.webm",
         "Andy Li", "CC0", CC0,
         "Rainy night in Sham Shui Po", 6.1),
    clip("hunghom", "hunghom.webm",
         "https://upload.wikimedia.org/wikipedia/commons/5/58/A_SP1900_train_enters_Hung_Hom_Station_on_June_19%2C_2021.webm",
         "IamCristYe", "CC BY-SA 4.0", SA4,
         "A train enters Hung Hom station", 24.9),
    clip("vespero", "vespero.webm",
         "https://upload.wikimedia.org/wikipedia/commons/1/1d/Vespero_en_Hong_Kong_Island_%282014%29_02.webm",
         "RG72", "CC BY-SA 4.0", SA4,
         "Evening on Hong Kong Island", 10.62),
    clip("tunnel", "tunnel.webm",
         "https://upload.wikimedia.org/wikipedia/commons/0/00/West_Rail_Line_Trains_in_Tunnel_Seen_at_new_Entrance_of_TML_to_Hung_Hom_Station.webm",
         "IamCristYe", "CC BY-SA 4.0", SA4,
         "Tracks into Hung Hom at night", 77.42),
    clip("amiga", "amiga.webm",
         "https://upload.wikimedia.org/wikipedia/commons/d/d3/Genesis_fractal_landscape_software_%28Commodore_Amiga%29.webm",
         "Morn", "CC0", CC0,
         "Genesis fractal landscape on a Commodore Amiga", 21.83),
    clip("fiber", "fiber.webm",
         "https://upload.wikimedia.org/wikipedia/commons/7/77/Fiber_Optic_Filament_Tips_%28Free_to_Use_Stock_Video_Footage%29.webm",
         "Jeffrey Beach", "CC BY 3.0", BY,
         "Fiber-optic filament tips", 59.52),
    clip("vhsio", "vhsio.webm",
         "https://upload.wikimedia.org/wikipedia/commons/6/6c/VHS_in%2C_autoplay%2C_VHS_out.webm",
         "MisterSanderson", "CC BY-SA 4.0", SA4,
         "A VHS deck taking a tape", 59.56),
    clip("floppy525", "floppy525.webm",
         "https://upload.wikimedia.org/wikipedia/commons/7/79/5.25_Inch_Floppy_Disks.webm",
         "Maximilian Schönherr", "CC BY-SA 4.0", SA4,
         "A hand on a stack of 5.25 inch disks", 39.07),
    clip("dat", "dat.webm",
         "https://upload.wikimedia.org/wikipedia/commons/b/bb/Sony_DAT_Walkman_TCD-D7_%281993%29.webm",
         "Maximilian Schönherr", "CC BY-SA 4.0", SA4,
         "Sony DAT Walkman TCD-D7, 1993", 55.08),
    clip("cassettes", "cassettes.webm",
         "https://upload.wikimedia.org/wikipedia/commons/9/9a/Two_Compact_Cassettes_%281960s%29.webm",
         "Maximilian Schönherr", "CC BY-SA 4.0", SA4,
         "Two compact cassettes from the 1960s", 28.0),
    clip("gameboy", "gameboy.webm",
         "https://upload.wikimedia.org/wikipedia/commons/1/11/Nintendo_Gameboy_I.webm",
         "Maximilian Schönherr", "CC BY-SA 4.0", SA4,
         "Nintendo Game Boy, screen blank", 37.0),
    clip("fitz", "fitz.webm",
         "https://upload.wikimedia.org/wikipedia/commons/8/8d/Fitzgeralds_sign_-_Neon_Museum_-_Sarah_Stierch_2019.webm",
         "Sarah Stierch", "CC BY 4.0", BY4,
         "Fitzgeralds neon sign", 5.05),
    clip("binion", "binion.webm",
         "https://upload.wikimedia.org/wikipedia/commons/f/f8/Binion%27s_horseshoe_sign_video_-_Sarah_Stierch_2019.webm",
         "Sarah Stierch", "CC BY 4.0", BY4,
         "Binion's horseshoe, a field of bulbs", 3.82),
    clip("brilliance", "brilliance.webm",
         "https://upload.wikimedia.org/wikipedia/commons/2/21/Brilliance_at_Neon_Museum_2019_1_-_Sarah_Stierch.webm",
         "Sarah Stierch", "CC BY 4.0", BY4,
         "Neon boneyard, Famous and Golden Nugget", 2.43),
    clip("walkman", "walkman.webm",
         "https://upload.wikimedia.org/wikipedia/commons/1/15/Sony_Cassette_Walkman_II_WM-2_%281981%29.webm",
         "Maximilian Schönherr", "CC BY-SA 4.0", SA4,
         "A hand opening a Sony Walkman WM-2, 1981", 24.07),
    clip("bridge", "bridge.webm",
         "https://upload.wikimedia.org/wikipedia/commons/4/4d/Traffic_on_bridge_at_night.webm",
         "Editor", "CC BY 3.0", BY,
         "Traffic on a bridge at night", 40.54),
    clip("citynight", "citynight.webm",
         "https://upload.wikimedia.org/wikipedia/commons/c/cd/City_at_night.webm",
         "Editor", "CC BY 3.0", BY,
         "A city at night, from above", 29.07),
    clip("c64", "c64.webm",
         "https://upload.wikimedia.org/wikipedia/commons/d/de/Commodore_64_Home_Computer_%281983%29.webm",
         "Maximilian Schönherr", "CC BY-SA 4.0", SA4,
         "Commodore 64, 1983", 91.75),
    clip("scope60", "scope60.webm",
         "https://upload.wikimedia.org/wikipedia/commons/b/bf/Video_of_warm-up_process_of_soviet_tube_oscilloscope_from_1963_-_%D0%9E%D1%81%D1%86%D0%B8%D0%BB%D0%BE%D0%B3%D1%80%D0%B0%D1%84_%D0%A11-5.webm",
         "Сарапулов", "CC BY 4.0", BY4,
         "Soviet tube oscilloscope С1-5, 1963, warming up", 100.3),
    clip("diskpack", "diskpack.webm",
         "https://upload.wikimedia.org/wikipedia/commons/c/cd/Loading_and_Unloading_a_Disk_Pack_%28CelGenStudios%29.webm",
         "CelGenStudios", "CC BY 3.0", BY,
         "Loading a disk pack", 63.62),
    clip("teletype", "teletype.webm",
         "https://upload.wikimedia.org/wikipedia/commons/8/8b/The_electric_teleprinter_Automatik_Lo_133.webm",
         "Konrad Gutkowski", "CC BY 3.0", BY,
         "Lorenz teleprinter Automatik Lo 133", 9.26),
    clip("cathode", "cathode.webm",
         "https://upload.wikimedia.org/wikipedia/commons/4/42/Cathde_Ray_being_deflected.webm",
         "Luís Silva", "CC BY 3.0", BY,
         "A cathode ray bending in a tube", 21.48),
    clip("philips", "philips.webm",
         "https://upload.wikimedia.org/wikipedia/commons/d/dd/Philips_Compact_Cassette_%281960s%29.webm",
         "Maximilian Schönherr", "CC BY-SA 4.0", SA4,
         "Philips compact cassette, 1960s", 64.8),
]
BY_ID = {item["id"]: item for item in FOOTAGE}


def take(*ids: str) -> list[dict]:
    return [BY_ID[i] for i in ids]


AMIGA = "1426:1074:252:0"

FILMS = [
    {
        "id": "kowloon",
        "title": "KOWLOON",
        "theme": "Hong Kong, rain on the glass",
        "kicker": "MV / 002",
        "line": "the harbor keeps the lights on",
        "file": "kowloon.mp4",
        "poster": 14,
        "accent": "#5ce1e6",
        "glow": "rgba(92, 225, 230, 0.14)",
        "title_colors": ("0x5CE1E6", "0xFF2BD6"),
        "proof": ["magenta"],
        "score": {
            "drones": [(73.42, 0.030), (110.00, 0.016)],
            "tick": 1900, "tick_amp": 0.035, "rain": True,
            "heart": 46, "kind": "sine", "trem": 0.06,
            "hat": (12, 740),
            "tones": [293.66, 349.23, 392.00, 440.00, 523.25, 440.00, 392.00, 349.23],
            "enter": 12, "step": 1, "amp": 0.060,
        },
        "footage": take("skyline", "ssprain", "hunghom", "vespero", "tunnel"),
        "shots": [
            dict(id="open", footage="skyline", start=12, length=6, grade="night", x=0.55, y=0.42, drift=0.04, punch=180, fade_in=0.8),
            dict(id="sign", footage="ssprain", start=0.2, length=3, grade="night", x=0.30, y=0.36, punch=240),
            dict(id="magenta", footage="skyline", start=36, length=6, grade="night", x=0.48, y=0.40, drift=-0.05, punch=200),
            dict(id="train", footage="hunghom", start=3, length=3, grade="night", x=0.55, y=0.46, punch=260),
            dict(id="lane", footage="vespero", start=0.4, length=6, grade="street", x=0.50, y=0.18, punch=60),
            dict(id="windows", footage="ssprain", start=2.2, length=3, grade="night", x=0.78, y=0.28, punch=280),
            dict(id="towers", footage="skyline", start=68, length=6, grade="night", x=0.42, y=0.46, drift=0.05, punch=160),
            dict(id="whip", footage="skyline", start=50, length=3, grade="night", x=0.50, y=0.45, punch=80),
            dict(id="tracks", footage="tunnel", start=6, length=6, grade="night", x=0.50, y=0.42, drift=0.04, punch=220),
            dict(id="doors", footage="hunghom", start=11, length=3, grade="night", x=0.40, y=0.48, punch=300),
            dict(id="lane2", footage="vespero", start=3.2, length=6, grade="street", x=0.48, y=0.14, drift=0.03, punch=80),
            dict(id="rain", footage="ssprain", start=0.4, length=3, grade="street", x=0.34, y=0.62, punch=320),
            dict(id="ferry", footage="skyline", start=18, length=6, grade="night", x=0.28, y=0.62, punch=240),
            dict(id="platform", footage="hunghom", start=6, length=6, grade="night", x=0.62, y=0.40, drift=-0.04, punch=240),
            dict(id="return", footage="skyline", start=36, length=6, grade="night", x=0.60, y=0.38, punch=220),
            dict(id="late", footage="skyline", start=80, length=6, grade="night", x=0.46, y=0.44, punch=150),
            dict(id="yard", footage="tunnel", start=22, length=6, grade="night", x=0.55, y=0.36, drift=-0.03, punch=260),
            dict(id="hold", footage="skyline", start=72, length=6, grade="night", x=0.50, y=0.42, punch=140, fade_out=2.2),
        ],
    },
    {
        "id": "ninety",
        "title": "NINETY",
        "theme": "a game still running",
        "kicker": "MV / 003",
        "line": "nineteen ninety, the cartridge is warm",
        "file": "ninety.mp4",
        "poster": 4,
        "accent": "#c6f54a",
        "glow": "rgba(198, 245, 74, 0.12)",
        "title_colors": ("0xC6F54A", "0x5CE1E6"),
        "proof": ["close", "hand"],
        "score": {
            "drones": [(55.00, 0.022), (110.00, 0.012)],
            "tick": 1480, "tick_amp": 0.04,
            "heart": 64, "kind": "chip", "trem": 0.11,
            "hat": (6, 1860),
            "tones": [440.00, 523.25, 587.33, 659.25, 783.99, 659.25, 587.33, 523.25],
            "enter": 6, "step": 0.5, "amp": 0.042,
        },
        "footage": take("amiga", "fiber", "vhsio", "floppy525", "dat", "cassettes", "gameboy"),
        "shots": [
            dict(id="world", footage="amiga", start=10, length=6, grade="game", precrop=AMIGA, x=0.50, y=0.58, punch=40, fade_in=0.6),
            dict(id="close", footage="amiga", start=14.5, length=6, grade="game", precrop=AMIGA, x=0.50, y=0.64, punch=80),
            dict(id="spark", footage="fiber", start=6, length=3, grade="data", x=0.50, y=0.74, punch=180),
            dict(id="field", footage="fiber", start=24, length=6, grade="data", x=0.48, y=0.78, drift=0.04, punch=160),
            dict(id="deck", footage="vhsio", start=2, length=3, grade="crt", x=0.55, y=0.48, punch=460),
            dict(id="heads", footage="vhsio", start=18, length=6, grade="crt", x=0.62, y=0.42, drift=-0.03, punch=500),
            dict(id="hand", footage="floppy525", start=15, length=6, grade="human", x=0.55, y=0.48, punch=220),
            dict(id="dat", footage="dat", start=8, length=3, grade="crt", x=0.52, y=0.48, punch=620),
            dict(id="tape", footage="cassettes", start=2, length=3, grade="crt", x=0.70, y=0.50, punch=180),
            dict(id="boy", footage="gameboy", start=1.2, length=6, grade="crt", void="white", x=0.50, y=0.46, punch=200),
            dict(id="fly", footage="amiga", start=8, length=6, grade="game", precrop=AMIGA, x=0.46, y=0.52, drift=0.04, punch=30),
            dict(id="green", footage="fiber", start=40, length=6, grade="data", x=0.52, y=0.70, punch=200),
            dict(id="spool", footage="vhsio", start=32, length=6, grade="crt", x=0.40, y=0.50, punch=380),
            dict(id="load", footage="floppy525", start=18, length=6, grade="human", x=0.42, y=0.55, punch=280),
            dict(id="relic", footage="gameboy", start=16, length=6, grade="crt", void="white", x=0.55, y=0.42, drift=0.03, punch=240),
            dict(id="net", footage="fiber", start=48, length=6, grade="data", x=0.50, y=0.72, punch=220),
            dict(id="end", footage="amiga", start=11, length=6, grade="game", precrop=AMIGA, x=0.50, y=0.60, punch=20, fade_out=2.2),
        ],
    },
    {
        "id": "chrome",
        "title": "CHROME",
        "theme": "nineteen eighty, neon and a hand",
        "kicker": "MV / 004",
        "line": "the sign comes on before the street does",
        "file": "chrome.mp4",
        "poster": 4,
        "accent": "#ff4ad8",
        "glow": "rgba(255, 43, 214, 0.14)",
        "title_colors": ("0xFF2BD6", "0x5CE1E6"),
        "proof": ["fitz2"],
        "score": {
            "drones": [(82.41, 0.028), (123.47, 0.014)],
            "tick": 2400, "tick_amp": 0.038,
            "heart": 55, "kind": "sine", "trem": 0.09,
            "hat": (9, 980),
            "tones": [329.63, 392.00, 493.88, 659.25, 493.88, 392.00, 329.63, 493.88],
            "enter": 9, "step": 1, "amp": 0.062,
        },
        "footage": take("fitz", "binion", "brilliance", "walkman", "floppy525", "bridge", "citynight", "c64"),
        "shots": [
            dict(id="fitz", footage="fitz", start=0.2, length=3, grade="neon", x=0.42, y=0.50, punch=140, fade_in=0.5),
            dict(id="fitz2", footage="fitz", start=1.3, length=3, grade="neon", x=0.64, y=0.42, punch=200),
            dict(id="bulbs", footage="binion", start=0.15, length=3, grade="neon", x=0.50, y=0.42, punch=20),
            dict(id="nugget", footage="brilliance", start=0.04, length=3, speed=0.70, grade="neon", x=0.55, y=0.46, punch=160),
            dict(id="hand", footage="walkman", start=1.0, length=6, grade="human", x=0.50, y=0.42, punch=340),
            dict(id="deck", footage="walkman", start=8.0, length=6, grade="chrome", x=0.48, y=0.46, punch=400),
            dict(id="disks", footage="floppy525", start=14, length=6, grade="human", x=0.58, y=0.40, punch=280),
            dict(id="bridge", footage="bridge", start=2, length=6, grade="night", x=0.50, y=0.55, drift=0.03, punch=140),
            dict(id="bridge2", footage="bridge", start=16, length=6, grade="night", x=0.48, y=0.48, punch=180),
            dict(id="city", footage="citynight", start=2, length=6, grade="night", x=0.45, y=0.50, drift=0.04, punch=120),
            dict(id="power", footage="c64", start=32, length=6, grade="chrome", x=0.52, y=0.48, punch=260),
            dict(id="keys", footage="c64", start=14, length=3, grade="chrome", x=0.50, y=0.68, punch=420),
            dict(id="fitz3", footage="fitz", start=0.5, length=3, speed=1.1, grade="neon", x=0.38, y=0.55, punch=160),
            dict(id="bulbs2", footage="binion", start=0.25, length=3, grade="neon", x=0.50, y=0.62, punch=40),
            dict(id="lid", footage="walkman", start=14, length=6, grade="human", x=0.52, y=0.40, punch=360),
            dict(id="road", footage="bridge", start=26, length=6, grade="night", x=0.50, y=0.60, punch=160),
            dict(id="grid", footage="citynight", start=12, length=6, grade="night", x=0.58, y=0.42, punch=160),
            dict(id="whip", footage="citynight", start=22, length=3, grade="night", x=0.50, y=0.48, punch=80),
            dict(id="stack", footage="floppy525", start=22, length=6, grade="human", x=0.44, y=0.50, punch=240, fade_out=2.2),
        ],
    },
    {
        "id": "phosphor",
        "title": "PHOSPHOR",
        "theme": "the tube draws the night",
        "kicker": "MV / 005",
        "line": "seventies, a trace still moving on the glass",
        "file": "phosphor.mp4",
        "poster": 3,
        "accent": "#ffb020",
        "glow": "rgba(140, 255, 90, 0.10)",
        "title_colors": ("0xB6FF4A", "0xFFB020"),
        "proof": ["trace2"],
        "score": {
            "drones": [(65.41, 0.032), (98.00, 0.012)],
            "heart": 40, "kind": "glow", "trem": 0.05,
            "tones": [261.63, 293.66, 349.23, 392.00, 440.00, 392.00, 349.23, 293.66],
            "enter": 15, "step": 2, "amp": 0.055,
        },
        "footage": take("scope60", "diskpack", "teletype", "philips", "cassettes"),
        "shots": [
            dict(id="trace", footage="scope60", start=26, length=6, grade="phosphor", precrop="1000:900:460:80", x=0.50, y=0.50, punch=80, fade_in=0.7),
            dict(id="trace2", footage="scope60", start=24, length=3, grade="phosphor", precrop="1000:900:460:80", x=0.50, y=0.50, punch=40),
            dict(id="platter", footage="diskpack", start=1.0, length=6, grade="amber", x=0.40, y=0.46, punch=180),
            dict(id="lamps", footage="diskpack", start=14, length=6, grade="amber", x=0.55, y=0.64, punch=220),
            dict(id="lorenz", footage="teletype", start=0.4, length=6, grade="amber", x=0.62, y=0.48, punch=140),
            dict(id="key", footage="teletype", start=2.8, length=3, grade="amber", x=0.55, y=0.64, punch=260),
            dict(id="tape", footage="philips", start=6, length=6, grade="amber", x=0.58, y=0.50, punch=180),
            dict(id="pink", footage="cassettes", start=2, length=3, grade="amber", x=0.72, y=0.48, punch=160),
            dict(id="wave", footage="scope60", start=40, length=6, grade="phosphor", precrop="1000:900:460:80", x=0.50, y=0.50, drift=0.02, punch=40),
            dict(id="load", footage="diskpack", start=28, length=6, grade="amber", x=0.38, y=0.42, punch=200),
            dict(id="glass", footage="scope60", start=62, length=6, grade="phosphor", precrop="1000:900:460:80", x=0.48, y=0.50, punch=60),
            dict(id="pack", footage="diskpack", start=36, length=6, grade="amber", x=0.46, y=0.40, punch=180),
            dict(id="paper", footage="teletype", start=1.0, length=3, speed=0.85, grade="amber", x=0.50, y=0.40, punch=160),
            dict(id="trace3", footage="scope60", start=55, length=6, grade="phosphor", precrop="1000:900:460:80", x=0.50, y=0.50, punch=20),
            dict(id="macro", footage="philips", start=30, length=6, grade="amber", x=0.60, y=0.48, punch=220),
            dict(id="spark", footage="scope60", start=78, length=3, grade="phosphor", precrop="1000:900:460:80", x=0.50, y=0.50, punch=30),
            dict(id="lid", footage="diskpack", start=46, length=3, grade="amber", x=0.48, y=0.55, punch=200),
            dict(id="hold", footage="scope60", start=88, length=6, grade="phosphor", precrop="1000:900:460:80", x=0.50, y=0.50, punch=20, fade_out=2.2),
        ],
    },
]


def main() -> None:
    proof = "--proof" in sys.argv
    wanted = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
    films = FILMS
    if wanted:
        films = [film for film in FILMS if film["id"] in wanted]
        if not films:
            raise SystemExit(f"unknown film {wanted}")
    for film in films:
        film["root"] = ROOT / film["id"]
        film["root"].mkdir(exist_ok=True)
        render_film(film, proof=proof)


if __name__ == "__main__":
    main()
