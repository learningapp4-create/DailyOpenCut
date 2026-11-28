# Daily cuts

Ten-second reference edits for OpenCut theme presets. This file is the index. The web app home page plays the cuts. The same list is in the collapsible panel on the left.

Each row is one cut: the theme, the date, what it shows, the footage and its license, and the preset version that was applied.

| Date | Theme | Preset | Shows | Footage | License |
| --- | --- | --- | --- | --- | --- |
| 2026-11-21 | Minimalistic homie | [minimalistic-homie@1.1.0](../presets/themes/minimalistic-homie.jsonc) | A hand lifts a French press and pours coffee into a red mug on a kitchen counter. | [Use of a coffee press](https://commons.wikimedia.org/wiki/File:Use_of_a_coffee_press.ogv) by Daniel Case, videography by his son | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0) |
| 2026-11-21 | Cinematic bars | [cinematic-bars@1.1.0](../presets/themes/cinematic-bars.jsonc) | A drone drifts over morning fog above the village of Vetla, with houses and fields showing through the trees. | [Drone video of foggy Vetla village in Estonia](https://commons.wikimedia.org/wiki/File:Drone_video_of_foggy_Vetla_village_in_Estonia.ogv) by Sillerkiil | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| 2026-11-24 | Indie fashion cute | [indie-fashion-cute@1.1.0](../presets/themes/indie-fashion-cute.jsonc) | A macro lens rests on a yellow rose, and the bloom fills the frame. | [Yellow Rose through a Macro Lens, One](https://commons.wikimedia.org/wiki/File:Yellow_Rose_through_a_Macro_Lens,_One.webm) by Joaquim Baeta | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0) |
| 2026-11-25 | Playful gamer | [playful-gamer@1.1.0](../presets/themes/playful-gamer.jsonc) | Balls run a Wildwasser pinball playfield while the inserts stay lit. | [Pinball-multi-ball](https://commons.wikimedia.org/wiki/File:Pinball-multi-ball.webm) by Myriam Thyes | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| 2026-11-26 | Gen Z ADHD | [genz-adhd@1.0.0](../presets/themes/genz-adhd.jsonc) | A dancer runs the six-step on a studio floor, seen through a fisheye. | [Tutorial breakdance - Six Step](https://commons.wikimedia.org/wiki/File:Tutorial_breakdance_-_Six_Step.webm) by Neil Sweeney | [CC BY 3.0](https://creativecommons.org/licenses/by/3.0) |
| 2026-11-27 | OpenCut editorial | [opencut-editorial@1.0.0](../presets/themes/opencut-editorial.jsonc) | A hand draws a short line with a gel pen on a pink index card. | [Aerra's Films of the Ordinary XII -- Muji Smooth Gel Ink Pen](https://commons.wikimedia.org/wiki/File:Aerra's_Films_of_the_Ordinary_XII_--_Muji_Smooth_Gel_Ink_Pen.webm) by Aerra Carnicom | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| 2026-11-28 | Cinematic bars | [cinematic-bars@1.1.0](../presets/themes/cinematic-bars.jsonc) | A pink sun sits over the sea while swells roll through the last light. | [Ocean surface waves 08](https://commons.wikimedia.org/wiki/File:Ocean_surface_waves_08.ogv) by Mostafameraji | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) |

## 2026-11-21 — Quiet press

A hand lifts a French press and pours coffee into a red mug on a kitchen counter.

The picture is the last 10 seconds of a 68.864 second clip, from 58.5s, played at 1x. Preset `minimalistic-homie` at version `1.1.0`. The first pass covered the mug and crushed the red. The notes for that change are in the preset changelog.

- Preview: [preview.mp4](cuts/2026-11-21-quiet-press/preview.mp4) (derivative, CC BY-SA 3.0)
- Project: [project.json](cuts/2026-11-21-quiet-press/project.json)
- Source file: <https://upload.wikimedia.org/wikipedia/commons/a/a6/Use_of_a_coffee_press.ogv>
- License: [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0)

Re-render from the preset:

```sh
node presets/render-preview.mjs daily/cuts/2026-11-21-quiet-press
```

The preview draws Liberation Serif where the editor would draw Playfair Display. Inter is used as installed. The project still names Playfair Display.

## 2026-11-21 — Fog hold

A drone drifts over morning fog above the village of Vetla, with houses and fields showing through the trees.

The picture is 10 seconds starting at 2s, played at 1x and 24 fps. Preset `cinematic-bars` at version `1.1.0`. The first pass sat the second title line on the lower bar and crushed the fog. The notes for that change are in the preset changelog. The source file has no audio track, so the preview's audio is silence.

- Preview: [preview.mp4](cuts/2026-11-21-fog-hold/preview.mp4) (derivative, CC0 1.0)
- Project: [project.json](cuts/2026-11-21-fog-hold/project.json)
- Source file: <https://upload.wikimedia.org/wikipedia/commons/c/c9/Drone_video_of_foggy_Vetla_village_in_Estonia.ogv>
- License: [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)

Re-render from the preset:

```sh
node presets/render-preview.mjs daily/cuts/2026-11-21-fog-hold
```

The preview draws Liberation Serif where the editor would draw Playfair Display. The project still names Playfair Display.

## 2026-11-24 — Pale rose

A macro lens rests on a yellow rose, and the bloom fills the frame.

The picture is 10 seconds starting at 8s, played at 1x and 24 fps. Preset `indie-fashion-cute` at version `1.1.0`. The first pass left the bloom as a strip in an empty blush frame and washed the yellow. The notes for that change are in the preset changelog. The source audio is a quiet room, kept low.

- Preview: [preview.mp4](cuts/2026-11-24-pale-rose/preview.mp4) (derivative, CC BY 4.0)
- Project: [project.json](cuts/2026-11-24-pale-rose/project.json)
- Source file: <https://upload.wikimedia.org/wikipedia/commons/4/4e/Yellow_Rose_through_a_Macro_Lens%2C_One.webm>
- License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0)

Re-render from the preset:

```sh
node presets/render-preview.mjs daily/cuts/2026-11-24-pale-rose
```

The preview draws Liberation Serif where the editor would draw Playfair Display. The project still names Playfair Display.

## 2026-11-25 — Multi ball

Balls run a Wildwasser pinball playfield while the inserts stay lit.

The picture is 10 seconds starting at 46s, played at 1.05x and 60 fps, so the source used is 10.5 seconds. Preset `playful-gamer` at version `1.1.0`. The first pass parked the acid chip on the lower targets and pushed the orange inserts toward lime. The notes for that change are in the preset changelog. The source audio is the machine in the room, kept under the preset volume.

- Preview: [preview.mp4](cuts/2026-11-25-multi-ball/preview.mp4) (derivative, CC BY-SA 4.0)
- Project: [project.json](cuts/2026-11-25-multi-ball/project.json)
- Source file: <https://upload.wikimedia.org/wikipedia/commons/d/df/Pinball-multi-ball.webm>
- License: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0)

Re-render from the preset:

```sh
node presets/render-preview.mjs daily/cuts/2026-11-25-multi-ball
```

The title is Inter, the same face the preview draws.

## 2026-11-26 — Six step

A dancer runs the six-step on a studio floor, seen through a fisheye.

The picture is 10 seconds starting at 38s, played at 1.12x and 30 fps, so the source used is 11.2 seconds. Preset `genz-adhd` at version `1.0.0`. The source file has no audio track, so the preview's audio is silence.

- Preview: [preview.mp4](cuts/2026-11-26-six-step/preview.mp4) (derivative, CC BY 3.0)
- Project: [project.json](cuts/2026-11-26-six-step/project.json)
- Source file: <https://upload.wikimedia.org/wikipedia/commons/9/9a/Tutorial_breakdance_-_Six_Step.webm>
- License: [CC BY 3.0](https://creativecommons.org/licenses/by/3.0)

Re-render from the preset:

```sh
node presets/render-preview.mjs daily/cuts/2026-11-26-six-step
```

The title is Inter, the same face the preview draws.

## 2026-11-27 — Gel ink

A hand draws a short line with a gel pen on a pink index card.

The picture is 10 seconds starting at 4s, played at 1x and 30 fps. Preset `opencut-editorial` at version `1.0.0`. The portrait source is contained in the 16:9 frame, so the title sits in the white margin. The source audio is the room, kept at the preset volume.

- Preview: [preview.mp4](cuts/2026-11-27-gel-ink/preview.mp4) (derivative, CC BY-SA 4.0)
- Project: [project.json](cuts/2026-11-27-gel-ink/project.json)
- Source file: <https://upload.wikimedia.org/wikipedia/commons/5/52/Aerra%27s_Films_of_the_Ordinary_XII_--_Muji_Smooth_Gel_Ink_Pen.webm>
- License: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0)

Re-render from the preset:

```sh
node presets/render-preview.mjs daily/cuts/2026-11-27-gel-ink
```

The preview draws Liberation Serif where the editor would draw Playfair Display. The project still names Playfair Display.

## 2026-11-28 — Dusk swell

A pink sun sits over the sea while swells roll through the last light.

The picture is 10 seconds starting at 4s, played at 1x and 24 fps. Preset `cinematic-bars` at version `1.1.0`. The title sits in the open window, above the lower bar. The source file has no audio track, so the preview's audio is silence.

- Preview: [preview.mp4](cuts/2026-11-28-dusk-swell/preview.mp4) (derivative, CC0 1.0)
- Project: [project.json](cuts/2026-11-28-dusk-swell/project.json)
- Source file: <https://upload.wikimedia.org/wikipedia/commons/a/a2/Ocean_surface_waves_08.ogv>
- License: [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)

Re-render from the preset:

```sh
node presets/render-preview.mjs daily/cuts/2026-11-28-dusk-swell
```

The preview draws Liberation Serif where the editor would draw Playfair Display. The project still names Playfair Display.

Theme knobs live in [presets/](../presets/README.md). The repository code is MIT. The quiet-press picture and sound stay under CC BY-SA 3.0. The fog-hold picture is CC0 1.0. The pale-rose picture and sound stay under CC BY 4.0. The multi-ball picture and sound stay under CC BY-SA 4.0. The six-step picture stays under CC BY 3.0. The gel-ink picture and sound stay under CC BY-SA 4.0. The dusk-swell picture is CC0 1.0.
