# Command patterns (groovectl 0.1.1)

Use subcommand `--help` for other flags. Resolve the user's actual IDs before writes. These examples are references, not a script to run in full.

## Output and pagination

- Prefer `--json`; it overrides saved output preferences. Records are objects; lists are arrays. Do not combine `--json` with another explicit output selection.
- Resource commands use `--format jsonl|tsv|table|json`. **Search uses `--output` for output; its `--format` filters the medium**, such as Vinyl.
- Lists support `--page 1 --per-page 50` (maximum 100), or `--all` for every page serially. Do not combine `--page` and `--all`. Use JSONL for large complete lists: JSON arrays have a 10,000-record limit. Nonzero exit after streamed rows means a partial result.
- `--fields` accepts top-level keys, not nested paths such as `price.value`. Schemas differ between resources and dry-run/actual mutations; omit projection on writes unless the schema is known.

## Database

```sh
groovectl search --artist "Miles Davis" --release-title "Kind of Blue" --type release --country Japan --format Vinyl --json
groovectl search "Kind of Blue" --type release --all --output jsonl
groovectl release get 249504 --json
groovectl master get 5460 --json
groovectl master versions 5460 --page 1 --per-page 50 --json
groovectl artist get 45 --json
groovectl artist releases 45 --page 1 --json
groovectl label get 1 --json
groovectl label releases 1 --page 1 --json
```

Search supports artist, release title, country, year, format, label, catalog number (`--catno`), barcode, and other filters. Check each result's `type`. Returned records are CLI-normalized objects; inspect actual JSON instead of assuming raw API names.

## Collection

All commands use the token's identity. Arbitrary usernames are unsupported.

```sh
groovectl collection folders --json
groovectl collection list --folder 0 --sort added --sort-order desc --all --format jsonl
groovectl collection contains 249504 --json
groovectl collection value --json
```

For authorized changes, replace example IDs, especially instance ID 123456:

```sh
groovectl collection add 249504 --folder 1 --dry-run --json
groovectl collection add 249504 --folder 1 --json
groovectl collection update 1 249504 123456 --rating 5 --dry-run --json
groovectl collection update 1 249504 123456 --rating 5 --move-to 2 --json
groovectl collection remove 1 249504 123456 --dry-run --json
groovectl collection remove 1 249504 123456 --yes --json
```

Update/remove arguments: **current folder ID, Release ID, instance ID**, in that order. `--move-to` is the destination. Folder 0 is the aggregate read view, not a guessed current folder; use returned `folderId`. Rating is an integer 0–5. Retain a new add's `instanceId` for verification and later changes.

## Wantlist

```sh
groovectl wantlist list --all --format jsonl
groovectl wantlist add 249504 --rating 5 --notes "Prefer a clean copy" --dry-run --json
groovectl wantlist add 249504 --rating 5 --notes "Prefer a clean copy" --json
groovectl wantlist update 249504 --notes "Japanese edition preferred" --json
groovectl wantlist remove 249504 --dry-run --json
groovectl wantlist remove 249504 --yes --json
```

Read all pages to check membership. Add/update can set rating/notes; preserve preferences the user did not request to change. Update requires `--rating` and/or `--notes`.

## Marketplace (read only)

```sh
groovectl marketplace stats 249504 --currency USD --json
groovectl marketplace stats 249504 --currency USD --fields releaseId,lowestPrice,numForSale,blockedFromSale --json
groovectl marketplace listing get 123456789 --currency EUR --json
groovectl marketplace fee 45.00 --currency USD --json
```

The Listing ID is a placeholder; obtain one from a supplied `/sell/item/<id>` URL. `stats` accepts a Release ID. Its fields include `lowestPrice`, `numForSale`, and `blockedFromSale`. Money is `{ value, currency }`; missing data stays `null`. Out of stock/blocked are data outcomes. Missing listings are not-found errors. Seller condition/details come only from a known listing, not all offers.

Supported currencies: USD, GBP, EUR, CAD, AUD, JPY, CHF, MXN, BRL, NZD, SEK, ZAR. CNY is unsupported in this baseline. Omission uses Discogs defaults; label the returned currency. Do not compare nominal amounts across currencies. Fee quotes come from the API; pass nonnegative decimal prices (`45.00`), without currency signs or scientific notation. Neither lowest item price nor fee quote is a landed purchase cost.

## Error handling

Inspect exit status and stderr; `--json` does not guarantee JSON errors.

| Exit | Meaning | Next action |
| --- | --- | --- |
| 2 | Usage/validation | Read subcommand help; correct arguments, not unchanged retries. |
| 3 | Authentication required/invalid | Follow setup. Supply credentials for `GROOVECTL_AUTH_REQUIRED`; correct invalid credentials rather than silently discarding them. |
| 4 | Forbidden | Report denied access; do not scrape or change endpoints to evade it. |
| 5 | Not found | Recheck entity type and ID; report missing content when appropriate. |
| 6 | Rate limited | Stop batch; report limit and returned delay if available. Do not poll. |
| 7 | Upstream/unexpected | Report failure; read state before retrying writes. Keyring unavailability may need setup recovery. |
| 8 | Network | Report connectivity failure; determine whether a write applied before retrying it. |
| 10 | Cancelled/confirmation needed | Respect cancellation; `--yes` is only for an already authorized removal. |

The CLI retries selected GET failures within bounds; writes are never automatically retried. Incomplete reads do not prove absence; ambiguous write failures do not prove nothing changed.
