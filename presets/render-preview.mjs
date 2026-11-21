// Render a 10 second preview from a theme preset and a cut record.
//
//   node presets/render-preview.mjs daily/cuts/2026-11-21-quiet-press
//
// The preset supplies pace, colour, type, grade, transitions, and fit.
// The cut supplies the footage URL, the in-point, and any line overrides.
// Playfair Display is the editor face. This machine draws Liberation Serif
// in its place. Inter is used as installed.

import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { parseJsonc } from "./parse-jsonc.mjs";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const TICKS_PER_SECOND = 120_000;
const FONT_SIZE_REFERENCE = 90;
const FONT_STAND_IN = "Liberation Serif stands in for Playfair Display in this preview.";

function argValue(flag) {
	const index = process.argv.indexOf(flag);
	if (index === -1) return undefined;
	return process.argv[index + 1];
}

function ticks(seconds) {
	return { ticks: Math.round(seconds * TICKS_PER_SECOND) };
}

function even(value) {
	const rounded = Math.max(2, Math.round(value));
	return rounded % 2 === 0 ? rounded : rounded - 1;
}

function ffmpegColor(hex) {
	return `0x${hex.replace("#", "")}`;
}

function applyCase(text, mode) {
	if (mode === "upper") return text.toUpperCase();
	if (mode === "lower") return text.toLowerCase();
	return text;
}

function escapeDrawtext(text) {
	return text.replaceAll("\\", "\\\\").replaceAll(":", "\\:").replaceAll("'", "\\'").replaceAll("%", "\\%");
}

function fontFile({ family, weight, style }) {
	const serif = /playfair|serif|times/i.test(family);
	if (serif) {
		const dir = "/usr/share/fonts/truetype/liberation/";
		if (style === "italic" && weight === "bold") return `${dir}LiberationSerif-BoldItalic.ttf`;
		if (style === "italic") return `${dir}LiberationSerif-Italic.ttf`;
		if (weight === "bold") return `${dir}LiberationSerif-Bold.ttf`;
		return `${dir}LiberationSerif-Regular.ttf`;
	}
	const dir = "/usr/share/fonts/truetype/macos/";
	if (style === "italic" && weight === "bold") return `${dir}Inter-BoldItalic.ttf`;
	if (style === "italic") return `${dir}Inter-Italic.ttf`;
	if (weight === "bold") return `${dir}Inter-Bold.ttf`;
	return `${dir}Inter-Regular.ttf`;
}

function run(command, args) {
	const result = spawnSync(command, args, { encoding: "utf8" });
	if (result.status !== 0) {
		process.stderr.write(result.stderr || "");
		process.stderr.write(result.stdout || "");
		throw new Error(`${command} failed`);
	}
	return result.stdout;
}

function ensureSource(cut) {
	const dest = join(tmpdir(), "daily-opencut", `${cut.id}${extname(cut.footage.fileUrl)}`);
	if (!existsSync(dest)) {
		mkdirSync(dirname(dest), { recursive: true });
		run("curl", [
			"-fL",
			"--retry",
			"3",
			"-A",
			"DailyOpenCut/0.1 (open-source video exercise)",
			"-o",
			dest,
			cut.footage.fileUrl,
		]);
	}
	return dest;
}

function extname(url) {
	const clean = url.split("?")[0];
	const match = clean.match(/\.[a-z0-9]+$/i);
	return match ? match[0] : ".bin";
}

function probeDuration(file) {
	const stdout = run("ffprobe", [
		"-v",
		"error",
		"-show_entries",
		"format=duration",
		"-of",
		"csv=p=0",
		file,
	]);
	return Number.parseFloat(stdout.trim());
}

function probeVideoSize(file) {
	const stdout = run("ffprobe", [
		"-v",
		"error",
		"-select_streams",
		"v:0",
		"-show_entries",
		"stream=width,height",
		"-of",
		"csv=p=0",
		file,
	]);
	const [w, h] = stdout.trim().split(",").map((part) => Number.parseInt(part, 10));
	return { w, h };
}

