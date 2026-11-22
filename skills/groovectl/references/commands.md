# Command patterns (groovectl 0.2.0)

Use `groovectl schema [command...] [--compact]` (or subcommand `--help`) to inspect exact flags and choices offline. Resolve the user's actual IDs before writes. These examples are references, not a script to run in full.

## Output, pagination, and AI ergonomics

- Prefer `--json`; it overrides saved output preferences. Records are objects; lists are arrays. Do not combine `--json` with another explicit `--format` (or `--output` on `search`), including `--format table`.
- Resource commands use `--format table|json|jsonl|tsv`. **Search uses `--output` for output format; its `--format` filters the release medium** (such as Vinyl). **`master versions` uses `--media-format` to filter the medium** alongside `--format` for output.
- Paginated list commands support `--page 1 --per-page 50` (maximum 100), `--all` (every page serially), and `--limit <count>` (stops fetching pages as soon as enough records are emitted). Do not combine `--page` and `--all`. Use `--format jsonl` for large complete lists: JSON arrays cap at 10,000 records. Nonzero exit after streamed rows means a partial result.
- Global options: `--fields id,title,...` selects top-level output keys (not nested paths such as `price.value`; omit on writes unless the dry-run/result schema is known), `-q`/`--quiet` suppresses informational stderr notices, `--error-format json` (or `GROOVECTL_ERROR_FORMAT=json`) emits structured JSON errors on stderr, `--timeout <ms>` sets per-attempt HTTP timeout, `--verbose` writes sanitized method/path/status/timing diagnostics to stderr.

```sh
groovectl schema --compact
groovectl schema marketplace listings
```

## Database and pressing identification

```sh
groovectl search --artist "Miles Davis" --release-title "Kind of Blue" --type release --country Japan --format Vinyl --limit 10 --json
groovectl search "Kind of Blue" --type release --all --limit 50 --output jsonl
groovectl release get 249504 --currency USD --json
groovectl release rating get 249504 --json
groovectl release rating get 249504 --mine --json
groovectl release rating set 249504 5 --dry-run --json
groovectl release rating set 249504 5 --json
groovectl release rating remove 249504 --dry-run --json
groovectl release rating remove 249504 --yes --json
groovectl master get 5460 --json
groovectl master versions 5460 --country Japan --media-format Vinyl --label "CBS/Sony" --released 1978 --sort released --sort-order asc --limit 20 --json
groovectl artist get 45 --json
groovectl artist releases 45 --sort year --sort-order desc --page 1 --json
groovectl label get 1 --json
groovectl label releases 1 --page 1 --json
```

`search` supports `--artist`, `--title`, `--release-title`, `--credit`, `--anv`, `--label`, `--genre`, `--style`, `--country`, `--year`, `--format` (medium), `--catno`, `--barcode`, `--track`, `--submitter`, `--contributor`, and returns `masterId` and `barcodes`. `release get` returns full pressing details (`masterId`, `released`, `formats` with qty/text, `labels` with `catalogNumber`, `companies`, `identifiers` such as barcode and matrix/runout, `tracklist`, `notes`, `community` stats, `lowestPrice`, `numForSale`). `master versions` includes community `have` and `want` counts.

## Collection

All commands operate on the active token's identity; arbitrary usernames are unsupported.

```sh
groovectl collection folders --json
groovectl collection folder get 2 --json
groovectl collection folder create "Japanese Pressings" --dry-run --json
groovectl collection folder create "Japanese Pressings" --json
groovectl collection folder rename 2 "Japan OBI Vinyl" --dry-run --json
groovectl collection folder rename 2 "Japan OBI Vinyl" --json
groovectl collection folder delete 2 --dry-run --json
groovectl collection folder delete 2 --yes --json
groovectl collection fields --json
groovectl collection note set 1 249504 123456 1 "Very Good Plus (VG+)" --dry-run --json
groovectl collection note set 1 249504 123456 1 "Very Good Plus (VG+)" --json
groovectl collection list --folder 0 --sort added --sort-order desc --all --query "OBI" --limit 50 --format jsonl
groovectl collection contains 249504 --json
groovectl collection value --json
```

For authorized release-instance changes, replace example IDs, especially instance ID `123456`:

