import argparse
import http.server
import json
import os
import pathlib
import re
import shlex
import shutil
import subprocess
import tempfile
import threading

repo = pathlib.Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(
    description="Check documented commands against the published CLI and local loopback/HTML fixtures, never a real Discogs account."
)
parser.add_argument(
    "--cli",
    default=shutil.which("groovectl"),
    help="Path to the installed groovectl executable (defaults to PATH)",
)
options = parser.parse_args()
if not options.cli:
    parser.error(
        "groovectl not found; follow README.md CLI installation steps or pass --cli"
    )
binpath = str(pathlib.Path(options.cli).resolve())

requests = []
base = "https://api.discogs.com"
basic = {
    "id": 249504,
    "title": "Fixture Album",
    "resource_url": f"{base}/releases/249504",
    "year": 1959,
    "artists": [{"name": "Fixture Artist"}],
    "formats": [{"name": "Vinyl", "qty": "1", "descriptions": ["LP", "Album"], "text": "180g"}],
    "labels": [{"name": "CBS/Sony", "catno": "25AP 755"}],
}
release_detail = {
    **basic,
    "master_id": 5460,
    "released": "1978",
    "released_formatted": "1978",
    "country": "Japan",
    "status": "Accepted",
    "data_quality": "Correct",
    "companies": [{"name": "CBS/Sony Inc.", "entity_type_name": "Manufactured By", "catno": ""}],
    "identifiers": [{"type": "Matrix / Runout", "value": "25AP-755A1", "description": "Side A"}],
    "tracklist": [{"position": "A1", "title": "So What", "duration": "9:22", "type_": "track"}],
    "notes": "Includes OBI strip and Japanese insert.",
    "genres": ["Jazz"],
    "styles": ["Modal"],
    "community": {"have": 840, "want": 312, "rating": {"count": 120, "average": 4.8}},
    "lowest_price": 45.0,
    "num_for_sale": 12,
    "uri": "https://www.discogs.com/release/249504",
}
item = {
    "id": 249504,
    "instance_id": 123456,
    "folder_id": 1,
    "rating": 5,
    "date_added": "2026-01-01T00:00:00Z",
    "notes": [{"field_id": 3, "value": "With OBI"}],
    "basic_information": basic,
}
want = {
    "id": 249504,
    "rating": 5,
    "notes": "Blue Note / Fixture notes",
    "resource_url": f"{base}/users/fixture-user/wants/249504",
    "basic_information": basic,
}
pagination = {"page": 1, "pages": 1, "items": 1, "per_page": 50, "urls": {}}
listing_obj = {
    "id": 123456789,
    "status": "For Sale",
    "price": {"value": 45, "currency": "EUR"},
    "original_price": {"value": 45, "curr_abbr": "EUR"},
    "shipping_price": {},
    "condition": "Near Mint (NM or M-)",
    "sleeve_condition": "Very Good Plus (VG+)",
    "comments": "Clean copy",
    "allow_offers": True,
    "location": "Shelf A1",
    "weight": 260,
    "format_quantity": 1,
    "ships_from": "United Kingdom",
    "seller": {"username": "fixture-seller", "stats": {"rating": "99.5"}},
    "release": {
        "id": 249504,
        "description": "Fixture Artist - Fixture Album",
        "artist": "Fixture Artist",
        "title": "Fixture Album",
        "format": "LP, Album",
        "catalog_number": "25AP 755",
        "year": 1978,
    },
    "resource_url": f"{base}/marketplace/listings/123456789",
    "uri": "https://www.discogs.com/sell/item/123456789",
}
order_obj = {
    "id": "12345-1",
    "status": "Payment Received",
    "next_status": ["Shipped"],
    "created": "2026-10-10T10:00:00Z",
    "last_activity": "2026-10-10T12:00:00Z",
    "archived": False,
    "buyer": {"id": 99, "username": "vinyl-buyer"},
    "seller": {"id": 1, "username": "fixture-user"},
    "items": [
        {
            "id": 123456789,
            "release": {"id": 249504, "description": "Fixture Artist - Fixture Album"},
            "price": {"value": 45, "currency": "USD"},
        }
    ],
    "shipping": {"value": 5, "currency": "USD", "method": "Standard"},
    "fee": {"value": 4.05, "currency": "USD"},
    "total": {"value": 50, "currency": "USD"},
    "shipping_address": "123 Vinyl St",
    "additional_instructions": "Pack outside sleeve",
    "resource_url": f"{base}/marketplace/orders/12345-1",
    "uri": "https://www.discogs.com/sell/order/12345-1",
}
order_msg_obj = {
    "type": "message",
    "subject": "Order update",
    "message": "Shipped today",
    "timestamp": "2026-10-11T08:00:00Z",
    "from": {"username": "fixture-user"},
}