function temperatureFilter(temperature) {
	if (temperature === 0) return null;
	const rs = (temperature / 10) * 0.06;
	const gs = (temperature / 10) * 0.01;
	const bs = (temperature / 10) * -0.07;
	return `colorbalance=rs=${rs.toFixed(4)}:gs=${gs.toFixed(4)}:bs=${bs.toFixed(4)}`;
}

function fitSize(srcW, srcH, canvasW, canvasH, fit) {
	const scale =
		fit === "cover" ? Math.max(canvasW / srcW, canvasH / srcH) : Math.min(canvasW / srcW, canvasH / srcH);
	return { w: even(srcW * scale), h: even(srcH * scale) };
}

function buildVideoFilter({ preset, cut, sourceUsed, sourceSize }) {
	const canvasW = preset.style.canvas.width;
	const canvasH = preset.style.canvas.height;
	const fps = preset.timing.fps.numerator / preset.timing.fps.denominator;
	const frames = Math.max(1, Math.round(cut.durationSeconds * fps));
	const filters = [`trim=start=${cut.inSeconds}:duration=${sourceUsed}`, "setpts=PTS-STARTPTS"];
	if (preset.pace.speed !== 1) {
		filters.push(`setpts=PTS/${preset.pace.speed}`);
	}
	filters.push(`fps=${fps}`);
	const letterbox = preset.compositing.cropSourceLetterbox ? cut.sourceLetterbox : null;
	if (letterbox) {
		filters.push(`crop=${letterbox.width}:${letterbox.height}:${letterbox.x}:${letterbox.y}`);
	}
	filters.push("setsar=1");

	const srcW = letterbox ? letterbox.width : sourceSize.w;
	const srcH = letterbox ? letterbox.height : sourceSize.h;
	const fitted = fitSize(srcW, srcH, canvasW, canvasH, preset.compositing.fit);
	filters.push(`scale=${fitted.w}:${fitted.h}:flags=lanczos`);
	let windowW = fitted.w;
	let windowH = fitted.h;
	if (preset.compositing.fit === "cover") {
		filters.push(`crop=${canvasW}:${canvasH}`);
		windowW = canvasW;
		windowH = canvasH;
	}

	const startScale = preset.motion.startScale;
	const endScale = preset.motion.endScale;
	if (endScale > startScale && startScale >= 1) {
		const drift = preset.motion.positionDriftY;
		const denom = Math.max(1, frames - 1);
		filters.push(
			[
				`zoompan=z='${startScale}+(${endScale - startScale})*on/${denom}'`,
				"d=1",
				"x='iw/2-(iw/zoom/2)'",
				`y='ih/2-(ih/zoom/2)+(${drift})*on/${denom}'`,
				`s=${windowW}x${windowH}`,
				`fps=${fps}`,
			].join(":"),
		);
	}

	const grade = preset.grade;
	filters.push(
		`eq=contrast=${grade.contrast}:brightness=${grade.brightness}:saturation=${grade.saturation}:gamma=${grade.gamma}`,
	);
	const temperature = temperatureFilter(grade.temperature);
	if (temperature) filters.push(temperature);
	if (grade.blurIntensity > 0) {
		filters.push(`gblur=sigma=${(grade.blurIntensity / 5).toFixed(3)}`);
	}

	if (preset.compositing.fit === "contain") {
		filters.push(
			`pad=${canvasW}:${canvasH}:(ow-iw)/2:(oh-ih)/2:${ffmpegColor(preset.colour.background)}`,
		);
	}

	const mask = preset.compositing.mask;
	if (mask?.type === "cinematic-bars") {
		const bar = even(((1 - mask.height) / 2) * canvasH);
		filters.push(`drawbox=x=0:y=0:w=iw:h=${bar}:color=black:t=fill`);
		filters.push(`drawbox=x=0:y=${canvasH - bar}:w=iw:h=${bar}:color=black:t=fill`);
	}

	const lines = (cut.lines ?? preset.type.lines).map((line) => applyCase(line, preset.typography.case));
	const fontPx = Math.round((preset.typography.fontSize * canvasH) / FONT_SIZE_REFERENCE);
	const anchor = canvasH / 2 + preset.type.positionYFraction * canvasH;
	const step = fontPx * preset.typography.lineHeight;
	const top = anchor - (step * lines.length) / 2;
	const margin = preset.type.safeMarginFraction * canvasW;
	const align = preset.typography.align;
	const x =
		align === "left"
			? String(Math.round(margin))
			: align === "right"
				? `w-text_w-${Math.round(margin)}`
				: "(w-text_w)/2";
	const face = fontFile({
		family: preset.typography.displayFamily,
		weight: preset.typography.displayWeight,
		style: preset.typography.fontStyle,
	});
	for (let index = 0; index < lines.length; index += 1) {
		const y = Math.round(top + index * step);
		const box = preset.typography.textBackground.enabled
			? `:box=1:boxcolor=${ffmpegColor(preset.typography.textBackground.color)}:boxborderw=${Math.round(preset.typography.textBackground.paddingX)}`
			: "";
		filters.push(
			`drawtext=fontfile='${face}':text='${escapeDrawtext(lines[index])}':fontsize=${fontPx}:fontcolor=${ffmpegColor(preset.colour.ink)}:x=${x}:y=${y}${box}`,
		);
	}

	const fadeIn = preset.transitions.in;
	const fadeOut = preset.transitions.out;
	if (fadeIn.kind === "dissolve" && fadeIn.seconds > 0) {
		filters.push(`fade=t=in:st=0:d=${fadeIn.seconds}`);
	}
	if (fadeIn.kind === "dip-white" && fadeIn.seconds > 0) {
		filters.push(`fade=t=in:st=0:d=${fadeIn.seconds}:color=white`);
	}
	const outStart = Math.max(0, cut.durationSeconds - fadeOut.seconds);
	if (fadeOut.kind === "dissolve" && fadeOut.seconds > 0) {
		filters.push(`fade=t=out:st=${outStart}:d=${fadeOut.seconds}`);
	}
	if (fadeOut.kind === "dip-white" && fadeOut.seconds > 0) {
		filters.push(`fade=t=out:st=${outStart}:d=${fadeOut.seconds}:color=white`);
	}

	filters.push("format=yuv420p");
	return filters.join(",");
}

