[🇷🇺 Русский](README.md) · 🇬 **English**

# Pixel Ruler

A small Python utility (Tkinter + Pillow) for measuring distances in pixels
directly on a photo: you place points, the program connects them into a
polyline and reports the length of each segment plus the total. It supports
zoom/pan so you can hit exact pixels, a "close contour" option for perimeters,
and a UI language switcher.

## Features
- Open photos (PNG / JPG / BMP / GIF / TIFF / WebP).
- Place points with the left mouse button, remove the last one with the right.
- Auto-connect points in order 1→2→3→… and show each segment length.
- Zoom with the mouse wheel (zooms toward the cursor) and pan by dragging.
- "Close contour" option joins the last point back to the first.
- Measurement panel on the right: point coordinates, lengths, pixel totals.
- **Bilingual UI (RU / EN)** with a switcher in the toolbar; the chosen language
  is remembered across launches and auto-detected from the system locale on the
  very first run.

## Controls
| Action | How |
|---|---|
| Place a point | Left click |
| Pan the image | Hold LMB and drag |
| Remove the last point | Right click |
| Zoom in / out | Mouse wheel |
| Open another photo | "Open image" button |
| Switch language | "Language" dropdown in the toolbar |

## Install & run from source
Requires Python 3.8+ and the Pillow library:

```bash
pip install pillow
python pixel_ruler.pyw
```

If `pip` is not found, use `python -m pip install pillow`
(or `py -m pip install pillow` on Windows).

## Build a standalone .exe (Windows)
To produce a program that runs without Python installed:

```bash
pip install pyinstaller
py -m PyInstaller --onefile --windowed --name PixelRuler --hidden-import=PIL._tkinter_finder --icon=icon.ico pixel_ruler.pyw
```

The result appears in `dist/PixelRuler.exe`.

## Download the prebuilt program
The latest build is in the **Releases** section on the right → `PixelRuler.exe`.
On first launch Windows may show a SmartScreen warning ("unknown publisher") —
this is normal for unsigned builds: click "More info" → "Run anyway". The app
runs fully offline and never sends your data or images anywhere.

## License
MIT.
