// Load every theme preset and check it against presets/schema.json.
// Also checks the daily index, when present, points at those presets.
//
//   node presets/load.mjs

import { spawnSync } from "node:child_process";
import { readFileSync, readdirSync, existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { parseJsonc } from "./parse-jsonc.mjs";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const presetsDir = join(root, "presets", "themes");
const schema = JSON.parse(readFileSync(join(root, "presets", "schema.json"), "utf8"));

const EASING = {
	smooth: [0.25, 0.1, 0.25, 1],
	"ease-out": [0, 0, 0.2, 1],
	"ease-in": [0.8, 0, 1, 1],
	"ease-in-out": [0.4, 0, 0.2, 1],
	pop: [0.175, 0.885, 0.32, 1.275],
	linear: [0, 0, 1, 1],
};

const errors = [];

function fail(message) {
	errors.push(message);
}

function ref(schemaNode) {
	if (!schemaNode.$ref) return schemaNode;
	const name = schemaNode.$ref.slice("#/$defs/".length);
	return schema.$defs[name];
}

function typeOf(value) {
	if (value === null) return "null";
	if (Array.isArray(value)) return "array";
	return typeof value;
}

function matchesType(expected, value) {
	const actual = typeOf(value);
	if (expected === "integer") {
		return typeof value === "number" && Number.isInteger(value);
	}
	if (expected === "number") return typeof value === "number";
	return actual === expected;
}

function validate(schemaNode, value, path) {
	const node = ref(schemaNode);
	if (node.oneOf) {
		const before = errors.length;
		const local = [];
		for (const option of node.oneOf) {
			const saved = errors.splice(before);
			local.push(saved);
			validate(option, value, path);
			if (errors.length === before) return;
			local[local.length - 1].push(...errors.splice(before));
		}
		fail(`${path} matched none of the allowed shapes`);
		return;
	}

	if (node.enum && !node.enum.includes(value)) {
		fail(`${path} must be one of ${node.enum.join(", ")}`);
	}
	if (Object.hasOwn(node, "const") && value !== node.const) {
		fail(`${path} must be ${node.const}`);
	}
	if (node.type) {
		const expected = Array.isArray(node.type) ? node.type : [node.type];
		if (!expected.some((kind) => matchesType(kind, value))) {
			fail(`${path} should be ${expected.join(" or ")}`);
			return;
		}
	}
	if (typeof value === "number") {
		if (Object.hasOwn(node, "minimum") && value < node.minimum) {
			fail(`${path} is below ${node.minimum}`);
		}
		if (Object.hasOwn(node, "exclusiveMinimum") && value <= node.exclusiveMinimum) {
			fail(`${path} must be greater than ${node.exclusiveMinimum}`);
		}
		if (Object.hasOwn(node, "maximum") && value > node.maximum) {
			fail(`${path} is above ${node.maximum}`);
		}
	}
	if (node.type === "object" && value && typeof value === "object") {
		const keys = Object.keys(value);
		for (const key of node.required ?? []) {
			if (!Object.hasOwn(value, key)) fail(`${path}.${key} is missing`);
		}
		if (node.additionalProperties === false) {
			for (const key of keys) {
				if (!node.properties?.[key]) fail(`${path}.${key} is not a known knob`);
			}
		}
		for (const key of keys) {
			const child = node.properties?.[key];
			if (child) validate(child, value[key], `${path}.${key}`);
		}
	}
	if (node.type === "array" && Array.isArray(value)) {
		if (Object.hasOwn(node, "minItems") && value.length < node.minItems) {
			fail(`${path} needs at least ${node.minItems} items`);
		}
		if (Object.hasOwn(node, "maxItems") && value.length > node.maxItems) {
			fail(`${path} has more than ${node.maxItems} items`);
		}
		if (node.items) {
			for (let index = 0; index < value.length; index += 1) {
				validate(node.items, value[index], `${path}[${index}]`);
			}
		}
	}
}

function checkEasing(easing, path) {
	const expected = EASING[easing.id];
	if (!expected) return;
	if (easing.bezier.length !== 4 || easing.bezier.some((item, index) => item !== expected[index])) {
		fail(`${path} bezier does not match the editor builtin "${easing.id}"`);
	}
}

const files = readdirSync(presetsDir).filter((name) => name.endsWith(".jsonc")).sort();
if (files.length === 0) fail("no theme files");

const catalogSource = readFileSync(
	join(root, "apps", "web", "src", "presets", "catalog.ts"),
	"utf8",
);
for (const file of files) {
	if (!catalogSource.includes(file)) {
		fail(`apps/web/src/presets/catalog.ts does not import ${file}`);
	}
}

const presets = new Map();
for (const file of files) {
	const full = join(presetsDir, file);
	let preset;
	try {
		preset = parseJsonc(readFileSync(full, "utf8"));
	} catch (error) {
		fail(`${file} did not parse: ${error.message}`);
		continue;
	}
	validate(schema, preset, file);
	if (preset?.id && file !== `${preset.id}.jsonc`) {
		fail(`${file} id is ${preset.id}`);
	}
	if (preset?.pace && preset.pace.shotLengthSeconds.min > preset.pace.shotLengthSeconds.max) {
		fail(`${file} shot min is longer than shot max`);
	}
	for (const key of ["in", "out", "between"]) {
		if (preset?.transitions?.[key]) checkEasing(preset.transitions[key].easing, `${file} transitions.${key}.easing`);
	}
	if (preset?.motion?.easing) checkEasing(preset.motion.easing, `${file} motion.easing`);
	const versions = new Set((preset.changelog ?? []).map((entry) => entry.version));
	if (preset.version && !versions.has(preset.version)) {
		fail(`${file} changelog has no note for ${preset.version}`);
	}
	presets.set(preset.id, preset);
}

const indexPath = join(root, "daily", "index.json");
if (!existsSync(indexPath)) {
	fail("daily/index.json is missing");
} else {
	const index = JSON.parse(readFileSync(indexPath, "utf8"));
	if (!Array.isArray(index.cuts) || index.cuts.length === 0) {
		fail("daily index has no cuts");
	}
	for (const cut of index.cuts ?? []) {
		const preset = presets.get(cut.presetId);
		if (!preset) {
			fail(`index cut ${cut.id} uses unknown preset ${cut.presetId}`);
			continue;
		}
		if (cut.presetVersion !== preset.version) {
			fail(`index cut ${cut.id} says ${cut.presetId}@${cut.presetVersion} but the file is ${preset.version}`);
		}
		const readme = readFileSync(join(root, "daily", "README.md"), "utf8");
		for (const needle of [cut.date, cut.presetId, cut.presetVersion, cut.footage.license, cut.footage.sourceUrl, cut.shows]) {
			if (!readme.includes(needle)) fail(`daily/README.md is missing ${needle}`);
		}
		const projectPath = join(root, cut.paths.project);
		if (!existsSync(projectPath)) {
			fail(`missing project ${cut.paths.project}`);
		} else {
			const project = JSON.parse(readFileSync(projectPath, "utf8"));
			if (project.daily?.presetVersion !== preset.version) {
				fail(`${cut.paths.project} preset version does not match the theme file`);
			}
			const canvas = project.settings?.canvasSize;
			if (canvas?.width !== preset.style.canvas.width || canvas?.height !== preset.style.canvas.height) {
				fail(`${cut.paths.project} canvas does not match the preset`);
			}
		}
		const previewPath = join(root, cut.paths.preview);
		if (!existsSync(previewPath)) {
			fail(`missing preview ${cut.paths.preview}`);
		} else {
			const probed = spawnSync(
				"ffprobe",
				["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", previewPath],
				{ encoding: "utf8" },
			);
			const duration = Number.parseFloat(probed.stdout.trim());
			if (!Number.isFinite(duration) || Math.abs(duration - 10) > 0.2) {
				fail(`${cut.paths.preview} is ${probed.stdout.trim() || "unreadable"} seconds, expected about 10`);
			}
		}
	}
}

if (errors.length > 0) {
	for (const error of errors) console.error(error);
	console.error(`${errors.length} check(s) failed`);
	process.exit(1);
}

console.log(`parsed ${presets.size} presets`);
for (const preset of presets.values()) {
	console.log(`  ${preset.id}@${preset.version}  ${preset.style.canvas.width}x${preset.style.canvas.height}  ${preset.category}`);
}
if (existsSync(indexPath)) {
	const index = JSON.parse(readFileSync(indexPath, "utf8"));
	console.log(`index ${index.cuts.length} cut(s)`);
}
