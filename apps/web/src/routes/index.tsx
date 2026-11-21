import { useEffect, useState } from "react"
import { createFileRoute } from "@tanstack/react-router"

import { Button } from "#/components/ui/button.tsx"
import { cn } from "#/lib/utils.ts"
import {
	loadDailyIndex,
	loadPresets,
	type DailyCut,
	type DailyIndex,
	type ThemePreset,
} from "#/presets/catalog.ts"
import previewUrl from "../../../../daily/cuts/2026-11-21-quiet-press/preview.mp4"
import captionsUrl from "../../../../daily/cuts/2026-11-21-quiet-press/captions.vtt?url"

export const Route = createFileRoute("/")({
	head: () => ({
		meta: [{ title: "Daily cuts" }],
	}),
	component: Home,
})

const cutMedia: Record<string, { video: string; captions: string }> = {
	"2026-11-21-quiet-press": {
		video: previewUrl,
		captions: captionsUrl,
	},
}

function Home() {
	const index = loadDailyIndex()
	const presets = loadPresets()
	const [open, setOpen] = useState(false)
	const [activeId, setActiveId] = useState(index.cuts[0]?.id ?? "")
	const activeCut = index.cuts.find((cut) => cut.id === activeId) ?? index.cuts[0]

	useEffect(() => {
		const nodes = document.querySelectorAll<HTMLElement>("[data-cut-id]")
		if (nodes.length === 0) return
		const observer = new IntersectionObserver(
			(entries) => {
				const visible = entries
					.filter((entry) => entry.isIntersecting)
					.sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0]
				const id = visible?.target.getAttribute("data-cut-id")
				if (id) setActiveId(id)
			},
			{ threshold: [0.6, 0.9] },
		)
		for (const node of nodes) observer.observe(node)
		return () => observer.disconnect()
	}, [index.cuts])

	useEffect(() => {
		if (!open) return
		const onKey = (event: KeyboardEvent) => {
			if (event.key === "Escape") setOpen(false)
		}
		window.addEventListener("keydown", onKey)
		return () => window.removeEventListener("keydown", onKey)
	}, [open])

	return (
		<div className="flex h-dvh overflow-hidden bg-background">
			<ProjectPanel
				open={open}
				onClose={() => setOpen(false)}
				index={index}
				presets={presets}
				activeCut={activeCut}
			/>
			{open ? (
				<button
					type="button"
					className="fixed inset-0 z-20 bg-black/40 md:hidden"
					aria-label="Close about this project"
					onClick={() => setOpen(false)}
				/>
			) : null}
			<main className="flex min-w-0 flex-1 flex-col">
				<div className="flex h-12 shrink-0 items-center px-3">
					<Button
						type="button"
						variant="outline"
						className={cn(open && "max-md:hidden")}
						aria-expanded={open}
						aria-controls="project-panel"
						onClick={() => setOpen((value) => !value)}
					>
						{open ? "Hide" : "About"}
					</Button>
				</div>
				<h1 className="sr-only">Daily cuts</h1>
				<div className="min-h-0 flex-1 snap-y snap-mandatory overflow-y-auto">
					{index.cuts.length === 0 ? (
						<p className="flex h-full items-center justify-center text-sm text-muted-foreground">
							No cut yet.
						</p>
					) : (
						index.cuts.map((cut) => (
							<CutFrame key={cut.id} cut={cut} />
						))
					)}
				</div>
			</main>
		</div>
	)
}

function CutFrame({ cut }: { cut: DailyCut }) {
	const media = cutMedia[cut.id]
	return (
		<section
			data-cut-id={cut.id}
			className="flex h-full snap-start items-center justify-center px-4 py-4"
		>
			<h2 className="sr-only">
				{cut.theme}, {cut.date}
			</h2>
			{media ? (
				<video
					controls
					playsInline
					preload="metadata"
					className="max-h-full max-w-full rounded-md bg-neutral-950 object-contain"
					src={media.video}
				>
					<track
						default
						kind="captions"
						srcLang="en"
						label="English"
						src={media.captions}
					/>
				</video>
			) : (
				<p className="text-sm text-muted-foreground">Preview missing for {cut.theme}.</p>
			)}
		</section>
	)
}

