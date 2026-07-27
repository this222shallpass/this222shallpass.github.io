# this222shallpass

Static artist page. No build step, no dependencies — plain HTML/CSS and ~50 lines of JS.

```
index.html      landing / index of works
profile.html    about
days.html       day tracking, reads days.js
style.css       everything visual, one file
site.js         language toggle + days rendering
days.js         the list of day images  ← the only file you touch to post
images/
  bg-placeholder.svg   background drawing
  days/                day images
```

## Posting a day

1. Drop the image into `images/days/`
2. Add one line at the **top** of the list in `days.js`:

```js
{ file: "2026-07-28.jpg", date: "2026.07.28", en: "note", ja: "メモ" },
```

`en` and `ja` are optional — delete either key to leave it out. Newest first.

Resize before committing. The grid never shows an image wider than ~250px, and
git keeps every version of a binary forever, so a few MB per day adds up fast and
cannot be taken back out. 1600px on the long edge as WebP q92 is the current
setting — that put the first six days at ~70 KB each instead of ~4.5 MB:

```bash
python3 -c 'from PIL import Image;import sys;i=Image.open(sys.argv[1]).convert("RGB");s=1600/max(i.size);i=i.resize([round(d*s) for d in i.size],Image.LANCZOS) if s<1 else i;i.save(sys.argv[2],quality=92,method=6)' in.png images/days/out.webp
```

Full-size originals live outside the repo in `../day-originals/`.

## Swapping the background

Replace `images/bg-brutalist.svg` with your own file, then change the one line
at the top of `style.css`:

```css
--bg-image: url("images/your-drawing.png");
```

Opacity, position and size are the four lines under `.bg` — the mobile override is
at the bottom of the file. The drawing is forced to grayscale and multiplied onto
the paper, so a scan with a white background will drop out on its own.

## Language toggle

Every translated string is two sibling elements:

```html
<span class="en">Profile</span><span class="ja">プロフィール</span>
```

CSS hides one based on `<html lang>`; the button flips it and remembers the choice
in localStorage. All the current copy is placeholder text — search for
"Placeholder" / "プレースホルダー".

## Publishing

The repo must be named `this222shallpass.github.io` for the bare domain to work.

```bash
git init && git add -A && git commit -m "site" && git branch -M main
```

Then add the remote and push; in the repo's Settings → Pages, set the source to
`main` / `/ (root)`.

## Local preview

```bash
python3 -m http.server 8000
```