function buildAudioFilter({ preset, cut, sourceUsed }) {
	const filters = [
		`atrim=start=${cut.inSeconds}:duration=${sourceUsed}`,
		"asetpts=PTS-STARTPTS",
	];
	if (preset.pace.speed !== 1) filters.push(`atempo=${preset.pace.speed}`);
	filters.push(`volume=${preset.compositing.volume}`);
	if (preset.transitions.in.kind !== "cut" && preset.transitions.in.seconds > 0) {
		filters.push(`afade=t=in:st=0:d=${preset.transitions.in.seconds}`);
	}
	if (preset.transitions.out.kind !== "cut" && preset.transitions.out.seconds > 0) {
		const start = Math.max(0, cut.durationSeconds - preset.transitions.out.seconds);
		filters.push(`afade=t=out:st=${start}:d=${preset.transitions.out.seconds}`);
	}
	return filters.join(",");
}

function scalarChannel(keys) {
	return {
		keys: keys.map((key) => ({
			id: key.id,
			time: ticks(key.time),
			value: key.value,
			segmentToNext: "linear",
			tangentMode: "auto",
		})),
		extrapolation: { before: "hold", after: "hold" },
	};
}

function opacityKeys(preset, duration) {
	const keys = [];
	const fadeIn = preset.transitions.in.seconds;
	const fadeOut = preset.transitions.out.seconds;
	if (preset.transitions.in.kind === "cut" || fadeIn === 0) {
		keys.push({ id: "opacity-in", time: 0, value: 1 });
	} else {
		keys.push({ id: "opacity-0", time: 0, value: 0 });
		keys.push({ id: "opacity-in", time: fadeIn, value: 1 });
	}
	if (preset.transitions.out.kind !== "cut" && fadeOut > 0) {
		keys.push({ id: "opacity-hold", time: duration - fadeOut, value: 1 });
		keys.push({ id: "opacity-out", time: duration, value: 0 });
	}
	return keys;
}

