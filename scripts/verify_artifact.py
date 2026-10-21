"""Check trusted file digests and label structure without loading model code."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys


def checked_file(path, expected_digest, capture=False):
    if not re.fullmatch(r"[0-9a-fA-F]{64}", expected_digest or ""):
        raise ValueError("Expected SHA-256 must contain exactly 64 hexadecimal characters")
    path = Path(path)
    if not path.is_file():
        raise ValueError("Input must be an existing regular file")
    digest = hashlib.sha256()
    content = bytearray()
    with path.open("rb") as stream:
        before = os.fstat(stream.fileno())
        if capture and before.st_size > 1024 * 1024:
            raise ValueError("Label mapping exceeds the size limit")
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
            if capture:
                content.extend(block)
                if len(content) > 1024 * 1024:
                    raise ValueError("Label mapping exceeds the size limit")
        after = os.fstat(stream.fileno())
    current = path.stat()
    fingerprint = lambda stat: (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns)
    if not fingerprint(before) == fingerprint(after) == fingerprint(current):
        raise ValueError("Input changed during verification")
    actual = digest.hexdigest()
    if actual != expected_digest.lower():
        raise ValueError("SHA-256 mismatch")
    return {"sha256": actual, "bytes": after.st_size}, bytes(content)


def verify(artifact, artifact_sha256, labels, labels_sha256, class_count):
    if not isinstance(class_count, int) or isinstance(class_count, bool) or class_count < 1:
        raise ValueError("Class count must be a positive integer")
    artifact_info, _ = checked_file(artifact, artifact_sha256)
    labels_info, labels_bytes = checked_file(labels, labels_sha256, capture=True)
    mapping = json.loads(labels_bytes.decode("utf-8-sig"))
    if not isinstance(mapping, dict) or set(mapping) != {str(i) for i in range(class_count)}:
        raise ValueError("Label indices must be contiguous and match the expected class count")
    names = [mapping[str(i)] for i in range(class_count)]
    if any(not isinstance(name, str) or not name.strip() for name in names):
        raise ValueError("Each label must be a non-empty string")
    if len(set(names)) != class_count:
        raise ValueError("Label names must be unique")
    return {"verified": True, "artifact": artifact_info,
            "labels": labels_info, "class_count": class_count}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    options = [("artifact", "MODEL_ARTIFACT_PATH"),
               ("artifact-sha256", "MODEL_ARTIFACT_SHA256"),
               ("labels", "MODEL_LABELS_PATH"),
               ("labels-sha256", "MODEL_LABELS_SHA256"),
               ("class-count", "MODEL_CLASS_COUNT")]
    for option, environment in options:
        parser.add_argument("--" + option, default=os.environ.get(environment))
    args = parser.parse_args(argv)
    try:
        if any(getattr(args, option.replace("-", "_")) is None for option, _ in options):
            raise ValueError("Required verification settings are missing")
        result = verify(args.artifact, args.artifact_sha256, args.labels,
                        args.labels_sha256, int(args.class_count))
    except (ValueError, OSError, UnicodeError) as error:
        print(json.dumps({"verified": False, "error": str(error)}), file=sys.stderr)
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
