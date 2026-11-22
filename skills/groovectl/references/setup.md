# CLI installation and authentication

Read for a new machine, missing prerequisites, or authentication failure. The host needs shell execution and network access. This skill does not bundle Node.js, groovectl, or credentials.

## 1. Install Node.js and npm

Run `node --version` and `npm --version` in the terminal/environment the agent uses. Require Node.js **24 or newer**. If missing or older, install a supported Node.js LTS version >=24 from [nodejs.org](https://nodejs.org/en/download), following the macOS, Linux, or Windows instructions. Include npm when offered. Open a new terminal and repeat both checks. Have the user complete any interactive installer or device-privilege step.

## 2. Install the published CLI

The validated baseline is the public npm release `groovectl@0.2.0`:

```sh
npm install --global groovectl@0.2.0
groovectl version --json
groovectl schema --compact
```

No CLI source checkout, pnpm, TypeScript compiler, `node dist/...`, or npm login is needed. Skill installation is separate and documented in the repository README.

On Windows PowerShell, use `.cmd` shims if `.ps1` execution is blocked:

```powershell
npm.cmd install --global groovectl@0.2.0
groovectl.cmd version --json
groovectl.cmd schema --compact
```

If installed but not found, inspect `npm prefix --global`. Its `bin` subdirectory must be on PATH on macOS/Linux; the prefix itself must be on PATH on Windows. Add it using the user's shell/system settings, reopen the terminal, and repeat the version check. Restart the agent host if it still has an old PATH. A successful npm install alone does not prove the agent can run the command.

For permissions errors, use a user-owned Node installation or npm prefix rather than changing system ownership. An optional isolated prefix on macOS/Linux is:

```sh
npm install --global --prefix "$HOME/.local" groovectl@0.2.0
export PATH="$HOME/.local/bin:$PATH"
groovectl version --json
```

Persist PATH in shell configuration only when requested. Alternatively, run without a global installation:

```sh
npm exec --yes --package=groovectl@0.2.0 -- groovectl version --json
```

In that mode, replace the leading `groovectl` in subsequent examples with `npm exec --yes --package=groovectl@0.2.0 -- groovectl`. On Windows use `npm.cmd exec`. Uncached invocations download npm code; this is not offline mode. Do not repeatedly attempt installation on network/permissions failures: report the actual failing step and recovery needed.

## 3. Authenticate only when needed

- **Anonymous OK**: `release get`, `release rating get` (community), `master get|versions`, `artist get|releases`, `label get|releases`, `user profile <username>`, `list ls <username>`, `list get <id>` (public lists), `marketplace stats`, `marketplace listing get`, `marketplace fee`, `marketplace inventory <username>` (public `"For Sale"` items), and `marketplace listings` (website reader — never uses tokens or cookies). Note that Discogs may still require authentication for specific Marketplace API requests.
- **User Token required**: `search`, `release rating get --mine|set|remove`, all `collection` and `wantlist` commands, `user profile` / `list ls` / `marketplace inventory` without `[username]`, `marketplace price-suggestions` (also requires Discogs seller settings), `marketplace listing create|update|delete`, and all `marketplace orders` commands.
- An npm token is not a Discogs token.

1. Have the user sign into Discogs and open [Settings → Developers](https://www.discogs.com/settings/developers) to generate a personal User Token.
2. Have them run this in their **own interactive terminal**, entering the token at the hidden prompt:

   ```sh
   groovectl --token auth login
   groovectl auth status --json
   ```

3. Check `authenticated: true` and the intended username. Login validates before saving to the OS credential store. Never ask the user to paste the token into chat or read it from the credential store yourself. On Windows substitute `groovectl.cmd` if needed.
4. Run `groovectl auth status --json` again in the agent environment before the dependent account operation. Another OS user/container's login does not automatically authenticate this environment.

Resolution order: `--token-stdin`, `DISCOGS_TOKEN`, explicit `--token` hidden prompt, then saved OS credential. `--token` is a boolean prompt switch, **not** `--token <secret>`. An environment token overrides saved credentials even during `auth login`. For a stale override, have the user remove it in the environment launching the agent before retrying. Never print its value.

On headless Linux or without an accessible OS credential store, have the user inject `DISCOGS_TOKEN` through the host's secret/environment mechanism before starting the agent. The CLI consumes it without saving it. Alternatively a trusted secret source may feed `--token-stdin`. Do not put a literal secret in shell history, a repo `.env` file, or command arguments. Do not start an interactive token prompt in a noninteractive agent process; stop dependent work until credentials are available. Never send a token to a custom API base URL.

For automation or AI agent callers, you can also set `GROOVECTL_ERROR_FORMAT=json` (or pass `--error-format json`) so stderr errors are always valid JSON.

`auth logout` deletes only the saved credential, not an environment token or server-side token. Revoke through Discogs settings when requested.

## 4. Verify readiness

```sh
groovectl schema --compact
groovectl release get 249504 --json
groovectl auth status --json
```

`schema --compact` verifies the CLI offline. The release command verifies a real public read when the API is reachable. Anonymous status is acceptable for public reads, not search/account/seller workflows. A 403, rate limit, or network failure is not successful connectivity; follow [commands.md](commands.md#error-handling).

## Maintenance

Upgrade only when requested, then verify version and schema:

```sh
npm install --global groovectl@latest
groovectl version --json
groovectl schema --compact
```

Uninstall CLI: `npm uninstall --global groovectl`. This does not remove the skill or revoke the Discogs token. The README covers skill removal.

Upstream: [Groovectl](https://github.com/ShiTuoCheng/groovectl), [npm package](https://www.npmjs.com/package/groovectl/v/0.2.0).