function textParams(preset, content, color, positionY) {
	const background = preset.typography.textBackground;
	return {
		content,
		fontSize: preset.typography.fontSize,
		fontFamily: preset.typography.displayFamily,
		color,
		textAlign: preset.typography.align,
		fontWeight: preset.typography.displayWeight,
		fontStyle: preset.typography.fontStyle,
		textDecoration: "none",
		letterSpacing: preset.typography.letterSpacing,
		lineHeight: preset.typography.lineHeight,
		"background.enabled": background.enabled,
		"background.color": background.color,
		"background.cornerRadius": background.cornerRadius,
		"background.paddingX": background.paddingX,
		"background.paddingY": background.paddingY,
		"background.offsetX": 0,
		"background.offsetY": 0,
		"transform.positionX": 0,
		"transform.positionY": positionY,
		"transform.scaleX": 1,
		"transform.scaleY": 1,
		"transform.rotate": 0,
		opacity: 1,
		blendMode: "normal",
	};
}

function writeProject({ preset, cut, sourceDuration, sourceUsed, previewPath }) {
	const duration = cut.durationSeconds;
	const trimEnd = sourceDuration - cut.inSeconds - sourceUsed;
	const canvas = preset.style.canvas;
	const lines = (cut.lines ?? preset.type.lines).map((line) => applyCase(line, preset.typography.case));
	const positionY = Math.round(preset.type.positionYFraction * canvas.height);
	const effects = [
		{
			id: "fx-grade",
			type: "grade",
			enabled: true,
			params: { ...preset.grade },
		},
	];
	if (preset.grade.blurIntensity > 0) {
		effects.push({
			id: "fx-blur",
			type: "blur",
			enabled: true,
			params: { intensity: preset.grade.blurIntensity },
		});
	}
	const masks = preset.compositing.mask
		? [
				{
					id: "mask-frame",
					type: preset.compositing.mask.type,
					params: {
						centerX: 0,
						centerY: 0,
						width: 1,
						height: preset.compositing.mask.height,
						rotation: 0,
						scale: 1,
						feather: preset.compositing.mask.feather,
						inverted: false,
						strokeColor: "#ffffff",
						strokeWidth: 0,
						strokeAlign: "center",
					},
				},
			]
		: [];
	const background =
		preset.colour.backgroundBlur > 0
			? { type: "blur", blurIntensity: preset.colour.backgroundBlur }
			: { type: "color", color: preset.colour.background };

	const project = {
		metadata: {
			id: cut.id,
			name: cut.title,
			duration: ticks(duration),
			createdAt: `${cut.date}T00:00:00.000Z`,
			updatedAt: `${cut.date}T00:00:00.000Z`,
		},
		settings: {
			fps: preset.timing.fps,
			canvasSize: { width: canvas.width, height: canvas.height },
			canvasSizeMode: preset.style.canvasSizeMode,
			background,
		},
		currentSceneId: "scene-main",
		version: 1,
		scenes: [
			{
				id: "scene-main",
				name: "Main scene",
				isMain: true,
				bookmarks: [],
				createdAt: `${cut.date}T00:00:00.000Z`,
				updatedAt: `${cut.date}T00:00:00.000Z`,
				tracks: {
					overlay: [
						{
							id: "track-type",
							name: "Text track",
							type: "text",
							hidden: false,
							elements: [
								{
									id: "el-title",
									type: "text",
									name: "Title",
									duration: ticks(duration),
									startTime: ticks(0),
									trimStart: ticks(0),
									trimEnd: ticks(0),
									params: textParams(preset, lines.join("\n"), preset.colour.ink, positionY),
								},
							],
						},
					],
					main: {
						id: "track-main",
						name: "Main",
						type: "video",
						muted: false,
						hidden: false,
						elements: [
							{
								id: "el-picture",
								type: "video",
								mediaId: cut.footage.mediaId,
								name: cut.footage.title,
								duration: ticks(duration),
								startTime: ticks(0),
								trimStart: ticks(cut.inSeconds),
								trimEnd: ticks(Math.max(0, trimEnd)),
								sourceDuration: ticks(sourceDuration),
								isSourceAudioEnabled: true,
								retime: {
									rate: preset.pace.speed,
									maintainPitch: preset.pace.maintainPitch,
								},
								effects,
								masks,
								animations: {
									opacity: scalarChannel(opacityKeys(preset, duration)),
									"transform.scaleX": scalarChannel([
										{ id: "scale-x-0", time: 0, value: preset.motion.startScale },
										{ id: "scale-x-1", time: duration, value: preset.motion.endScale },
									]),
									"transform.scaleY": scalarChannel([
										{ id: "scale-y-0", time: 0, value: preset.motion.startScale },
										{ id: "scale-y-1", time: duration, value: preset.motion.endScale },
									]),
								},
								params: {
									"transform.positionX": 0,
									"transform.positionY": preset.motion.positionDriftY,
									"transform.scaleX": preset.motion.startScale,
									"transform.scaleY": preset.motion.startScale,
									"transform.rotate": preset.motion.rotateDegrees,
									opacity: 1,
									blendMode: preset.compositing.blendMode,
									volume: preset.compositing.volume,
								},
							},
						],
					},
					audio: [],
				},
			},
		],
		daily: {
			format: "daily-opencut-cut",
			presetId: preset.id,
			presetVersion: preset.version,
			presetPath: `presets/themes/${preset.id}.jsonc`,
			fit: preset.compositing.fit,
			cropSourceLetterbox: preset.compositing.cropSourceLetterbox,
			footage: cut.footage,
			inSeconds: cut.inSeconds,
			durationSeconds: duration,
			sourceDurationSeconds: sourceDuration,
			sourceLetterbox: cut.sourceLetterbox ?? null,
			lines,
			preview: previewPath,
			fontStandIn: FONT_STAND_IN,
			render: `node presets/render-preview.mjs ${dirname(previewPath)}`,
		},
	};

	const projectPath = join(root, dirname(previewPath), "project.json");
	writeFileSync(projectPath, `${JSON.stringify(project, null, 2)}\n`);
	return projectPath;
}

