# Theme presets

JSONC files a pipeline or the editor can load. Each file is one theme. Comments on the knobs say what they do. `schema.json` is the contract.

```sh
node presets/load.mjs
node presets/render-preview.mjs daily/cuts/2026-11-21-quiet-press
node presets/render-preview.mjs daily/cuts/2026-11-21-fog-hold
```

## How a preset lands in a project

The rewrite's editor model, carried over from the current app, is a project with `settings` and scenes whose tracks are `overlay`, `main`, and `audio`. Time is `MediaTime`: an integer tick count at 120000 ticks per second. Frame rate is a rational `{ numerator, denominator }`.

| Knob group | Where it goes |
| --- | --- |
| `style.canvas` | `settings.canvasSize`. `canvasSizeMode` is `preset` for 1920×1080, 1080×1920, 1080×1080, and 1440×1080. |
| `colour.background` | `settings.background` color, or a blur background when `backgroundBlur` is above 0. |
| `pace.speed` | `retime.rate` on the video. Source used is timeline length times the rate. |
| `grade` | An effect of type `grade` on the picture. `blurIntensity` above 0 also adds the editor's `blur` effect. |
| `typography` and `type` | A text element on an overlay text track. `fontSize` is the editor design size: pixels = fontSize × canvas height / 90, clamped to 5..300. |
| `transitions` | Opacity keyframes. The editor has no transition object. `slide-left` is the handoff between two shots. |
| `motion` | `transform.scaleX` / `scaleY` keyframes, plus `positionDriftY`. Easing ids match the graph editor: smooth, ease-out, ease-in, ease-in-out, pop, linear. |
| `compositing.mask` | A `cinematic-bars` mask. `height` is the open window as a fraction of the frame. Null means no mask. |
| `compositing.fit` | `contain` keeps the whole gesture. `cover` fills the frame and crops. |
| `compositing.volume` | `volume` on the video element. |

## Themes

| Id | Why it's here |
| --- | --- |
| `minimalistic-homie` | Quiet domestic stills. |
| `playful-gamer` | Acid HUD type and a pop into the hit. |
| `genz-adhd` | Jump cuts and a caption chip. |
| `indie-fashion-cute` | Blush 4:5 frame and an italic serif. |
| `opencut-editorial` | Playfair Display, Inter, and the neutral palette already used by the web shell. |
| `cinematic-bars` | The cinematic-bars mask, at 24 fps. |

`minimalistic-homie` is at 1.1.0. The changelog in that file says what the first 10 second conform changed. `cinematic-bars` is at 1.1.0. The changelog in that file says what the fog hold changed.