html_fixture = """<!doctype html>
<html>
  <head><title>Marketplace Release 249504</title></head>
  <body>
    <a href="/sell/release/249504">Release 249504</a>
    <strong class="pagination_total">1 – 1 of 1</strong>
    <table>
      <tbody>
        <tr data-release-id="249504">
          <td class="item_description">
            <a class="item_description_title" href="/sell/item/123456789">Fixture Album</a>
            <p class="item_condition">
              <span class="mplabel">Media Condition:</span>
              Very Good Plus (VG+)
              <span class="item_sleeve_condition">Very Good Plus (VG+)</span>
            </p>
            <p class="hide_mobile">Clean copy with OBI.</p>
          </td>
          <td class="seller_info">
            <ul>
              <li><a href="/seller/fixture-seller">fixture-seller</a></li>
              <li><strong>99.5%</strong> <a href="/sell/seller_feedback/fixture-seller">1,234 ratings</a></li>
              <li>Ships From: United Kingdom</li>
            </ul>
          </td>
          <td class="item_price">
            <span class="price" data-pricevalue="80.00" data-currency="GBP">£80.00</span>
            <span class="item_shipping">+ £10.00 shipping</span>
          </td>
          <td class="item_add_to_cart">Add to Cart</td>
        </tr>
      </tbody>
    </table>
  </body>
</html>
"""


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def respond(self):
        path = self.path.split("?")[0]
        requests.append((self.command, path))
        data = None
        status = 200

        if self.command == "DELETE":
            status = 204
        elif path == "/oauth/identity":
            data = {
                "id": 1,
                "username": "fixture-user",
                "resource_url": f"{base}/users/fixture-user",
            }
        elif path == "/releases/249504":
            data = release_detail
        elif path == "/releases/249504/rating":
            data = {"release_id": 249504, "rating": {"count": 120, "average": 4.8}}
        elif path == "/releases/249504/rating/fixture-user":
            data = {"username": "fixture-user", "release_id": 249504, "rating": 5}
        elif path == "/database/search":
            data = {
                "pagination": pagination,
                "results": [
                    {
                        "id": 249504,
                        "master_id": 5460,
                        "type": "release",
                        "title": "Fixture Artist - Fixture Album",
                        "country": "Japan",
                        "year": "1978",
                        "format": ["Vinyl"],
                        "label": ["CBS/Sony"],
                        "catno": "25AP 755",
                        "barcode": ["07464081631"],
                        "resource_url": f"{base}/releases/249504",
                    }
                ],
            }
        elif path == "/masters/5460":
            data = {
                "id": 5460,
                "title": "Fixture Album",
                "year": 1959,
                "main_release": 249504,
                "resource_url": f"{base}{path}",
                "uri": "https://www.discogs.com/master/5460",
            }
        elif path == "/masters/5460/versions":
            data = {
                "pagination": pagination,
                "versions": [
                    {
                        "id": 249504,
                        "title": "Fixture Album",
                        "label": "CBS/Sony",
                        "country": "Japan",
                        "released": "1978",
                        "major_formats": ["Vinyl"],
                        "format": "LP, Album",
                        "catno": "25AP 755",
                        "status": "Accepted",
                        "stats": {"community": {"in_collection": 840, "in_wantlist": 312}},
                        "resource_url": f"{base}/releases/249504",
                    }
                ],
            }
        elif path in ["/artists/45", "/labels/1"]:
            data = {
                "id": int(path.rsplit("/", 1)[1]),
                "name": "Fixture",
                "resource_url": f"{base}{path}",
                "uri": f"https://www.discogs.com{path}",
            }
        elif path in ["/artists/45/releases", "/labels/1/releases"]:
            data = {
                "pagination": pagination,
                "releases": [
                    {
                        "id": 249504,
                        "title": "Fixture Album",
                        "type": "release",
                        "artist": "Fixture Artist",
                        "role": "Main",
                        "resource_url": f"{base}/releases/249504",
                    }
                ],
            }
        elif path.endswith("/collection/folders"):
            if self.command == "POST":
                status = 201
                data = {
                    "id": 2,
                    "count": 0,
                    "name": "Japanese Pressings",
                    "resource_url": f"{base}{path}/2",
                }
            else:
                data = {
                    "folders": [
                        {"id": 0, "count": 1, "name": "All", "resource_url": f"{base}{path}/0"},
                        {"id": 1, "count": 1, "name": "Uncategorized", "resource_url": f"{base}{path}/1"},
                        {"id": 2, "count": 0, "name": "Japanese Pressings", "resource_url": f"{base}{path}/2"},
                    ]
                }
        elif re.search(r"/collection/folders/\d+$", path):
            folder_id = int(path.rsplit("/", 1)[1])
            data = {
                "id": folder_id,
                "count": 0,
                "name": "Japan OBI Vinyl" if self.command == "POST" else "Japanese Pressings",
                "resource_url": f"{base}{path}",
            }
        elif path.endswith("/collection/fields"):
            data = {
                "fields": [
                    {
                        "id": 1,
                        "name": "Media Condition",
                        "type": "dropdown",
                        "position": 1,
                        "public": True,
                        "options": ["Mint (M)", "Near Mint (NM or M-)", "Very Good Plus (VG+)"],
                    },
                    {"id": 3, "name": "Notes", "type": "textarea", "position": 3, "lines": 3, "public": False},
                ]
            }
        elif "/instances/" in path:
            status = 204
        elif path.endswith("/collection/value"):
            data = {"minimum": "$1.00", "median": "$2.00", "maximum": "$3.00"}
        elif "/collection/" in path:
            if self.command == "POST":
                status = 201
                data = {"instance_id": 123456, "resource_url": f"{base}{path}/instances/123456"}
            else:
                data = {"pagination": pagination, "releases": [item]}
        elif path.endswith("/wants"):
            data = {"pagination": pagination, "wants": [want]}
        elif "/wants/" in path:
            data = want
        elif path in ["/users/fixture-user", "/users/some-collector"]:
            username = path.rsplit("/", 1)[1]
            data = {
                "id": 1 if username == "fixture-user" else 2,
                "username": username,
                "name": "Fixture Collector",
                "curr_abbr": "USD",
                "num_collection": 10,
                "num_wantlist": 5,
                "num_for_sale": 1,
                "num_lists": 1,
                "resource_url": f"{base}{path}",
                "uri": f"https://www.discogs.com/user/{username}",
            }
        elif path.endswith("/lists"):
            data = {
                "pagination": pagination,
                "lists": [
                    {
                        "id": 55,
                        "name": "Essential Jazz",
                        "description": "Core pressings",
                        "public": True,
                        "resource_url": f"{base}/lists/55",
                        "uri": "https://www.discogs.com/lists/Essential-Jazz/55",
                    }
                ],
            }
        elif path == "/lists/55":
            data = {
                "id": 55,
                "name": "Essential Jazz",
                "description": "Core pressings",
                "public": True,
                "resource_url": f"{base}/lists/55",
                "items": [
                    {
                        "id": 249504,
                        "type": "release",
                        "display_title": "Fixture Artist - Fixture Album",
                        "comment": "Favorite pressing",
                        "uri": "/release/249504",
                        "resource_url": f"{base}/releases/249504",
                    }
                ],
            }
        elif "/marketplace/stats/" in path:
            data = {"lowest_price": None, "num_for_sale": None, "blocked_from_sale": True}
        elif "/marketplace/price_suggestions/" in path:
            data = {
                "Very Good Plus (VG+)": {"value": 45.0, "currency": "USD"},
                "Near Mint (NM or M-)": {"value": 80.0, "currency": "USD"},
            }
        elif path.endswith("/inventory"):
            data = {"pagination": pagination, "listings": [listing_obj]}
        elif path == "/marketplace/listings" and self.command == "POST":
            status = 201
            data = {
                "listing_id": 123456789,
                "resource_url": f"{base}/marketplace/listings/123456789",
            }
        elif "/marketplace/listings/" in path:
            if self.command == "POST":
                status = 204
            else:
                data = listing_obj
        elif path == "/marketplace/orders":
            data = {"pagination": pagination, "orders": [order_obj]}
        elif path == "/marketplace/orders/12345-1":
            data = {**order_obj, "status": "Shipped"} if self.command == "POST" else order_obj
        elif path == "/marketplace/orders/12345-1/messages":
            if self.command == "POST":
                status = 201
                data = order_msg_obj
            else:
                data = {"pagination": pagination, "messages": [order_msg_obj]}
        elif "/marketplace/fee/" in path:
            data = {"value": 4.05, "currency": "USD"}
        else:
            status = 404
            data = {"message": f"Unexpected fixture route: {self.command} {path}"}

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if status != 204:
            self.wfile.write(json.dumps(data).encode())

    do_GET = respond
    do_POST = respond
    do_PUT = respond
    do_DELETE = respond


