# Daily cuts

Ten-second reference edits for OpenCut theme presets. This file is the index. The web app shows the same list on the home page.

Each row is one cut: the theme, the date, what it shows, the footage and its license, and the preset version that was applied.

| Date | Theme | Preset | Shows | Footage | License |
| --- | --- | --- | --- | --- | --- |
| 2026-11-21 | Minimalistic homie | [minimalistic-homie@1.1.0](../presets/themes/minimalistic-homie.jsonc) | A hand lifts a French press and pours coffee into a red mug on a kitchen counter. | [Use of a coffee press](https://commons.wikimedia.org/wiki/File:Use_of_a_coffee_press.ogv) by Daniel Case, videography by his son | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0) |

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

Theme knobs live in [presets/](../presets/README.md). The repository code is MIT. This cut's picture and sound stay under CC BY-SA 3.0.
