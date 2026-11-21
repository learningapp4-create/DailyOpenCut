import indexRaw from "../../../../daily/index.json?raw"
import cinematicBars from "../../../../presets/themes/cinematic-bars.jsonc?raw"
import genzAdhd from "../../../../presets/themes/genz-adhd.jsonc?raw"
import indieFashionCute from "../../../../presets/themes/indie-fashion-cute.jsonc?raw"
import minimalisticHomie from "../../../../presets/themes/minimalistic-homie.jsonc?raw"
import opencutEditorial from "../../../../presets/themes/opencut-editorial.jsonc?raw"
import playfulGamer from "../../../../presets/themes/playful-gamer.jsonc?raw"

import { parseJsonc } from "./parse-jsonc.ts"

export type ThemePreset = {
	id: string
	version: string
	category: string
	name: string
	summary: string
	style: Record<string, unknown>
	pace: Record<string, unknown>
	colour: Record<string, unknown>
	typography: Record<string, unknown>
	transitions: Record<string, unknown>
	timing: Record<string, unknown>
	grade: Record<string, unknown>
	type: Record<string, unknown>
	motion: Record<string, unknown>
	compositing: Record<string, unknown>
	changelog: { version: string; note: string }[]
}

export type DailyCut = {
	id: string
	date: string
	theme: string
	presetId: string
	presetVersion: string
	shows: string
	footage: {
		title: string
		creator: string
		sourceUrl: string
		fileUrl: string
		license: string
		licenseUrl: string
	}
	paths: {
		project: string
		preview: string
		preset: string
	}
}

export type DailyIndex = {
	title: string
	about: string
	cuts: DailyCut[]
}

const presetSources = [
	minimalisticHomie,
	playfulGamer,
	genzAdhd,
	indieFashionCute,
	opencutEditorial,
	cinematicBars,
]

function isRecord(value: unknown): value is Record<string, unknown> {
	return typeof value === "object" && value !== null && !Array.isArray(value)
}

function readString(record: Record<string, unknown>, key: string): string {
	const value = record[key]
	if (typeof value !== "string" || value.length === 0) {
		throw new Error(`Missing ${key}`)
	}
	return value
}

function asPreset(value: unknown): ThemePreset {
	if (!isRecord(value)) throw new Error("Preset did not parse")
	const changelog = value.changelog
	if (!Array.isArray(changelog)) throw new Error("Preset changelog missing")
	return {
		id: readString(value, "id"),
		version: readString(value, "version"),
		category: readString(value, "category"),
		name: readString(value, "name"),
		summary: readString(value, "summary"),
		style: isRecord(value.style) ? value.style : {},
		pace: isRecord(value.pace) ? value.pace : {},
		colour: isRecord(value.colour) ? value.colour : {},
		typography: isRecord(value.typography) ? value.typography : {},
		transitions: isRecord(value.transitions) ? value.transitions : {},
		timing: isRecord(value.timing) ? value.timing : {},
		grade: isRecord(value.grade) ? value.grade : {},
		type: isRecord(value.type) ? value.type : {},
		motion: isRecord(value.motion) ? value.motion : {},
		compositing: isRecord(value.compositing) ? value.compositing : {},
		changelog: changelog.flatMap((entry) => {
			if (!isRecord(entry)) return []
			const version = entry.version
			const note = entry.note
			if (typeof version !== "string" || typeof note !== "string") return []
			return [{ version, note }]
		}),
	}
}

function asCut(value: unknown): DailyCut {
	if (!isRecord(value)) throw new Error("Cut did not parse")
	const footage = value.footage
	const paths = value.paths
	if (!isRecord(footage) || !isRecord(paths)) throw new Error("Cut is incomplete")
	return {
		id: readString(value, "id"),
		date: readString(value, "date"),
		theme: readString(value, "theme"),
		presetId: readString(value, "presetId"),
		presetVersion: readString(value, "presetVersion"),
		shows: readString(value, "shows"),
		footage: {
			title: readString(footage, "title"),
			creator: readString(footage, "creator"),
			sourceUrl: readString(footage, "sourceUrl"),
			fileUrl: readString(footage, "fileUrl"),
			license: readString(footage, "license"),
			licenseUrl: readString(footage, "licenseUrl"),
		},
		paths: {
			project: readString(paths, "project"),
			preview: readString(paths, "preview"),
			preset: readString(paths, "preset"),
		},
	}
}

export function loadPresets(): ThemePreset[] {
	return presetSources.map((source) => asPreset(parseJsonc(source)))
}

export function loadDailyIndex(): DailyIndex {
	const parsed = parseJsonc(indexRaw)
	if (!isRecord(parsed) || !Array.isArray(parsed.cuts)) {
		throw new Error("Daily index did not parse")
	}
	return {
		title: readString(parsed, "title"),
		about: readString(parsed, "about"),
		cuts: parsed.cuts.map((cut) => asCut(cut)),
	}
}

export function findPreset(id: string): ThemePreset | undefined {
	return loadPresets().find((preset) => preset.id === id)
}
