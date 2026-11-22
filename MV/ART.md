# ESSENCE

A music video about the essence of humanity in machines. The finished film is three minutes. Movement I is the cut on the page now.

## Audience

A general YouTube gaming cyberpunk audience, judging the picture only. They decide in the first seconds: crushed black, cyan in the shadows, magenta in the highlights, a small RGB split on machines. Skin stays warm and registered, with no split, so a person still reads as a person. If a new shot looks like a museum or a lecture under that grade, it does not belong. Do not retouch the score when the picture changes.

## Picture

One frame: 1280×720, 24 fps. Hard cuts. Light grain, a soft vignette.

- **Machine** — night city. Cyan shadows, magenta highlights, a 3-pixel RGB split. Gears, the disk arm, the robot’s hands, the open drive.
- **Human** — the hands film, warm skin, no chromatic split. Heat against the neon.
- **Warm** — a person still inside a machine: the press, the thread, the projector. Neon in the metal, warmth on the body, a smaller split.
- **Data** — the pianists’ hands as a HUD. Yellow points on a deep blue grid, a wider split.
- **Machine, remembered** — the watch again, still neon, with the magenta turned up after the hands have been there.

Screen-blend only the hands film over a machine. The black void drops out, so skin sits inside metal. That blend is the sentence of the film. Do not blend arbitrary shots.

The word ESSENCE appears once, early, and leaves. No other type on the picture.

## Time

80 BPM. One bar is 3 seconds. Shot lengths stay on that bar. The grid is the machine. The melody is the human part, and it does not break the grid. It lives in it.

The score is original. Do not lay in a found song. Source audio stays out — some of it is not ours to use, and the pulse has to be one pulse.

## Where the three minutes go

| Time | What it has to do |
| --- | --- |
| 0:00–1:30 | Movement I, on the page. The machine alone, then a hand, then the hand inside the machine. |
| 1:30–2:30 | The human rhythm starts to lead. Clock face, a watch being assembled, closer work of hands in tools. Reprises must change speed, grade, or blend. Do not loop a shot unchanged. |
| 2:30–3:00 | Hold. One image of a hand resting on metal, then black. The tick leaves. The drone remains, then nothing. |

## Footage still waiting

Use these before going hunting, and keep the licenses in `cut.js`:

- Andreas Huber clock, Wien — Furkan Akkurt — CC BY-SA 4.0. Human time. A good door into the second movement.
- *How a Watch Works* (1949) — public domain. Hands assembling a watch. Strip the sound.
- Hettich movement — Christoph Waghubinger — CC BY-SA 4.0.
- EGU CNC milling aluminum — CC BY-SA 3.0. Heavy file. Take a few seconds of metal, not the whole reel.
- Intaglio printing — CC BY-SA 4.0. Hands, ink, plate.

Leave out anything with a burned-in watermark, a speed badge, a talking-head explainer, or a song we did not write. The window robot, the Baxter arms, and the mill are already in. A return has to be a reprise, not a repeat.

## Build

`python3 build.py` from this folder. Rushes download into `rushes/` and are not committed. The page reads `cut.js`, which the build rewrites from the real duration.
