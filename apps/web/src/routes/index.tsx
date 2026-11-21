import { createFileRoute } from "@tanstack/react-router"

import { Badge } from "#/components/ui/badge.tsx"
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "#/components/ui/card.tsx"
import { loadDailyIndex, loadPresets } from "#/presets/catalog.ts"
import previewUrl from "../../../../daily/cuts/2026-11-21-quiet-press/preview.mp4"
import captionsUrl from "../../../../daily/cuts/2026-11-21-quiet-press/captions.vtt?url"

export const Route = createFileRoute("/")({
	head: () => ({
		meta: [{ title: "Daily cuts | OpenCut" }],
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

	return (
		<main className="mx-auto flex w-full max-w-3xl flex-col gap-12 px-6 py-16">
			<header className="flex flex-col gap-3">
				<p className="text-xs tracking-[0.18em] text-muted-foreground uppercase">
					OpenCut
				</p>
				<h1 className="font-heading text-4xl text-balance">Daily cuts</h1>
				<p className="max-w-prose text-base text-muted-foreground">
					{index.about} Themes are data in the repository. This page is the
					same index as <span className="text-foreground">daily/README.md</span>.
				</p>
			</header>

			<section className="flex flex-col gap-4">
				<h2 className="font-heading text-2xl">Themes</h2>
				<ul className="grid gap-3 sm:grid-cols-2">
					{presets.map((preset) => (
						<li key={preset.id}>
							<Card>
								<CardHeader>
									<div className="flex items-center justify-between gap-2">
										<CardTitle>{preset.name}</CardTitle>
										<Badge variant="secondary">{preset.category}</Badge>
									</div>
									<CardDescription>
										{preset.id}@{preset.version}
									</CardDescription>
								</CardHeader>
								<CardContent className="flex flex-col gap-3">
									<p>{preset.summary}</p>
									<a
										href={`/editor?preset=${encodeURIComponent(preset.id)}`}
										className="text-sm underline-offset-4 hover:underline"
									>
										Open in the editor
									</a>
								</CardContent>
							</Card>
						</li>
					))}
				</ul>
			</section>

			<section className="flex flex-col gap-4">
				<h2 className="font-heading text-2xl">Cuts</h2>
				<ul className="flex flex-col gap-6">
					{index.cuts.map((cut) => {
						const media = cutMedia[cut.id]
						return (
							<li key={cut.id}>
								<article className="flex flex-col gap-4">
									<div className="flex flex-wrap items-baseline justify-between gap-2">
										<h3 className="font-heading text-xl">{cut.theme}</h3>
										<p className="text-sm text-muted-foreground">
											<time dateTime={cut.date}>{cut.date}</time>
											{" · "}
											{cut.presetId}@{cut.presetVersion}
										</p>
									</div>
									<p>{cut.shows}</p>
									{media ? (
										<video
											controls
											preload="metadata"
											className="aspect-[9/16] w-full max-w-xs rounded-lg bg-card"
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
									) : null}
									<dl className="grid gap-2 text-sm sm:grid-cols-[8rem_1fr]">
										<dt className="text-muted-foreground">Footage</dt>
										<dd>
											<a
												href={cut.footage.sourceUrl}
												rel="noopener noreferrer"
												target="_blank"
												className="underline-offset-4 hover:underline"
											>
												{cut.footage.title}
											</a>
											{", "}
											{cut.footage.creator}
										</dd>
										<dt className="text-muted-foreground">License</dt>
										<dd>
											<a
												href={cut.footage.licenseUrl}
												rel="noopener noreferrer"
												target="_blank"
												className="underline-offset-4 hover:underline"
											>
												{cut.footage.license}
											</a>
										</dd>
									</dl>
								</article>
							</li>
						)
					})}
				</ul>
			</section>
		</main>
	)
}