server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()

with tempfile.TemporaryDirectory(prefix="groovectl-skill-fixture-") as config:
    html_path = pathlib.Path(config) / "saved-page.html"
    html_path.write_text(html_fixture, encoding="utf-8")
    env = {
        **os.environ,
        "NODE_ENV": "test",
        "GROOVECTL_CONFIG_DIR": config,
        "GROOVECTL_API_BASE_URL": f"http://127.0.0.1:{server.server_port}",
        "DISCOGS_TOKEN": "synthetic-fixture-token-not-a-user-secret",
    }
    doc = (repo / "skills/groovectl/references/commands.md").read_text(encoding="utf-8")
    raw_commands = [
        line
        for block in re.findall(r"```sh\n(.*?)```", doc, re.S)
        for line in block.splitlines()
        if line.startswith("groovectl ")
    ]
    commands = []
    for line in raw_commands:
        if "marketplace listings " in line:
            if "--html" in line:
                commands.append(line.replace("/path/to/saved-page.html", str(html_path)))
            else:
                # Never hit live discogs.com in offline contract tests; validate all filter flags against the saved HTML fixture.
                offline = re.sub(r"\s+--sort\s+\S+", "", line)
                offline = re.sub(r"\s+--all\b", "", offline)
                commands.append(f'{offline} --html "{html_path}"')
        else:
            commands.append(line)
    commands.append("groovectl auth status --json")

    for line in commands:
        args = shlex.split(line)[1:]
        before = len(requests)
        p = subprocess.run(
            [binpath, *args], env=env, text=True, capture_output=True, timeout=20
        )
        assert p.returncode == 0, (line, p.returncode, p.stderr)
        if "--dry-run" in args:
            assert all(method == "GET" for method, _ in requests[before:]), line
            assert json.loads(p.stdout)["dryRun"] is True
        if "--json" in args:
            result = json.loads(p.stdout)
        if args[:2] == ["schema", "--compact"]:
            schema = json.loads(p.stdout)
            assert schema["name"] == "groovectl" and len(schema["commands"]) >= 50
        if args[:2] == ["release", "get"]:
            assert result["masterId"] == 5460
            assert result["identifiers"][0]["value"] == "25AP-755A1"
            assert result["labels"][0]["catalogNumber"] == "25AP 755"
        if args[:2] == ["marketplace", "stats"]:
            assert (
                result["lowestPrice"] is None
                and result["numForSale"] is None
                and result["blockedFromSale"] is True
            )
        if args[:2] == ["marketplace", "price-suggestions"]:
            assert [row["grade"] for row in result] == ["NM", "VG+"]
        if args[:2] == ["collection", "contains"]:
            assert isinstance(result, list) and result[0]["instanceId"] == 123456
        if "listings" in args and "--html" in args:
            assert p.stderr == ""
            assert isinstance(result, list) and result[0]["id"] == 123456789
            assert result[0]["source"] == "html"
        print("PASS", line)

    # Also verify structured JSON error output on stderr (including missing subcommand)
    err_proc = subprocess.run(
        [binpath, "--error-format", "json", "marketplace"],
        env=env,
        text=True,
        capture_output=True,
        timeout=20,
    )
    assert err_proc.returncode == 2
    assert err_proc.stdout == ""
    err_payload = json.loads(err_proc.stderr)
    assert err_payload["error"]["code"] == "GROOVECTL_USAGE"
    assert err_payload["error"]["exitCode"] == 2
    print("PASS groovectl --error-format json marketplace (exit 2 structured JSON error)")

    print(
        f"VALIDATED {len(commands) + 1} commands against isolated loopback/HTML fixtures; {len(requests)} local HTTP requests."
    )

server.shutdown()
