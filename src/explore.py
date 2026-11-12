"""Print the folder layout and a sample of each kind of file, so we can confirm the loader matches."""
import os
import sys
from collections import Counter

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from dataset import read_table  # noqa: E402


def explore(data_dir="/content/data", max_show=15):
    exts = Counter()
    folders = Counter()
    files = []
    for root, _, names in os.walk(data_dir):
        for n in names:
            if n.endswith(".zip"):
                continue
            p = os.path.join(root, n)
            files.append(p)
            exts[os.path.splitext(n)[1].lower()] += 1
            folders[os.path.relpath(root, data_dir)] += 1

    print("File types:", dict(exts))
    print("\nFolders (file count):")
    for f, c in sorted(folders.items()):
        print(f"  {f}: {c}")

    print("\nSample files:")
    shown = set()
    for p in sorted(files):
        folder = os.path.dirname(p)
        if folder in shown and len(shown) < max_show:
            continue
        shown.add(folder)
        print("\n---", os.path.relpath(p, data_dir))
        if p.lower().endswith((".csv", ".txt")):
            try:
                df = read_table(p, nrows=3)
                print("columns:", list(df.columns)[:30], "..." if df.shape[1] > 30 else "")
                print(df.head(2).to_string()[:600])
            except Exception as e:  # noqa
                print("could not read:", e)


if __name__ == "__main__":
    explore(sys.argv[1] if len(sys.argv) > 1 else "/content/data")
