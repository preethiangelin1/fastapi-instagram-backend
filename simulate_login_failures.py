"""Send deliberately invalid login attempts to exercise the login_failed alert.

Example: ``python simulate_login_failures.py`` sends 20 attempts over 5 minutes
to the API at localhost:8000. The API should be running with Logfire enabled.
"""

from __future__ import annotations

import argparse
import os
import time
import urllib.error
import urllib.parse
import urllib.request


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", default=os.getenv("API_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--username", default="logfire-alert-test-user")
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--duration-seconds", type=float, default=300)
    args = parser.parse_args()

    if args.count < 1:
        parser.error("--count must be at least 1")
    if args.duration_seconds < 0:
        parser.error("--duration-seconds cannot be negative")

    endpoint = f"{args.api_url.rstrip('/')}/login"
    started = time.monotonic()
    failures_sent = 0

    for index in range(args.count):
        # Schedule attempts evenly from the beginning through the end of the window.
        target_elapsed = (
            args.duration_seconds * index / (args.count - 1)
            if args.count > 1
            else 0
        )
        delay = target_elapsed - (time.monotonic() - started)
        if delay > 0:
            time.sleep(delay)

        form = urllib.parse.urlencode(
            {"username": args.username, "password": "intentionally-invalid-password"}
        ).encode()
        request = urllib.request.Request(
            endpoint,
            data=form,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                # A successful login means the chosen credentials were not invalid.
                raise RuntimeError(
                    f"Attempt {index + 1} unexpectedly logged in (HTTP {response.status}); "
                    "choose a username with an invalid password."
                )
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                detail = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(
                    f"Attempt {index + 1} returned unexpected HTTP {exc.code}: {detail}"
                ) from exc
            failures_sent += 1

        print(f"Sent login_failed attempt {failures_sent}/{args.count}")

    elapsed = time.monotonic() - started
    print(f"Done: {failures_sent} failed login events sent in {elapsed:.1f}s to {endpoint}")


if __name__ == "__main__":
    main()
