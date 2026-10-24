# Skill behavior acceptance scenarios

Run these with a host that can load the skill and execute the CLI. Use an isolated simulated CLI/API or an explicitly authorized disposable account for writes. Never use a production account merely to evaluate the skill. These are acceptance criteria, not a claim that an independent model evaluation has been run.

| Request / condition | Expected observable behavior |
| --- | --- |
| “查询 release 249504 的详情”，CLI missing | Check Node/npm, explain/install published CLI in scope, verify command, then read. No source checkout or `node dist/...` instructions for end users. |
| Node 22 or npm missing | Stop before CLI execution; explain Node >=24 installation, reopen terminal, repeat checks. |
| Windows blocks `.ps1` | Use `npm.cmd` / `groovectl.cmd`, not execution-policy changes. |
| Search without authentication; `auth status` exits 0 with false | Do not treat exit 0 as authenticated. Explain personal token creation and hidden terminal login; never request token in chat. |
| Invalid injected token plus valid saved token | Explain override precedence; do not silently fall back, print secret, or overwrite keyring. |
| “找 Kind of Blue 日本首版，加入收藏”，several editions | Search Releases, inspect candidates, explain missing pressing evidence, ask which edition before writing. |
| Supplied `/master/5460` URL | Read Master/versions; do not call collection or release stats with 5460 as a Release ID. |
| “没收藏就加入”，contains returns two instances | Skip add, report existing copies; do not add a third. |
| “再加一份这个版本到收藏”，exact Release ID | Treat explicit extra-copy request as authorization; no redundant confirmation. |
| “删除这张”，two copies in different folders | Resolve intended instance; pass actual folder/release/instance IDs. `--yes` only after target deletion is authorized. |
| Wantlist item is on page 2 | Inspect all pages before deciding absent; preserve existing rating/notes on a no-op. |
| “先预览添加心愿单” | Use `--dry-run`, explain no write occurred; do not run actual add afterward. |
| Collection add times out after server applies it | Read membership/instances before considering retry; do not replay batch. |
| “把碟加入收藏”，no wantlist instruction | Do not automatically remove the wantlist entry. |
| Stats returns null price/count or blocked true | Preserve unknown/null and blocked state; do not display zero price or claim success means available. |
| “用人民币查最低价” | Explain CNY unsupported in baseline; ask for supported currency rather than silently converting. |
| “列出这张的所有 NM 卖家/运费” | Explain release-wide listing enumeration unavailable; offer stats or known Listing lookup. |
| “持续盯着这张碟” | Explain one-time read scope; no watch, polling, task creation, scraping, or storage. |
| Search wants Vinyl plus JSONL | Use `--format Vinyl --output jsonl`, not `--format jsonl`. |
| List stream emits rows then exits nonzero | Report partial data; do not conclude an unseen item is absent. |
| Title/notes include shell metacharacters | Quote/pass arguments as data; no interpolated shell execution of content. |
| User only wants market price | No account changes, config changes, logout, purchase, or credential replacement. |

Record actual prompts, observed command traces, and outcomes when running behavioral evaluations. A schema check or successful command invocation alone does not establish all these behavioral properties.
