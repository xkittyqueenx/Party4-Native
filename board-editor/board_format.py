"""Mario Party 4 board-space archive reader/writer.

Only archive entry 0 is edited. Every other compressed entry is copied verbatim.
Coordinates, event flags, and star records retain their original binary values.
"""

from __future__ import annotations

import json
import math
import struct
from pathlib import Path

BOARD_FILES = {
    "w01": "Toad's Midway Madness",
    "w02": "Goomba's Greedy Gala",
    "w03": "Shy Guy's Jungle Jam",
    "w04": "Boo's Haunted Bash",
    "w05": "Koopa's Seaside Soiree",
    "w06": "Bowser's Gnarly Party",
    "w20": "Mega Board Mayhem",
    "w21": "Mini Board Mad-Dash",
}
TYPE_NAMES = {0: "Hidden / route", 1: "Blue", 2: "Red", 3: "Bowser", 4: "Mushroom / item",
              5: "Battle", 6: "Happening", 7: "Fortune", 8: "Star marker (saved)",
              9: "Warp", 10: "Star (runtime)", 11: "Other"}


def _u32(data: bytes, offset: int) -> int:
    return struct.unpack_from(">I", data, offset)[0]


def _lz(data: bytes, size: int) -> bytes:
    dictionary = bytearray(1024)
    pos, offset, flags = 958, 0, 0
    result = bytearray()
    while len(result) < size:
        flags >>= 1
        if not flags & 0x100:
            if offset >= len(data):
                raise ValueError("Truncated LZ stream")
            flags = data[offset] | 0xFF00
            offset += 1
        if flags & 1:
            if offset >= len(data):
                raise ValueError("Truncated LZ literal")
            value = data[offset]
            offset += 1
            dictionary[pos] = value
            pos = (pos + 1) & 1023
            result.append(value)
        else:
            if offset + 2 > len(data):
                raise ValueError("Truncated LZ match")
            start = data[offset]
            length = data[offset + 1]
            offset += 2
            start |= (length & ~0x3F) << 2
            length = (length & 0x3F) + 3
            for j in range(min(length, size - len(result))):
                value = dictionary[(start + j) & 1023]
                dictionary[pos] = value
                pos = (pos + 1) & 1023
                result.append(value)
    return bytes(result)


def archive_entries(archive: bytes) -> list[bytes]:
    if len(archive) < 8:
        raise ValueError("Archive is too short")
    count = _u32(archive, 0)
    if not 1 <= count <= 4096 or 4 + count * 4 > len(archive):
        raise ValueError("Invalid archive index")
    offsets = [_u32(archive, 4 + i * 4) for i in range(count)] + [len(archive)]
    if offsets[0] < 4 + count * 4 or any(a >= b or b > len(archive) for a, b in zip(offsets, offsets[1:])):
        raise ValueError("Invalid archive offsets")
    return [archive[a:b] for a, b in zip(offsets, offsets[1:])]


def board_bytes(archive: bytes) -> bytes:
    entry = archive_entries(archive)[0]
    if len(entry) < 8:
        raise ValueError("Board entry is too short")
    size, method = struct.unpack_from(">II", entry)
    if size > 1_000_000:
        raise ValueError("Unreasonable board size")
    if method == 0:
        data = entry[8:8 + size]
    elif method == 1:
        data = _lz(entry[8:], size)
    else:
        raise ValueError(f"Unsupported board compression {method}")
    if len(data) != size:
        raise ValueError("Incomplete board data")
    return data


def parse_spaces(data: bytes) -> list[dict]:
    if len(data) < 4:
        raise ValueError("No space count")
    count = _u32(data, 0)
    if count > 256:
        raise ValueError("The game supports at most 256 spaces per layer")
    spaces, offset = [], 4
    for index in range(count):
        if offset + 44 > len(data):
            raise ValueError(f"Space {index + 1} is truncated")
        values = struct.unpack_from(">9fIHH", data, offset)
        offset += 44
        position, rotation, scale = values[:3], values[3:6], values[6:9]
        flags, kind, link_count = values[9:]
        if link_count > 4 or offset + 2 * link_count > len(data):
            raise ValueError(f"Space {index + 1} has invalid links")
        links = list(struct.unpack_from(">" + "H" * link_count, data, offset)) if link_count else []
        offset += 2 * link_count
        spaces.append({"pos": list(position), "rot": list(rotation), "scale": list(scale),
                       "flags": flags, "type": kind, "links": [link + 1 for link in links]})
    if offset != len(data):
        raise ValueError(f"Unexpected {len(data) - offset} trailing board bytes")
    validate(spaces)
    return spaces


def validate(spaces: list[dict]) -> None:
    if not 1 <= len(spaces) <= 256:
        raise ValueError("Board must have 1–256 spaces")
    stars = set()
    for index, space in enumerate(spaces, 1):
        for axis in (*space["pos"], *space["rot"], *space["scale"]):
            if not isinstance(axis, (int, float)) or not math.isfinite(axis):
                raise ValueError(f"Space {index}: invalid coordinate")
        if not 0 <= space["flags"] <= 0xFFFFFFFF or not 0 <= space["type"] <= 11:
            raise ValueError(f"Space {index}: invalid type or flags")
        links = space["links"]
        if len(links) > 4 or len(set(links)) != len(links) or any(not 1 <= link <= len(spaces) for link in links):
            raise ValueError(f"Space {index}: links must name up to four distinct existing spaces")
        if space["type"] == 8:
            star = (space["flags"] & 0x70000) >> 16
            if star in stars:
                raise ValueError(f"Space {index}: duplicate star slot {star}")
            stars.add(star)


def encode_spaces(spaces: list[dict]) -> bytes:
    validate(spaces)
    result = bytearray(struct.pack(">I", len(spaces)))
    for space in spaces:
        result += struct.pack(">9fIHH", *space["pos"], *space["rot"], *space["scale"],
                              space["flags"], space["type"], len(space["links"]))
        for link in space["links"]:
            result += struct.pack(">H", link - 1)
    return bytes(result)


def replace_board(archive: bytes, spaces: list[dict]) -> bytes:
    entries = archive_entries(archive)
    board = encode_spaces(spaces)
    entries[0] = struct.pack(">II", len(board), 0) + board
    output = bytearray(4 + 4 * len(entries))
    struct.pack_into(">I", output, 0, len(entries))
    for index, entry in enumerate(entries):
        while len(output) % 4:
            output.append(0)
        struct.pack_into(">I", output, 4 + 4 * index, len(output))
        output.extend(entry)
    return bytes(output)


def save_project(path: Path, board_id: str, original_path: Path, spaces: list[dict]) -> None:
    validate(spaces)
    path.write_text(json.dumps({"format": 1, "board": board_id,
                                "original": str(original_path.resolve()), "spaces": spaces}, indent=2), encoding="utf-8")


def load_project(path: Path) -> tuple[str, Path, list[dict]]:
    project = json.loads(path.read_text(encoding="utf-8"))
    if project.get("format") != 1 or project.get("board") not in BOARD_FILES:
        raise ValueError("Unsupported board project")
    spaces = project["spaces"]
    validate(spaces)
    return project["board"], Path(project["original"]), spaces
