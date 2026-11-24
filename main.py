#!/usr/bin/env python3
"""Everyday Wonder: Two Days to Find the Line -- writes the one-sentence
entry to entry.txt.

The gate (sealed scorer): /output/entry.txt must be UTF-8 text of 1 to 200
characters, not only whitespace. The entry itself is exactly one sentence
about a small everyday moment made strange and new: the self-checkout
thanking the shopper by name, and the jolt of being grateful to a machine
for never mispronouncing it.
"""

import os

ENTRY = (
    "The self-checkout thanks me by name, and for one second I am grateful "
    "to the only voice in the shop that has never once mispronounced it."
)

MAX_CHARS = 200


def resolve_output_dir():
    """Return the harness output dir, falling back to ./output."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "./output"


def build_entry():
    """Return the one-sentence entry text (no trailing newline)."""
    return ENTRY


def validate(text):
    """Enforce the entry format exactly as the requirements state."""
    if not isinstance(text, str):
        raise ValueError("entry must be text")
    if not text.strip():
        raise ValueError("entry must not be empty or whitespace only")
    # UTF-8 round trip: the gate reads the file as UTF-8 text.
    text.encode("utf-8").decode("utf-8")
    if len(text) > MAX_CHARS:
        raise ValueError(
            "entry is %d characters, over the %d limit" % (len(text), MAX_CHARS)
        )
    if text != text.strip():
        raise ValueError("entry must not have leading/trailing whitespace")
    if any(ord(ch) < 32 for ch in text):
        raise ValueError("entry must not contain control characters")
    if "  " in text:
        raise ValueError("entry must not contain double spaces")
    lines = text.split("\n")
    if len(lines) != 1:
        raise ValueError("entry must be exactly one line, got %d" % len(lines))
    # Exactly one sentence: one terminator, and it closes the sentence.
    terminators = sum(text.count(mark) for mark in (".", "!", "?"))
    if terminators != 1 or not text.endswith((".", "!", "?")):
        raise ValueError(
            "entry must be exactly one sentence, got %d terminators" % terminators
        )
    return True


def check_entry():
    """Validate the entry without writing anything; print a short report."""
    text = build_entry()
    validate(text)
    words = text.split(" ")
    print("sentence: %d characters, %d words, 1 line, valid" % (len(text), len(words)))
    print("limit: %d characters; headroom: %d" % (MAX_CHARS, MAX_CHARS - len(text)))
    return 0


def main(argv=None):
    if argv and "--check" in argv:
        return check_entry()
    text = build_entry()
    validate(text)
    out_dir = resolve_output_dir()
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    # Determinism guard: render the file bytes twice and require equality,
    # so two grading runs can never disagree about the entry.
    payload = (text + "\n").encode("utf-8")
    if payload != (build_entry() + "\n").encode("utf-8"):
        raise ValueError("entry is not deterministic")
    with open(path, "wb") as f:
        f.write(payload)
    with open(path, "r", encoding="utf-8") as f:
        written = f.read()
    if written != text + "\n":
        raise ValueError("written file does not match the entry exactly")
    validate(written.rstrip("\n"))
    print(
        "wrote %s (%d characters incl. trailing newline; "
        "sentence: %d characters)" % (path, len(written), len(text))
    )
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv[1:]))