function ProjectPanel({
	open,
	onClose,
	index,
	presets,
	activeCut,
}: {
	open: boolean
	onClose: () => void
	index: DailyIndex
	presets: ThemePreset[]
	activeCut: DailyCut | undefined
}) {
	return (
		<aside
			id="project-panel"
			aria-label="About this project"
			aria-hidden={!open}
			inert={!open}
			className={cn(
				"z-30 h-full shrink-0 overflow-hidden border-sidebar-border bg-sidebar text-sidebar-foreground transition-[width] duration-200 ease-out",
				open
					? "w-80 border-r max-md:fixed max-md:inset-y-0 max-md:left-0 max-md:shadow-xl"
					: "w-0 border-r-0",
			)}
		>
			<div className="flex h-full w-80 max-w-[calc(100vw-3rem)] flex-col">
				<header className="flex items-start justify-between gap-3 px-5 pt-5 pb-3">
					<div className="flex flex-col gap-1">
						<p className="text-xs tracking-[0.16em] text-muted-foreground uppercase">
							Daily cuts
						</p>
						<p className="font-heading text-2xl">About this project</p>
					</div>
					<Button type="button" variant="ghost" size="sm" onClick={onClose}>
						Close
					</Button>
				</header>
				<div className="flex flex-1 flex-col gap-8 overflow-y-auto px-5 pt-2 pb-8">
					<section className="flex flex-col gap-3 text-sm leading-relaxed">
						<p>
							{index.about} The page is the videos. This panel is how you read
							a cut: theme, footage, license, and preset.
						</p>
						<p className="text-muted-foreground">
							Themes are JSONC in the repository. Each file sets style, pace,
							colour, typography, transitions, and compositing: timing, grade,
							type, and motion. A pipeline or the editor loads that file. The
							same list is <span className="text-foreground">daily/README.md</span>.
							The code is MIT. The picture stays under the footage license.
						</p>
					</section>

					{activeCut ? (
						<section className="flex flex-col gap-3 border-t border-sidebar-border pt-6">
							<h2 className="font-heading text-lg">This cut</h2>
							<p className="font-heading text-xl">{activeCut.theme}</p>
							<p className="text-sm text-muted-foreground">
								<time dateTime={activeCut.date}>{activeCut.date}</time>
								{" · "}
								{activeCut.presetId}@{activeCut.presetVersion}
							</p>
							<p className="text-sm leading-relaxed">{activeCut.shows}</p>
							<dl className="grid gap-2 text-sm">
								<div>
									<dt className="text-muted-foreground">Footage</dt>
									<dd>
										<a
											href={activeCut.footage.sourceUrl}
											rel="noopener noreferrer"
											target="_blank"
											className="underline-offset-4 hover:underline"
										>
											{activeCut.footage.title}
										</a>
										{", "}
										{activeCut.footage.creator}
									</dd>
								</div>
								<div>
									<dt className="text-muted-foreground">License</dt>
									<dd>
										<a
											href={activeCut.footage.licenseUrl}
											rel="noopener noreferrer"
											target="_blank"
											className="underline-offset-4 hover:underline"
										>
											{activeCut.footage.license}
										</a>
									</dd>
								</div>
							</dl>
							<a
								href={`/editor?preset=${encodeURIComponent(activeCut.presetId)}`}
								className="text-sm underline-offset-4 hover:underline"
							>
								Open this preset
							</a>
						</section>
					) : null}

					<section className="flex flex-col gap-4 border-t border-sidebar-border pt-6">
						<h2 className="font-heading text-lg">Themes</h2>
						<ul className="flex flex-col gap-4">
							{presets.map((preset) => (
								<li key={preset.id} className="flex flex-col gap-1 text-sm">
									<p className="flex items-baseline justify-between gap-3">
										<span className="font-medium">{preset.name}</span>
										<span className="text-xs text-muted-foreground">
											{preset.category}
										</span>
									</p>
									<p className="text-muted-foreground">{preset.summary}</p>
									<a
										href={`/editor?preset=${encodeURIComponent(preset.id)}`}
										className="underline-offset-4 hover:underline"
									>
										{preset.id}@{preset.version}
									</a>
								</li>
							))}
						</ul>
					</section>
				</div>
			</div>
		</aside>
	)
}
