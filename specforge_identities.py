#!/usr/bin/env python
"""Create the users a SpecForge run acts as on a RealWorld API, and write identities.toml.

An example to copy and adapt, not part of SpecForge: every API creates users and hands out tokens
its own way. What SpecForge needs is the file it writes: one `[[identities]]` per user, each with
a `label` and the `[identities.headers]` its requests carry.

Usage: python identities_example.py [api_url] [out_file]
  api_url   default: $SPECFORGE_BASE_URL, else http://localhost:8000/api
  out_file  default: identities.toml

A pipeline starts the API with an empty database, so the same names are free on every run, and
fixed names keep the run the same from one job to the next. Standard library only.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Final

DEFAULT_URL: Final = "http://localhost:8000/api"
DEFAULT_OUT: Final = "identities.toml"
PASSWORD: Final = "s3cret-password"
USERS: Final = {"alice": "alice", "bob": "bobby"}
"""Each identity's label, the name a finding is reported under, and the username it signs up
with: the API wants usernames of at least four characters."""
TIMEOUT_S: Final = 10


def register(api_url: str, user: str) -> str:
    """Sign `user` up and return the token the API answers with."""
    payload = {"user": {"username": user, "email": f"{user}@example.com", "password": PASSWORD}}
    request = urllib.request.Request(
        f"{api_url}/users",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
        token = json.loads(response.read().decode("utf-8")).get("user", {}).get("token")
    if not token:
        raise SystemExit(f"{api_url}/users returned no token for {user}")
    return token


def identities_toml(tokens: dict[str, str]) -> str:
    """One identity per label, carrying the token its user signed up with."""
    blocks = [
        f'[[identities]]\nlabel = "{label}"\n'
        f'[identities.headers]\nAuthorization = "Token {token}"\n'
        for label, token in tokens.items()
    ]
    return "\n".join(blocks)


def main() -> None:
    from_env = os.environ.get("SPECFORGE_BASE_URL", DEFAULT_URL)
    api_url = sys.argv[1] if len(sys.argv) > 1 else from_env
    out = Path(sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT)
    tokens = {label: register(api_url, username) for label, username in USERS.items()}
    out.write_text(identities_toml(tokens), encoding="utf-8")
    print(f"wrote {len(tokens)} identities to {out}")


if __name__ == "__main__":
    main()
