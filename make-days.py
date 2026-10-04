#!/usr/bin/env python3
"""
The whole day-image pipeline, in one command.

    python3 make-days.py

Drop full-size images into images/days/ (png, jpg, tif — any format Pillow
reads) named by date, e.g. 2026-10-04.png. Then run this. It will:

  1. resize each one to 1600px and save it as WebP q92
  2. move the original out to ../day-originals/, outside the repo
  3. build a 400px thumbnail into images/days/thumbs/
  4. rebuild days.js from whatever is on disk, newest first

Thumbnails are what the contact sheet loads — about 3 KB each against 75 KB
for the full image, so the page stays light however many days pile up. The
full image is only fetched when someone clicks a plate.

Safe to re-run: with no new originals it just refreshes thumbnails and days.js.
"""
import os
import glob
import shutil
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("needs Pillow:  python3 -m pip install Pillow")

HERE = os.path.dirname(os.path.abspath(__file__))
DAYS = os.path.join(HERE, "images", "days")
THUMBS = os.path.join(DAYS, "thumbs")
ORIGINALS = os.path.join(HERE, "..", "day-originals")

FULL_PX, FULL_Q = 1600, 92
THUMB_PX, THUMB_Q = 400, 80
SOURCE_EXT = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp")


def mb(n):
    return f"{n / 1048576:.1f} MB"


def kb(n):
    return f"{n / 1024:.0f} KB"


def main():
    os.makedirs(THUMBS, exist_ok=True)
    os.makedirs(ORIGINALS, exist_ok=True)

    # ---- 1 + 2: convert anything that is not already a webp ------------
    sources = sorted(
        p for p in glob.glob(os.path.join(DAYS, "*"))
        if os.path.splitext(p)[1].lower() in SOURCE_EXT
    )
    if sources:
        tin = tout = 0
        for p in sources:
            name = os.path.basename(p)
            im = Image.open(p).convert("RGB")
            w, h = im.size
            if max(w, h) > FULL_PX:
                s = FULL_PX / max(w, h)
                im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
            out = os.path.join(DAYS, os.path.splitext(name)[0] + ".webp")
            im.save(out, quality=FULL_Q, method=6)
            tin += os.path.getsize(p)
            tout += os.path.getsize(out)

            # never clobber a previously archived original of the same name
            dest = os.path.join(ORIGINALS, name)
            if os.path.exists(dest):
                old = os.path.join(ORIGINALS, "superseded")
                os.makedirs(old, exist_ok=True)
                shutil.move(dest, os.path.join(old, name))
            shutil.move(p, dest)
            print(f"  {name:<20} -> {kb(os.path.getsize(out))}")
        print(f"converted {len(sources)}: {mb(tin)} -> {kb(tout)}\n")
    else:
        print("no new originals to convert\n")

    # ---- 3: thumbnails --------------------------------------------------
    full = sorted(glob.glob(os.path.join(DAYS, "*.webp")))
    if not full:
        sys.exit("no images in images/days/")

    made = tthumb = 0
    for p in full:
        out = os.path.join(THUMBS, os.path.basename(p))
        if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(p):
            im = Image.open(p).convert("RGB")
            im.thumbnail((THUMB_PX, THUMB_PX), Image.LANCZOS)
            im.save(out, quality=THUMB_Q, method=6)
            made += 1
        tthumb += os.path.getsize(out)
    print(f"thumbnails: {made} rebuilt, {len(full)} total, {kb(tthumb)}")
    print(f"full size:  {mb(sum(os.path.getsize(f) for f in full))} "
          f"(only fetched on click)\n")

    # ---- 4: days.js -----------------------------------------------------
    names = sorted((os.path.basename(f) for f in full), reverse=True)
    rows = []
    for n in names:
        stem = os.path.splitext(n)[0]
        try:
            y, m, d = stem.split("-")
            date = f"{y}.{m}.{d}"
        except ValueError:
            date = stem          # odd filename: show it as-is rather than fail
        rows.append(f'  {{ file: "{n}", date: "{date}" }},')
    rows[-1] = rows[-1].rstrip(",")

    path = os.path.join(HERE, "days.js")
    header = open(path, encoding="utf-8").read().split("var DAYS = [")[0]
    open(path, "w", encoding="utf-8").write(
        header + "var DAYS = [\n" + "\n".join(rows) + "\n];\n")
    print(f"days.js: {len(names)} entries, {names[0]} .. {names[-1]}")


if __name__ == "__main__":
    main()
