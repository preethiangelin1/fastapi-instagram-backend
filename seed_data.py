"""Populate a running InstaClone API with dashboard demo data.

Creates 20 users, 100 posts, 200 comments, and 500 likes per run. Run the API
first, then execute ``python seed_data.py``. Each post image is uploaded with
the exact content type used to obtain its S3 presigned URL.
"""

from __future__ import annotations

import argparse
import json
import os
import struct
import urllib.error
import urllib.parse
import urllib.request
import zlib


API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
PASSWORD = os.getenv("SEED_PASSWORD")

NAMES = [
    ("maya", "Maya Chen"), ("noah", "Noah Williams"), ("amina", "Amina Patel"),
    ("leo", "Leo Martin"), ("sofia", "Sofia Garcia"), ("arjun", "Arjun Rao"),
    ("ella", "Ella Thompson"), ("liam", "Liam Wilson"), ("zara", "Zara Khan"),
    ("ethan", "Ethan Brown"), ("nina", "Nina Kapoor"), ("omar", "Omar Hassan"),
    ("lucy", "Lucy Davis"), ("kai", "Kai Nakamura"), ("ivy", "Ivy Robinson"),
    ("rafael", "Rafael Costa"), ("meera", "Meera Shah"), ("jack", "Jack Turner"),
    ("hana", "Hana Suzuki"), ("adam", "Adam Miller"),
]
USERS = [
    {
        "username": username,
        "email": f"{username}@example.com",
        "full_name": full_name,
        "is_private": index % 5 == 2,
    }
    for index, (username, full_name) in enumerate(NAMES)
]
CAPTIONS = [
    "Morning light", "A little weekend color", "Out for a walk", "Found a quiet corner",
    "Small things worth saving", "A good day outside", "Somewhere new", "Golden hour",
    "Coffee and a view", "A moment to remember",
]
COMMENT_TEXTS = [
    "Love this!", "Such a great shot", "This made my day", "Where was this taken?",
    "The colors are amazing", "Adding this to my list", "Beautiful moment", "So peaceful",
    "I need to visit", "Perfect timing",
]


def png_image(color: tuple[int, int, int]) -> bytes:
    """Return a small valid RGB PNG, avoiding any external image dependency."""

    def chunk(kind: bytes, data: bytes) -> bytes:
        payload = kind + data
        return struct.pack(">I", len(data)) + payload + struct.pack(">I", zlib.crc32(payload) & 0xFFFFFFFF)

    scanline = b"\x00" + bytes(color)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(scanline))
        + chunk(b"IEND", b"")
    )


def request_json(path: str, *, method: str = "GET", body: object | None = None, token: str | None = None):
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json"} if data is not None else {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{API_URL}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} failed ({exc.code}): {detail}") from exc


def create_or_login(user: dict[str, object]) -> str:
    payload = {**user, "password": PASSWORD}
    try:
        request_json("/users/", method="POST", body=payload)
        print(f"Created user @{user['username']}")
    except RuntimeError as exc:
        # Existing seed users are expected on repeat runs; verify credentials.
        if "Username already exists" not in str(exc) and "Email already registered" not in str(exc):
            raise
        print(f"User @{user['username']} already exists; logging in")

    form = urllib.parse.urlencode({"username": user["username"], "password": PASSWORD}).encode()
    req = urllib.request.Request(f"{API_URL}/login", data=form, headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read())["access_token"]
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Could not log in as @{user['username']}: {exc.read().decode(errors='replace')}") from exc


def upload_and_create_post(token: str, caption: str, color: tuple[int, int, int]) -> dict:
    content_type = "image/png"
    presign = request_json("/uploads/presign", method="POST", token=token, body={"content_type": content_type})

    # The content type must match the one included when the URL was signed.
    put = urllib.request.Request(
        presign["upload_url"],
        data=png_image(color),
        headers={"Content-Type": content_type},
        method="PUT",
    )
    try:
        with urllib.request.urlopen(put, timeout=60) as response:
            if response.status not in (200, 201, 204):
                raise RuntimeError(f"S3 upload returned HTTP {response.status}")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"S3 PUT failed ({exc.code}): {exc.read().decode(errors='replace')}") from exc

    return request_json(
        "/posts/",
        method="POST",
        token=token,
        body={"caption": caption, "image_file": presign["key"]},
    )


def main() -> None:
    global API_URL
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", default=API_URL, help="Base URL for the running API")
    args = parser.parse_args()
    API_URL = args.api_url.rstrip("/")

    tokens = {user["username"]: create_or_login(user) for user in USERS}
    colors = [(236, 143, 120), (111, 168, 220), (130, 180, 142), (224, 193, 103), (174, 139, 194)]
    created_posts = []
    for index in range(100):
        author = USERS[index % len(USERS)]
        caption = f"{CAPTIONS[index % len(CAPTIONS)]} #{index + 1}"
        post = upload_and_create_post(tokens[author["username"]], caption, colors[index % len(colors)])
        created_posts.append((post, author["username"]))
        print(f"Created post {index + 1}/100 (id {post['id']}) for @{author['username']}")

    usernames = [user["username"] for user in USERS]
    comment_count = 0
    like_count = 0
    for post_index, (post, author) in enumerate(created_posts):
        for offset in range(2):
            commenter = usernames[(post_index + offset + 1) % len(usernames)]
            request_json(
                f"/posts/{post['id']}/comments",
                method="POST",
                token=tokens[commenter],
                body={"text": f"{COMMENT_TEXTS[(post_index + offset) % len(COMMENT_TEXTS)]} ({commenter})"},
            )
            comment_count += 1
        for offset in range(5):
            liker = usernames[(post_index + offset + 1) % len(usernames)]
            request_json(f"/posts/{post['id']}/likes", method="POST", token=tokens[liker])
            like_count += 1
        if (post_index + 1) % 10 == 0:
            print(f"Added comments and likes to {post_index + 1}/100 posts")

    print(f"Seed complete: {len(USERS)} users, {len(created_posts)} posts, {comment_count} comments, {like_count} likes.")
    print("Demo password: " + PASSWORD)


if __name__ == "__main__":
    main()