```sh
groovectl collection add 249504 --folder 1 --dry-run --json
groovectl collection add 249504 --folder 1 --json
groovectl collection update 1 249504 123456 --rating 5 --dry-run --json
groovectl collection update 1 249504 123456 --rating 5 --move-to 2 --json
groovectl collection remove 1 249504 123456 --dry-run --json
groovectl collection remove 1 249504 123456 --yes --json
```

- Folder `0` is the aggregate read view; folder `1` is Uncategorized (default for `add`). Custom folders have IDs `>= 2`; folders `0` and `1` cannot be renamed or deleted, and `folder delete` requires an empty folder.
- Instance update/remove/note arguments: **current folder ID, Release ID, instance ID** (plus `field-id` and `value` for `note set`, passing `""` to clear). Always inspect `collection fields` to get real field IDs and options.
- `--query` filters locally across the pages read (title, artists, labels, catalog numbers, notes); combine with `--all` to search the full collection. Rating is an integer `0`–`5`. Retain a new `add`'s `instanceId` for verification and later edits.

## Wantlist, user profiles, and lists

```sh
groovectl wantlist list --all --query "Blue Note" --limit 50 --format jsonl
groovectl wantlist add 249504 --rating 5 --notes "Prefer a clean copy" --dry-run --json
groovectl wantlist add 249504 --rating 5 --notes "Prefer a clean copy" --json
groovectl wantlist update 249504 --notes "Japanese edition preferred" --json
groovectl wantlist remove 249504 --dry-run --json
groovectl wantlist remove 249504 --yes --json
groovectl user profile --json
groovectl user profile some-collector --json
groovectl list ls --all --json
groovectl list ls some-collector --json
groovectl list get 55 --json
```

Read all wantlist pages to check membership. Preserve existing wantlist rating/notes when not asked to change them; `wantlist update` requires `--rating` and/or `--notes`. `user profile` and `list ls` default to the authenticated user when `[username]` is omitted and read public accounts when `[username]` is provided.

## Marketplace

### Official API reads (stats, price suggestions, listings, seller inventory, fees)

```sh
groovectl marketplace stats 249504 --currency USD --json
groovectl marketplace stats 249504 --currency USD --fields releaseId,lowestPrice,numForSale,blockedFromSale --json
groovectl marketplace price-suggestions 249504 --json
groovectl marketplace listing get 123456789 --currency EUR --json
groovectl marketplace inventory some-record-shop --status "For Sale" --sort price --sort-order asc --limit 25 --json
groovectl marketplace inventory --all --format jsonl
groovectl marketplace fee 45.00 --currency USD --json
```

- Supported currencies: `USD`, `GBP`, `EUR`, `CAD`, `AUD`, `JPY`, `CHF`, `MXN`, `BRL`, `NZD`, `SEK`, `ZAR` (`CNY` is unsupported). Omission uses Discogs defaults. Money is `{ value, currency }`; missing values remain `null`. Never compare nominal amounts across different currencies or treat item price/fee as landed cost.
- `price-suggestions` returns condition-graded suggested prices ordered `M` down to `P`; requires an authenticated token for an account with seller settings configured.
- `inventory` reads a public seller shop when `[username]` is supplied, or the authenticated seller's own inventory when omitted.

### Release website offers (best-effort HTML/PJAX reader, not official API)

```sh
groovectl --quiet marketplace listings 249504 --ships-from "United Kingdom" --currency GBP --min-media "VG+" --min-sleeve "VG+" --max-price 150 --min-seller-rating 99 --sort price-asc --all --limit 10 --json
groovectl --quiet marketplace listings 249504 --html "/path/to/saved-page.html" --min-media "VG+" --json
```

