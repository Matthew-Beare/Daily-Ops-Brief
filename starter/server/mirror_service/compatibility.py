from __future__ import annotations

from dataclasses import dataclass

API_MAJOR = 1
SERVER_VERSION = "0.2.0"
MIN_CLIENT_VERSION = "0.2.0"


def parse_semver(value: str) -> tuple[int, int, int]:
    core = (value or "").split("+", 1)[0].split("-", 1)[0]
    parts = core.split(".")
    if len(parts) != 3 or any(not p.isdigit() for p in parts):
        raise ValueError(f"invalid semantic version: {value!r}")
    return tuple(int(p) for p in parts)


@dataclass(frozen=True)
class Compatibility:
    compatible: bool
    reason: str


def evaluate(client_version: str, client_api_major: int) -> Compatibility:
    if client_api_major != API_MAJOR:
        return Compatibility(False, f"API major mismatch: server={API_MAJOR}, client={client_api_major}")
    try:
        if parse_semver(client_version) < parse_semver(MIN_CLIENT_VERSION):
            return Compatibility(False, f"client {client_version} is older than minimum {MIN_CLIENT_VERSION}")
    except ValueError as exc:
        return Compatibility(False, str(exc))
    return Compatibility(True, "compatible")
