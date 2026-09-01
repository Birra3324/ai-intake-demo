#!/usr/bin/env python3
"""POST the three example leads at a running API."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples" / "demo_requests.json"
BASE = os.environ.get("INTAKE_URL", "http://127.0.0.1:8787")
KEY = os.environ.get("API_KEY", "")


def main() -> int:
    leads = json.loads(EXAMPLES.read_text())
    for item in leads:
        req = urllib.request.Request(
            f"{BASE}/api/v1/intake",
            data=json.dumps(item).encode(),
            headers={
                "content-type": "application/json",
                "X-API-Key": KEY,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                print(resp.status, resp.read().decode())
        except urllib.error.HTTPError as exc:
            print(exc.code, exc.read().decode(), file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
