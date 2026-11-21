import { createFileRoute } from "@tanstack/react-router"

import { findPreset, type ThemePreset } from "#/presets/catalog.ts"

type EditorSearch = {
	preset: string
}

const knobGroups = [
	"style",
	"pace",
	"colour",
	"typography",
	"transitions",
	"timing",
	"grade",
	"type",
	"motion",
	"compositing",
] as const

export const Route = createFileRoute("/editor")({
	validateSearch: (search: Record<string, unknown>): EditorSearch => {
		return {
			preset: typeof search.preset === "string" ? search.preset : "",
		}
	},
	component: Editor,
})

function formatKnob(value: unknown): string {
	if (typeof value === "string") return value
	if (typeof value === "number" || typeof value === "boolean") return String(value)
	if (value === null) return "null"
	return JSON.stringify(value)
}

function KnobGroup({
	name,
	value,
}: {
	name: string
	value: Record<string, unknown>
}) {
	const entries = Object.entries(value)
	return (
		<section className="flex flex-col gap-2">
			<h2 className="font-heading text-lg">{name}</h2>
			<dl className="grid gap-1 text-sm sm:grid-cols-[12rem_1fr]">
				{entries.map(([key, item]) => (
					<div key={key} className="contents">
						<dt className="text-muted-foreground">{key}</dt>
						<dd className="break-words">{formatKnob(item)}</dd>
					</div>
				))}
			</dl>
		</section>
	)
}

function PresetView({ preset }: { preset: ThemePreset }) {
	const latest = preset.changelog.at(-1)
	return (
		<div className="flex flex-col gap-8">
			<header className="flex flex-col gap-2">
				<p className="text-sm text-muted-foreground">
					{preset.category} · {preset.id}@{preset.version}
				</p>
				<h1 className="font-heading text-3xl">{preset.name}</h1>
				<p className="max-w-prose text-muted-foreground">{preset.summary}</p>
				{latest ? (
					<p className="max-w-prose text-sm">
						{latest.version}: {latest.note}
					</p>
				) : null}
			</header>
			{knobGroups.map((group) => (
				<KnobGroup key={group} name={group} value={preset[group]} />
			))}
		</div>
	)
}

function Editor() {
	const { preset: presetId } = Route.useSearch()
	const preset = presetId ? findPreset(presetId) : undefined

	return (
		<main className="mx-auto flex w-full max-w-3xl flex-col gap-8 px-6 py-16">
			<p>
				<a href="/" className="text-sm underline-offset-4 hover:underline">
					Daily cuts
				</a>
			</p>
			{preset ? (
				<PresetView preset={preset} />
			) : (
				<header className="flex flex-col gap-2">
					<h1 className="font-heading text-3xl">Editor</h1>
					<p className="text-muted-foreground">
						{presetId
							? `No preset named ${presetId}.`
							: "Open a theme from the daily index to load its knobs."}
					</p>
				</header>
			)}
		</main>
	)
}
