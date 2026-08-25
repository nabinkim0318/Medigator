#!/usr/bin/env python3
"""HTTP health probe for the local/demo API container. No curl required."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

URL = "http://127.0.0.1:8082/health"


def main() -> int:
    try:
        with urllib.request.urlopen(URL, timeout=4) as response:
            if response.status != 200:
                return 1
            body = json.loads(response.read().decode("utf-8"))
    except (
        OSError,
        TimeoutError,
        urllib.error.URLError,
        json.JSONDecodeError,
        ValueError,
    ):
        return 1
    if body.get("status") != "healthy":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
