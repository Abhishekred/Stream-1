#!/usr/bin/env python3
"""Verify upstream CloudStream extension assets and prepare the test-builds branch."""
import hashlib
import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

OWNER_REPO = "Abhishekred/Stream-1"
UPSTREAM_PREFIX = "https://raw.githubusercontent.com/phisher98/cloudstream-extensions-phisher/builds/"
PUBLISH_PREFIX = f"https://raw.githubusercontent.com/{OWNER_REPO}/test-builds/"
OUT = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "stream-1-test-builds"

plugins = json.loads(Path("plugins.json").read_text(encoding="utf-8"))
if not isinstance(plugins, list) or not plugins:
    raise RuntimeError("plugins.json must contain a nonempty array")

OUT.mkdir(parents=True, exist_ok=True)
seen = set()
published = []

for plugin in plugins:
    source_url = plugin.get("url", "")
    if not isinstance(source_url, str) or not source_url.startswith(UPSTREAM_PREFIX):
        raise RuntimeError(f"Unapproved source URL: {source_url}")

    parsed = urllib.parse.urlparse(source_url)
    filename = urllib.parse.unquote(parsed.path.rsplit("/", 1)[-1])
    if not re.fullmatch(r"[A-Za-z0-9_.-]+\.cs3", filename) or filename in seen:
        raise RuntimeError(f"Invalid or duplicate extension filename: {filename}")
    seen.add(filename)

    request = urllib.request.Request(source_url, headers={"User-Agent": "Stream-1-test-build-sync"})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read(25 * 1024 * 1024 + 1)
    if len(data) > 25 * 1024 * 1024:
        raise RuntimeError(f"Extension too large: {filename}")

    expected_hash = plugin.get("fileHash", "")
    digest = hashlib.sha256(data).hexdigest()
    if expected_hash and expected_hash.lower() != f"sha256-{digest}":
        raise RuntimeError(f"SHA-256 checksum mismatch for {filename}")

    expected_size = plugin.get("fileSize")
    if isinstance(expected_size, int) and expected_size > 0 and expected_size != len(data):
        raise RuntimeError(f"File-size mismatch for {filename}")

    (OUT / filename).write_bytes(data)
    entry = dict(plugin)
    entry["url"] = PUBLISH_PREFIX + urllib.parse.quote(filename)
    entry["fileHash"] = f"sha256-{digest}"
    entry["fileSize"] = len(data)
    published.append(entry)
    print(f"Verified {filename} ({len(data)} bytes)")

(OUT / "plugins.json").write_text(
    json.dumps(published, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
(OUT / "repo.json").write_text(
    json.dumps({
        "name": "Stream-1 Test Builds",
        "iconUrl": f"https://raw.githubusercontent.com/{OWNER_REPO}/main/Icons/RepoIcon.png",
        "description": "Test build mirror for Stream-1 CloudStream extensions",
        "manifestVersion": 1,
        "pluginLists": [PUBLISH_PREFIX + "plugins.json"]
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(f"Prepared {len(published)} verified extensions for test-builds")
