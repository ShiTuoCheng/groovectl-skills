# Validation record

Date: 2026-11-22. Environment: macOS arm64, Node.js v24.4.1, npm 11.5.2.

## Verified

- Registry metadata reports `groovectl` 0.2.0, Node.js >=24, and the `groovectl` executable.
- Installed `groovectl@0.2.0` from the public npm registry into an isolated temporary global prefix. `groovectl version --json` returned `0.2.0` and `groovectl schema --compact` returned all 52 commands. This installation did not use the CLI source checkout.
- `skill-creator/scripts/quick_validate.py skills/groovectl`: passed frontmatter/name/scaffold validation.
- `node --test tests/install-skill.test.mjs`: 4 tests passed. Verified byte-identical copy of all skill resources, paths containing spaces, rejection of malformed options, and preservation of existing files/symlinks.
- `python3 tests/verify-cli.py --cli <isolated-installed-executable>`: all 70 command-reference examples plus `auth status` and `--error-format json` error verification passed (72 commands, 87 loopback HTTP requests plus local HTML fixture parsing). Checked `schema --compact`, enriched `release get` pressing fields (`masterId`, `labels`, `identifiers`), `release rating`, `master versions` server-side filters, `collection folder/fields/note/--query`, `wantlist --query`, `user profile`, `list ls/get`, `marketplace stats` null/blocked preservation, `marketplace price-suggestions` grade ordering, `marketplace inventory`, `marketplace listings --html` filters with clean stderr under `--quiet`, `marketplace listing create|update|delete`, `marketplace orders list|get|update|messages|message`, structured JSON errors on stderr, and no write requests for dry runs.
- Reviewed workflows against the acceptance scenarios in `tests/scenarios.md`: pressing identification, entity disambiguation, custom folders/fields/notes, account authorization, credential handling, pagination/early-stop limits, write recovery, and Marketplace API vs. website boundaries are explicitly covered in the instructions.

## Limits

The loopback API and local HTML file serve synthetic responses. This verifies published-command compatibility and example syntax, not real Discogs availability, live website HTML anti-bot behavior, real-account permissions, or live writes. No real account mutation, live web fetch, or token lookup is needed for these contract tests.

Installer tests ran on macOS. Windows/Linux installation commands and platform-specific paths are documented; execution on those OSes has not been verified in this project. Skill frontmatter checks and instruction review do not prove an agent will always follow the workflows. An independent model/host evaluation of every acceptance scenario has not been run.

## Reproduce

1. Follow README steps 1–2 to install Node.js >=24, npm, and public `groovectl@0.2.0`.
2. From this repository root run `node --test tests/install-skill.test.mjs`.
3. If Python 3 is installed, run `python3 tests/verify-cli.py`. Use `--cli` for an isolated executable.
4. If the Codex skill-creator validator is available, run `python3 <skill-creator-directory>/scripts/quick_validate.py skills/groovectl`.
5. For agent-level behavior, run the scenarios with the skill loaded and capture actual command traces. Use simulated/disposable accounts for writes.
