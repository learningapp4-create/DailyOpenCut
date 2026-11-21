// Same comment stripper as presets/parse-jsonc.mjs. Keep the two in step.

export function parseJsonc(text: string): unknown {
	return JSON.parse(stripJsonc(text))
}

function stripJsonc(input: string): string {
	let out = ""
	let inString = false
	let escape = false

	for (let index = 0; index < input.length; index += 1) {
		const char = input[index] ?? ""
		const next = input[index + 1]

		if (inString) {
			out += char
			if (escape) {
				escape = false
			} else if (char === "\\") {
				escape = true
			} else if (char === '"') {
				inString = false
			}
			continue
		}

		if (char === '"') {
			inString = true
			out += char
			continue
		}

		if (char === "/" && next === "/") {
			index += 1
			while (index + 1 < input.length && input[index + 1] !== "\n") {
				index += 1
			}
			continue
		}

		if (char === "/" && next === "*") {
			index += 2
			while (
				index < input.length &&
				!(input[index] === "*" && input[index + 1] === "/")
			) {
				index += 1
			}
			index += 1
			continue
		}

		out += char
	}

	return out
}
