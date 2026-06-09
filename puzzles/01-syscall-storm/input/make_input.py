#!/usr/bin/env python3
"""Generate deterministic input for the syscall-storm puzzle."""

from __future__ import annotations

import argparse
from pathlib import Path


LINE = b"ptf deterministic benchmark data: 0123456789 abcdefghijklmnopqrstuvwxyz\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", nargs="?", type=Path, default=Path("data.txt"))
    parser.add_argument("--size-mib", type=int, default=8)
    args = parser.parse_args()

    target_size = args.size_mib * 1024 * 1024
    chunk = LINE * 4096
    args.output.parent.mkdir(parents=True, exist_ok=True)
    remaining = target_size
    with args.output.open("wb") as output:
        while remaining:
            piece = chunk[:remaining]
            output.write(piece)
            remaining -= len(piece)
    print(f"Wrote {target_size} bytes to {args.output}")


if __name__ == "__main__":
    main()
