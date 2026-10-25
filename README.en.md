[🇷🇺 Русский](README.md) · [🇬🇧 **English**](README.en.md)

# Pixel Ruler

A desktop utility written in Python (Tkinter + Pillow) for measuring distances in
pixels directly on a photo or screenshot. Place points, and the program connects
them into a polyline, reports each segment length and the total, and lets you save
the result as a separate file with the markup drawn over the original at full
resolution.

The UI is bilingual (RU / EN); the chosen language is remembered between launches.
The app runs fully offline — neither your images nor your settings are sent anywhere.

## Features
- Open photos and screenshots: PNG / JPG / JPEG / BMP / GIF / TIFF / WebP.
- Place points with the left mouse button, remove the last one with the right.
- Auto‑connect points in order 1→2→3→… with per‑segment length.
- Zoom with the mouse wheel (toward the cursor) and pan by dragging.
- "Close contour" option joins the last point back to the first (perimeter).
- Measurement panel on the right: point coordinates, lengths, pixel totals.
- **Export the marked image** — saves a copy of the photo at its native resolution
  with lines, points and length labels drawn on top (for reports and messaging).
- **Crisp on HiDPI** — the app is DPI‑aware: the window, native dialogs and text
  render in physical monitor pixels, with no blur from Windows scaling; at 100%
  zoom one photo pixel maps to exactly one screen pixel.
- **Adaptive resampling** — LANCZOS when shrinking (sharp image), NEAREST when
  enlarging (hard pixel grid, easy to land a point on an exact pixel).
- **Bilingual UI (RU / EN)** with a toolbar switcher; the language is stored in the
  user profile and auto‑detected from the system locale on first run. The file
  open/save dialogs and error popups are localized too.

## Controls
| Action | How |
|---|---|
| Place a point | Left click |
| Pan the image | Hold LMB and drag |
| Remove the last point | Right click |
| Zoom in / out | Mouse wheel |
| Open another photo | "Open image" button |
| Save with markup | "Export marked image" button |
| Close contour | "Close contour" checkbox |
| Switch language | "Language" dropdown in the toolbar |

## Install & run from source
Requires Python 3.10+ (tested on 3.15) and the Pillow library:

```bash
pip install pillow
python pixel_ruler.pyw
```

If `pip` is not found, use `python -m pip install pillow`
(on Windows the launcher works too: `py -m pip install pillow` and `py pixel_ruler.pyw`).

## Build a standalone .exe (Windows)
To produce a program that runs without Python installed:

```bash
pip install pyinstaller
py -m PyInstaller --onefile --windowed --noconfirm --name PixelRuler --hidden-import=PIL._tkinter_finder --icon=icon.ico pixel_ruler.pyw
```

The result appears in `dist/PixelRuler.exe`.

## Custom icon
The app icon (`icon.ico`) is generated from any image sitting next to the script:

```bash
py make_icon.py
```

The script takes the first `.png`/`.jpg` in the folder, crops it to a centered
square and packs all sizes (16…256) into one `.ico`. Drop your own picture into the
project folder as e.g. `icon_source.png`, run `py make_icon.py`, then rebuild the exe.

## Project files
| File | Purpose |
|---|---|
| `pixel_ruler.pyw` | main application (Tkinter + Pillow) |
| `make_icon.py` | image → `icon.ico` converter |
| `icon.ico` | ready icon used by the exe build |
| `icon_source.png` | source picture for the icon |
| `README.md` / `README.en.md` | documentation (RU / EN) |

## Download the prebuilt program
The latest build is in the **Releases** section on the right → `PixelRuler.exe`.
On first launch Windows may show a SmartScreen warning ("unknown publisher") — this
is normal for unsigned builds: click "More info" → "Run anyway". The app runs
offline; the chosen language is stored locally in the user profile
(`%APPDATA%\PixelRuler\config.json` on Windows) and is never transmitted.

## License
MIT.