- Uses the Discogs English Marketplace PJAX route without API tokens, cookies, retries, or redirects. May fail with HTTP 403 / challenge (`GROOVECTL_MARKETPLACE_WEB_BLOCKED`) even when official API access works; fall back to `--html <saved-file>` (max 10 MiB) or official API commands.
- `--max-price` requires `--currency`. `--ships-from` filters the **seller's** country. `--sort` choices: `price-asc`, `price-desc`, `listed-desc`, `listed-asc`, `condition-desc`, `condition-asc`. Grade choices: `P`, `F`, `G`, `G+`, `VG`, `VG+`, `NM`, `M` (unknown/generic sleeves fail `--min-sleeve`). `--html` cannot be combined with `--page`, `--all`, or `--sort`. `--all` caps at 100 pages.
- Offers are not API-verified and exclude shipping/tax (`shippingText` is unverified). Follow up on candidate IDs with `marketplace listing get <listing-id>` when needed.

### Seller listing and order management (authenticated writes & reads)

```sh
groovectl marketplace listing create 249504 --condition VG+ --sleeve-condition VG+ --price 45.00 --allow-offers --dry-run --json
groovectl marketplace listing create 249504 --condition VG+ --sleeve-condition Generic --price 45.00 --status Draft --json
groovectl marketplace listing update 123456789 --price 39.99 --no-allow-offers --dry-run --json
groovectl marketplace listing update 123456789 --price 39.99 --json
groovectl marketplace listing delete 123456789 --dry-run --json
groovectl marketplace listing delete 123456789 --yes --json
groovectl marketplace orders list --status "Payment Received" --sort created --sort-order desc --limit 20 --json
groovectl marketplace orders get 12345-1 --json
groovectl marketplace orders update 12345-1 --status Shipped --shipping 5.00 --dry-run --json
groovectl marketplace orders update 12345-1 --status Shipped --json
groovectl marketplace orders messages 12345-1 --all --json
groovectl marketplace orders message 12345-1 --message "Shipped today" --dry-run --json
groovectl marketplace orders message 12345-1 --message "Shipped today" --json
```

- `listing create` defaults to `--status Draft` for safety; pass `--status "For Sale"` only when explicitly asked to publish live. `--condition` / `--sleeve-condition` accept case-insensitive shorthands (`M`, `NM`, `M-`, `VG+`, `VG`, `G+`, `G`, `F`, `P`) or full Discogs condition names (plus `Generic`, `Not Graded`, `No Cover` for sleeve).
- `listing update` reads the current listing first and merges unchanged seller fields (`location`, `weight`, `external_id`, `format_quantity`, `allow_offers`, `comments`). It refuses to update `Sold`/`Expired` listings unless `--status` is explicitly provided (`GROOVECTL_LISTING_STATUS_REQUIRED`).
- `orders list --archived` includes archived orders. `orders update` requires `--status` and/or `--shipping`; `orders message` requires `--message` and/or `--status`.

## Error handling

Pass `--error-format json` or export `GROOVECTL_ERROR_FORMAT=json` to receive a single JSON object on stderr (`{ "error": { "code", "kind", "message", "remediation", "httpStatus", "exitCode" } }`) for every error, including usage/missing-subcommand errors and website blocks. Without `--error-format json`, stderr uses plain text.

| Exit | Meaning | Next action |
| --- | --- | --- |
| 2 | Usage or validation error | Run `groovectl schema <command...>` or `--help`; fix arguments instead of retrying unchanged. |
| 3 | Authentication required or invalid | Follow [setup.md](setup.md). Supply credentials for `GROOVECTL_AUTH_REQUIRED`; fix invalid credentials rather than silently discarding them. |
| 4 | Forbidden or website blocked | Report denied access. For `GROOVECTL_MARKETPLACE_WEB_BLOCKED`, do not retry or bypass; offer `--html <file>` or official API alternatives. |
| 5 | Not found | Recheck entity type and ID; report missing resource or unknown command path. |
| 6 | Rate limited | Stop batch; report rate limit and returned delay if available. Do not poll. |
| 7 | Upstream, schema, or page-parse error | Report failure; read state before retrying writes. For `GROOVECTL_MARKETPLACE_PAGE_INVALID`, do not treat the page as zero offers. |
| 8 | Network error | Report connectivity failure; read current state to check whether a write applied before retrying. |
| 10 | Cancelled or confirmation required | Respect cancellation; pass `--yes` only after the user authorizes the exact deletion. |

The CLI retries selected official API GET failures within bounds; writes and website HTML reads are never automatically retried. Incomplete reads do not prove absence; ambiguous write failures do not prove nothing changed.