const cutDirArg = process.argv[2];
if (!cutDirArg || cutDirArg.startsWith("--")) {
	throw new Error("Pass the cut directory, for example daily/cuts/2026-11-21-quiet-press");
}

const cutDir = resolve(root, cutDirArg);
const cut = JSON.parse(readFileSync(join(cutDir, "cut.json"), "utf8"));
const preset = parseJsonc(
	readFileSync(join(root, "presets", "themes", `${cut.presetId}.jsonc`), "utf8"),
);
const source = ensureSource(cut);
const sourceDuration = probeDuration(source);
const sourceSize = probeVideoSize(source);
const sourceUsed = cut.durationSeconds * preset.pace.speed;
if (cut.inSeconds + sourceUsed > sourceDuration + 0.05) {
	throw new Error(
		`In-point ${cut.inSeconds}s plus ${sourceUsed}s of source runs past ${sourceDuration}s`,
	);
}

const previewRel = argValue("--out") ?? join(cutDirArg, "preview.mp4");
const previewAbs = resolve(root, previewRel);
mkdirSync(dirname(previewAbs), { recursive: true });

const videoFilter = buildVideoFilter({ preset, cut, sourceUsed, sourceSize });
const audioFilter = buildAudioFilter({ preset, cut, sourceUsed });
const fps = preset.timing.fps.numerator / preset.timing.fps.denominator;

run("ffmpeg", [
	"-y",
	"-i",
	source,
	"-filter_complex",
	`[0:v]${videoFilter}[v];[0:a]${audioFilter}[a]`,
	"-map",
	"[v]",
	"-map",
	"[a]",
	"-t",
	String(cut.durationSeconds),
	"-r",
	String(fps),
	"-c:v",
	"libx264",
	"-pix_fmt",
	"yuv420p",
	"-crf",
	"23",
	"-preset",
	"veryfast",
	"-c:a",
	"aac",
	"-b:a",
	"128k",
	"-movflags",
	"+faststart",
	"-metadata",
	`title=${cut.title}`,
	"-metadata",
	`artist=${cut.footage.creator}`,
	"-metadata",
	`comment=Picture and sound from ${cut.footage.title}. ${cut.footage.license}. ${cut.footage.sourceUrl}`,
	previewAbs,
]);

if (!process.argv.includes("--skip-project")) {
	const written = writeProject({
		preset,
		cut,
		sourceDuration,
		sourceUsed,
		previewPath: previewRel,
	});
	console.log(written);
}
console.log(previewAbs);
