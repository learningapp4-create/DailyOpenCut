// Strip // and /* */ comments from JSONC without touching strings.
// Shared by the preset loader and the preview renderer.

export function parseJsonc(text) {
	return JSON.parse(stripJsonc(text));
}

export function stripJsonc(input) {
	let out = "";
	let inString = false;
	let escape = false;

	for (let index = 0; index < input.length; index += 1) {
		const char = input[index];
		const next = input[index + 1];

		if (inString) {
			out += char;
			if (escape) {
				escape = false;
			} else if (char === "\\") {
				escape = true;
			} else if (char === '"') {
				inString = false;
			}
			continue;
		}

		if (char === '"') {
			inString = true;
			out += char;
			continue;
		}

		if (char === "/" && next === "/") {
			index += 1;
			while (index + 1 < input.length && input[index + 1] !== "\n") {
				index += 1;
			}
			continue;
		}

		if (char === "/" && next === "*") {
			index += 2;
			while (
				index < input.length &&
				!(input[index] === "*" && input[index + 1] === "/")
			) {
				index += 1;
			}
			index += 1;
			continue;
		}

		out += char;
	}

	return out;
}
