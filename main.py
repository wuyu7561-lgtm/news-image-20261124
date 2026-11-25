#!/usr/bin/env python3
"""make.fun entry: copy the final poster to /output/entry.png, byte for byte.

Pure standard library only: no network, no PIL, no image re-encoding.
The output is a deterministic copy of the source file, so repeated runs
produce identical bytes and identical SHA-256 hashes.

Local test overrides (optional, not needed on make.fun):
    ENTRY_SOURCE  path to the source image
    ENTRY_OUTPUT  path to the output file
"""

import hashlib
import os
import sys

# Final poster chosen by the team. To switch versions, change this one line.
SOURCE_NAME = "v2-b.jpg"

OUTPUT_PATH = os.environ.get("ENTRY_OUTPUT", "/output/entry.png")

HERE = os.path.dirname(os.path.abspath(__file__))

SOURCE_CANDIDATES = [
    os.environ.get("ENTRY_SOURCE", ""),
    os.path.join(HERE, SOURCE_NAME),
    os.path.join("/input", SOURCE_NAME),
    os.path.join(HERE, "input", SOURCE_NAME),
    r"E:\makefun-20261124" + "\\" + SOURCE_NAME,
]


def find_source():
    """Return the first existing source file, or None."""
    for path in SOURCE_CANDIDATES:
        if path and os.path.isfile(path):
            return path
    return None


def copy_bytes(src, dst):
    """Copy src to dst in chunks and return (size, sha256) of the written file."""
    digest = hashlib.sha256()
    size = 0
    with open(src, "rb") as fin, open(dst, "wb") as fout:
        while True:
            chunk = fin.read(1024 * 1024)
            if not chunk:
                break
            fout.write(chunk)
            digest.update(chunk)
            size += len(chunk)
        fout.flush()
        os.fsync(fout.fileno())
    return size, digest.hexdigest()


def main():
    src = find_source()
    if src is None:
        sys.stderr.write(
            "ERROR: source image not found. Looked for: %s\n"
            % ", ".join(p for p in SOURCE_CANDIDATES if p)
        )
        return 1

    out_dir = os.path.dirname(os.path.abspath(OUTPUT_PATH))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # Write to a temporary file first, then move it into place. This keeps a
    # failed run from leaving a truncated entry.png behind.
    tmp_path = OUTPUT_PATH + ".tmp"
    size, sha = copy_bytes(src, tmp_path)
    os.replace(tmp_path, OUTPUT_PATH)

    print("source: %s" % src)
    print("output: %s" % OUTPUT_PATH)
    print("bytes: %d" % size)
    print("sha256: %s" % sha)
    return 0


if __name__ == "__main__":
    sys.exit(main())
