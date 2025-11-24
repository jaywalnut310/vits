import os
import sys
import argparse


def detect_delimiter(sample_line):
    for d in ["|", ",", "\t", " "]:
        if d in sample_line:
            return d
    return None


def normalize_path(p):
    return "../" + p.strip().strip('"').strip("'")


def main():
    p = argparse.ArgumentParser(
        description="Check existence of first-column paths in a filelist"
    )
    p.add_argument("filelist", help="Input file (one record per line)")
    p.add_argument(
        "-r", "--root", help="Prefix to prepend to relative paths", default=None
    )
    p.add_argument(
        "-d",
        "--delimiter",
        help="Delimiter to split columns (auto if omitted)",
        default="auto",
    )
    args = p.parse_args()

    if not os.path.exists(args.filelist):
        print(f"ERROR: filelist not found: {args.filelist}", file=sys.stderr)
        sys.exit(2)

    with open(args.filelist, "r", encoding="utf-8") as f:
        # find first non-empty line for delimiter detection
        lines = f.readlines()

    sample_line = next((l for l in lines if l.strip() and not l.startswith("#")), "")
    delim = (
        args.delimiter if args.delimiter != "auto" else detect_delimiter(sample_line)
    )
    if delim is None:
        delim = None  # will use split() fallback

    total = 0
    missing = 0
    for i, line in enumerate(lines, start=1):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        total += 1
        if delim:
            parts = line.split(delim, 1)
        else:
            parts = line.split(None, 1)
        if not parts:
            # print(f"[LINE {i}] no columns: {line}")
            missing += 1
            continue
        first = normalize_path(parts[0])
        check_path = first
        if args.root and not os.path.isabs(check_path):
            check_path = os.path.join(args.root, check_path)
        if not os.path.exists(check_path):
            # print(f"[MISSING] line {i}: '{first}' -> tried '{check_path}'")
            missing += 1
        else:
            # print the line to antoher file
            print(line)
    # print(f"Checked {total} entries, missing: {missing}")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
