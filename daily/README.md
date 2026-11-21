# Daily cuts

Ten-second reference edits for OpenCut theme presets. This file is the index. The web app home page plays the cuts. The same list is in the collapsible panel on the left.

Each row is one cut: the theme, the date, what it shows, the footage and its license, and the preset version that was applied.

| Date | Theme | Preset | Shows | Footage | License |
| --- | --- | --- | --- | --- | --- |
| 2026-11-21 | Minimalistic homie | [minimalistic-homie@1.1.0](../presets/themes/minimalistic-homie.jsonc) | A hand lifts a French press and pours coffee into a red mug on a kitchen counter. | [Use of a coffee press](https://commons.wikimedia.org/wiki/File:Use_of_a_coffee_press.ogv) by Daniel Case, videography by his son | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0) |
| 2026-11-21 | Cinematic bars | [cinematic-bars@1.1.0](../presets/themes/cinematic-bars.jsonc) | A drone drifts over morning fog above the village of Vetla, with houses and fields showing through the trees. | [Drone video of foggy Vetla village in Estonia](https://commons.wikimedia.org/wiki/File:Drone_video_of_foggy_Vetla_village_in_Estonia.ogv) by Sillerkiil | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) |

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

Theme knobs live in [presets/](../presets/README.md). The repository code is MIT. The quiet-press picture and sound stay under CC BY-SA 3.0. This cut's picture is CC0 1.0.
