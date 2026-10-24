# Validation record

Date: 2026-10-24. Environment: macOS arm64, Node.js v24.4.1, npm 11.5.2.

## Verified

- Registry metadata reports `groovectl` 0.1.1, Node.js >=24, and the `groovectl` executable.
- Installed `groovectl@0.1.1` from the public npm registry into an isolated temporary global prefix. `groovectl version --json` returned 0.1.1 and root help succeeded. This installation did not use the CLI source checkout.
- `skill-creator/scripts/quick_validate.py skills/groovectl`: passed frontmatter/name/scaffold validation.
- `node --test tests/install-skill.test.mjs`: 4 tests passed. Verified byte-identical copy of all skill resources, paths containing spaces, rejection of malformed options, and preservation of existing files/symlinks.
- `python3 tests/verify-cli.py --cli <isolated-installed-executable>`: all 29 command-reference examples plus auth status passed (30 commands, 43 loopback HTTP requests). Checked structured output, the array of collection instances, actual `blockedFromSale` field name, preservation of null market values, and no write requests for dry runs.
- Reviewed workflows against the acceptance scenarios in `tests/scenarios.md`: entity disambiguation, account authorization, credential handling, pagination, write recovery, and Marketplace boundaries are explicitly covered in the instructions.

## Limits

The loopback API serves synthetic responses. This verifies published-command compatibility and example syntax, not real Discogs availability, real-account permissions, or live writes. No real account mutation or token lookup is needed for these contract tests.

Installer tests ran on macOS. Windows/Linux installation commands and platform-specific paths are documented; execution on those OSes has not been verified in this project. Skill frontmatter checks and instruction review do not prove an agent will always follow the workflows. An independent model/host evaluation of every acceptance scenario has not been run.

## Reproduce

1. Follow README steps 1–2 to install Node.js >=24, npm, and public `groovectl@0.1.1`.
2. From this repository root run `node --test tests/install-skill.test.mjs`.
3. If Python 3 is installed, run `python3 tests/verify-cli.py`. Use `--cli` for an isolated executable.
4. If the Codex skill-creator validator is available, run `python3 <skill-creator-directory>/scripts/quick_validate.py skills/groovectl`.
5. For agent-level behavior, run the scenarios with the skill loaded and capture actual command traces. Use simulated/disposable accounts for writes.
