#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import os
import sys
import json
import ctypes
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    try:
        from PIL import ImageOps
    except ImportError:
        ImageOps = None
except ImportError:
    raise SystemExit("Нужна библиотека Pillow. Установите её командой: pip install pillow")


if hasattr(Image, "Resampling"):
    RESAMPLE = Image.Resampling.BILINEAR
    NEAREST_RESAMPLE = Image.Resampling.NEAREST
    LANCZOS_RESAMPLE = Image.Resampling.LANCZOS
else:
    RESAMPLE = Image.BILINEAR
    NEAREST_RESAMPLE = Image.NEAREST
    LANCZOS_RESAMPLE = Image.LANCZOS


FONT_FAMILY = "TkDefaultFont"


# --- DPI-awareness (слой 1): зовём Windows рисовать нас в физических пикселях ---
def enable_dpi_awareness():
    if sys.platform != "win32":
        return
    try:
        # per-monitor v2 — лучший режим на Win10 1703+ / Win11
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        return
    except Exception:
        pass
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass
# ------------------------------------------------------------------------------


# ============================ ЛОКАЛИЗАЦИЯ (данные + функции) ============================
STRINGS = {
    "ru": {
        "app_title":      "Пиксельная линейка",
        "btn_open":       "Открыть изображение",
        "btn_fit":        "По размеру окна",
        "btn_reset":      "Масштаб 100%",
        "btn_undo":       "Отменить точку",
        "btn_clear":      "Очистить точки",
        "btn_export":     "Сохранить с разметкой",
        "chk_closed":     "Замкнуть контур",
        "lbl_scale":      "Масштаб:",
        "lbl_lang":       "Язык:",
        "lbl_total":      "Всего",
        "lbl_measures":   "Замеры",
        "status_hint":    ("ЛКМ: поставить точку; зажать и тянуть — перемещение; "
                           "ПКМ — удалить последнюю точку; колесо — приближение/отдаление"),
        "canvas_empty":   "Откройте изображение, чтобы начать измерять",
        "help_intro":     "Пиксельная линейка",
        "help_1":         "1. Нажмите «Открыть изображение».",
        "help_2":         "2. Ставьте точки левым кликом.",
        "help_3":         "3. Точки соединяются в ломаную.",
        "help_4":         "4. Колесо мыши приближает/отдаляет фото.",
        "help_5":         "5. Перетаскивание левой кнопкой — перемещение.",
        "help_6":         "6. Правый клик — удалить последнюю точку.",
        "help_7":         "7. Галочка «Замкнуть контур» соединит последнюю точку с первой.",
        "lbl_file":       "Файл: ",
        "lbl_size":       "Размер изображения: ",
        "lbl_points":     "Точек: ",
        "hint_first":     "Поставьте первую точку на изображении.",
        "hint_point1":    "Точка 1: ",
        "hint_second":    "Поставьте вторую точку, чтобы получить длину отрезка.",
        "lbl_segment":    "Отрезок ",
        "lbl_len":        "    Длина: ",
        "lbl_pxcount":    " px | целых пикселей: ",
        "lbl_total_len":  "ИТОГО длина: ",
        "lbl_total_px":   "ИТОГО целых пикселей: ",
        "lbl_closed":     "Контур замкнут.",
        "lbl_list":       "\nСписок точек:\n",
        "dlg_open_title":  "Выберите изображение",
        "dlg_images":      "Изображения",
        "dlg_allfiles":    "Все файлы",
        "msg_error":       "Ошибка",
        "msg_open_fail":   "Не удалось открыть изображение:\n",
        "msg_render_error":"Ошибка рендеринга",
        "dlg_export_title":"Сохранить изображение с замерами",
        "msg_export_ok":   "Сохранено:\n",
        "msg_export_fail": "Не удалось сохранить:\n",
        "msg_need_points": "Сначала откройте изображение и поставьте хотя бы две точки.",
    },
    "en": {
        "app_title":      "Pixel Ruler",
        "btn_open":       "Open image",
        "btn_fit":        "Fit to window",
        "btn_reset":      "Zoom 100%",
        "btn_undo":       "Undo point",
        "btn_clear":      "Clear points",
        "btn_export":     "Export marked image",
        "chk_closed":     "Close contour",
        "lbl_scale":      "Scale:",
        "lbl_lang":       "Language:",
        "lbl_total":      "Total",
        "lbl_measures":   "Measurements",
        "status_hint":    ("LMB: place point; drag LMB to move; "
                           "RMB: remove last point; wheel: zoom in/out"),
        "canvas_empty":   "Open an image to start measuring",
        "help_intro":     "Pixel Ruler",
        "help_1":         "1. Click “Open image”.",
        "help_2":         "2. Place points with left click.",
        "help_3":         "3. Points connect into a polyline.",
        "help_4":         "4. Mouse wheel zooms in/out.",
        "help_5":         "5. Drag with left button to pan.",
        "help_6":         "6. Right click removes the last point.",
        "help_7":         "7. “Close contour” joins the last point to the first.",
        "lbl_file":       "File: ",
        "lbl_size":       "Image size: ",
        "lbl_points":     "Points: ",
        "hint_first":     "Place the first point on the image.",
        "hint_point1":    "Point 1: ",
        "hint_second":    "Place a second point to get a segment length.",
        "lbl_segment":    "Segment ",
        "lbl_len":        "    Length: ",
        "lbl_pxcount":    " px | whole pixels: ",
        "lbl_total_len":  "TOTAL length: ",
        "lbl_total_px":   "TOTAL whole pixels: ",
        "lbl_closed":     "Contour closed.",
        "lbl_list":       "\nPoint list:\n",
        "dlg_open_title":  "Select an image",
        "dlg_images":      "Images",
        "dlg_allfiles":    "All files",
        "msg_error":       "Error",
        "msg_open_fail":   "Could not open image:\n",
        "msg_render_error":"Rendering error",
        "dlg_export_title":"Save image with measurements",
        "msg_export_ok":   "Saved:\n",
        "msg_export_fail": "Could not save:\n",
        "msg_need_points": "Open an image and place at least two points first.",
    },
}

LANG_DISPLAY = {"ru": "Русский", "en": "English"}
DISPLAY_LANG = {v: k for k, v in LANG_DISPLAY.items()}


def tr(key, lang):
    return STRINGS.get(lang, STRINGS["en"]).get(key, STRINGS["en"].get(key, key))


def config_dir():
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home())) / "PixelRuler"
    else:
        base = Path.home() / ".config" / "pixel_ruler"
    base.mkdir(parents=True, exist_ok=True)
    return base


CONFIG_FILE = config_dir() / "config.json"


def load_config():
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return {}


def save_config(cfg):
    try:
        CONFIG_FILE.write_text(
            json.dumps(cfg, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError:
        pass


def detect_system_lang():
    env = os.environ.get("PIXEL_RULER_LANG")
    if env and env[:2].lower() in ("ru", "en"):
        return env[:2].lower()
    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        val = os.environ.get(var)
        if val:
            code = val.split(".")[0].split("_")[0].lower()
            if code in ("ru", "en"):
                return code
    if sys.platform == "win32":
        try:
            lcid = ctypes.windll.kernel32.GetUserDefaultUILanguage()
            primary = lcid & 0x3FF
            return "ru" if primary == 0x19 else "en"
        except Exception:
            pass
    return "en"
# =====================================================================================


class PixelRulerApp:
    MIN_SCALE = 0.01
    MAX_SCALE = 100.0
    DRAG_THRESHOLD = 3

    def __init__(self, root):
        self.root = root

        # --- DPI (слой 2а): узнаём реальный масштаб Windows и компенсируем Tk-виджеты ---
        self.dpi_scale = 1.0
        if sys.platform == "win32":
            try:
                self.root.update_idletasks()          # корневой hwnd должен существовать
                hwnd = self.root.winfo_id()
                dpi = 0
                try:
                    dpi = ctypes.windll.user32.GetDpiForWindow(hwnd)
                except Exception:
                    dpi = 0
                if not dpi:
                    try:
                        dpi = ctypes.windll.user32.GetDpiForSystem()
                    except Exception:
                        dpi = 0
                if dpi:
                    self.dpi_scale = dpi / 96.0       # напр. 1.5 при 150%
                    try:
                        self.root.tk.call('tk', 'scaling', dpi / 72.0)
                    except Exception:
                        pass
            except Exception:
                pass
        # порог «это клик или уже перетаскивание» тоже масштабируем, иначе на HiDPI
        # микро-движение руки будет то считаться кликом, то драгом
        self.drag_threshold = max(3, round(3 * self.dpi_scale))
        # ------------------------------------------------------------------------------

        # начальный размер окна домножаем на dpi_scale, иначе на 150% окно будет крошечным
        self.root.geometry(
            f"{int(round(1200 * self.dpi_scale))}x{int(round(760 * self.dpi_scale))}"
        )

        self.original = None
        self.image_path = ""
        self.points = []

        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0

        self.viewport_photo = None
        self.render_key = None
        self.viewport_x = 0.0
        self.viewport_y = 0.0

        self.press_x = None
        self.press_y = None
        self.start_offset_x = 0.0
        self.start_offset_y = 0.0
        self.dragged = False

        self.closed_var = tk.BooleanVar(value=False)

        cfg = load_config()
        if "language" in cfg and cfg["language"] in STRINGS:
            self.lang = cfg["language"]
        else:
            self.lang = detect_system_lang()
            cfg["language"] = self.lang
            save_config(cfg)
        self.vars = {}
        self.root.title(tr("app_title", self.lang))

        self.build_ui()
        self.bind_events()
        self.redraw()
        self.update_info()

    def L(self, key):
        if key not in self.vars:
            sv = tk.StringVar(master=self.root, value=tr(key, self.lang))
            self.vars[key] = sv
        return self.vars[key]

    def on_lang_change(self, event=None):
        chosen = self.lang_combo.get()
        code = DISPLAY_LANG.get(chosen, self.lang)
        self.apply_language(code)

    def apply_language(self, lang):
        if lang not in STRINGS:
            return
        self.lang = lang
        cfg = load_config()
        cfg["language"] = lang
        save_config(cfg)
        for key, sv in self.vars.items():
            sv.set(tr(key, lang))
        self.root.title(tr("app_title", lang))
        try:
            self.lang_combo.set(LANG_DISPLAY[lang])
        except Exception:
            pass
        self.redraw()
        self.update_info()

    def build_ui(self):
        toolbar = ttk.Frame(self.root)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        ttk.Button(toolbar, textvariable=self.L("btn_open"), command=self.open_image).pack(side="left")
        ttk.Button(toolbar, textvariable=self.L("btn_fit"), command=self.fit_image_action).pack(side="left", padx=5)
        ttk.Button(toolbar, textvariable=self.L("btn_reset"), command=self.reset_zoom).pack(side="left")
        ttk.Button(toolbar, textvariable=self.L("btn_undo"), command=self.undo_point).pack(side="left", padx=5)
        ttk.Button(toolbar, textvariable=self.L("btn_clear"), command=self.clear_points).pack(side="left")
        ttk.Button(toolbar, textvariable=self.L("btn_export"), command=self.export_marked_image).pack(side="left", padx=5)

        ttk.Checkbutton(
            toolbar,
            textvariable=self.L("chk_closed"),
            variable=self.closed_var,
            command=self.on_closed_toggled
        ).pack(side="left", padx=10)

        ttk.Label(toolbar, textvariable=self.L("lbl_scale")).pack(side="left", padx=(15, 2))
        self.scale_var = tk.StringVar(value="—")
        ttk.Label(toolbar, textvariable=self.scale_var, width=8).pack(side="left")

        ttk.Label(toolbar, textvariable=self.L("lbl_lang")).pack(side="left", padx=(15, 2))
        self.lang_combo = ttk.Combobox(
            toolbar,
            values=list(LANG_DISPLAY.values()),
            state="readonly",
            width=10,
        )
        self.lang_combo.set(LANG_DISPLAY[self.lang])
        self.lang_combo.pack(side="left")
        self.lang_combo.bind("<<ComboboxSelected>>", self.on_lang_change)

        self.total_var = tk.StringVar(value=f"{tr('lbl_total', self.lang)}: 0.00 px / 0")
        ttk.Label(
            toolbar,
            textvariable=self.total_var,
            font=(FONT_FAMILY, 10, "bold")
        ).pack(side="right")

        # --- DPI (слой 2б): начальный размер холста домножаем на dpi_scale ---
        self.canvas = tk.Canvas(
            self.root,
            bg="#2b2b2b",
            highlightthickness=0,
            width=int(round(900 * self.dpi_scale)),
            height=int(round(650 * self.dpi_scale)),
        )
        # ---------------------------------------------------------------------
        self.canvas.grid(row=1, column=0, sticky="nsew")

        info_frame = ttk.Frame(self.root)
        info_frame.grid(row=1, column=1, sticky="nsew", padx=(0, 5), pady=5)

        ttk.Label(
            info_frame,
            textvariable=self.L("lbl_measures"),
            font=(FONT_FAMILY, 11, "bold")
        ).pack(anchor="w", padx=2, pady=(0, 4))

        text_box = ttk.Frame(info_frame)
        text_box.pack(fill="both", expand=True)

        self.info = tk.Text(
            text_box,
            wrap="word",
            width=48,
            height=25,
            state="disabled",
            bg="#f7f7f7"
        )
        info_scroll = ttk.Scrollbar(text_box, orient="vertical", command=self.info.yview)
        self.info.configure(yscrollcommand=info_scroll.set)

        self.info.pack(side="left", fill="both", expand=True)
        info_scroll.pack(side="right", fill="y")

        status = ttk.Label(
            self.root,
            textvariable=self.L("status_hint"),
            anchor="w"
        )
        status.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5))

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def bind_events(self):
        self.canvas.bind("<Configure>", lambda e: self.redraw())
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", lambda e: self.undo_point())
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", lambda e: self.zoom_at(e.x, e.y, 1))
        self.canvas.bind("<Button-5>", lambda e: self.zoom_at(e.x, e.y, -1))

    def get_canvas_size(self):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        # fallback до первого Configure — тоже в масштабе dpi, чтобы был консистентен
        if cw <= 1:
            cw = int(round(900 * self.dpi_scale))
        if ch <= 1:
            ch = int(round(650 * self.dpi_scale))
        return cw, ch

    def on_closed_toggled(self):
        self.redraw()
        self.update_info()

    def open_image(self):
        path = filedialog.askopenfilename(
            title=tr("dlg_open_title", self.lang),
            filetypes=[
                (tr("dlg_images", self.lang), "*.png *.jpg *.jpeg *.bmp *.gif *.tif *.tiff *.webp"),
                (tr("dlg_allfiles", self.lang), "*.*")
            ]
        )
        if not path:
            return
        try:
            img = Image.open(path)
            img.load()
            if ImageOps is not None:
                try:
                    img = ImageOps.exif_transpose(img)
                except Exception:
                    pass
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")
            self.original = img
            self.image_path = path
        except Exception as e:
            messagebox.showerror(
                tr("msg_error", self.lang),
                tr("msg_open_fail", self.lang) + str(e)
            )
            return
        self.points.clear()
        self.viewport_photo = None
        self.render_key = None
        self.fit_image()
        self.redraw()
        self.update_info()

    def fit_image_action(self):
        self.fit_image()
        self.redraw()

    def fit_image(self):
        if not self.original:
            return
        cw, ch = self.get_canvas_size()
        iw, ih = self.original.size
        self.scale = min(cw / iw, ch / ih)
        self.scale = max(self.MIN_SCALE, min(self.MAX_SCALE, self.scale))
        self.center_image()

    def reset_zoom(self):
        if not self.original:
            return
        self.scale = 1.0
        self.center_image()
        self.redraw()

    def center_image(self):
        if not self.original:
            return
        cw, ch = self.get_canvas_size()
        self.offset_x = (cw - self.original.width * self.scale) / 2.0
        self.offset_y = (ch - self.original.height * self.scale) / 2.0

    def on_press(self, event):
        self.press_x = event.x
        self.press_y = event.y
        self.start_offset_x = self.offset_x
        self.start_offset_y = self.offset_y
        self.dragged = False

    def on_drag(self, event):
        if self.press_x is None:
            return
        dx = event.x - self.press_x
        dy = event.y - self.press_y
        # --- DPI: порог драга в масштабе (self.drag_threshold, а не константа) ---
        if not self.dragged and (abs(dx) > self.drag_threshold or abs(dy) > self.drag_threshold):
            self.dragged = True
        # ------------------------------------------------------------------------
        if self.dragged:
            self.offset_x = self.start_offset_x + dx
            self.offset_y = self.start_offset_y + dy
            self.redraw()

    def on_release(self, event):
        if self.press_x is not None and not self.dragged:
            self.add_point(event.x, event.y)
        self.press_x = None
        self.press_y = None
        self.dragged = False

    def on_mousewheel(self, event):
        direction = 1 if event.delta > 0 else -1
        self.zoom_at(event.x, event.y, direction)

    def zoom_at(self, cx, cy, direction):
        if not self.original:
            return
        factor = 1.2 if direction > 0 else 1.0 / 1.2
        new_scale = self.scale * factor
        new_scale = max(self.MIN_SCALE, min(self.MAX_SCALE, new_scale))
        if abs(new_scale - self.scale) < 1e-9:
            return
        img_x = (cx - self.offset_x) / self.scale
        img_y = (cy - self.offset_y) / self.scale
        self.scale = new_scale
        self.offset_x = cx - img_x * self.scale
        self.offset_y = cy - img_y * self.scale
        self.redraw()

    def add_point(self, cx, cy):
        if not self.original:
            return
        img_x, img_y = self.canvas_to_image(cx, cy)
        if 0 <= img_x < self.original.width and 0 <= img_y < self.original.height:
            point = (int(math.floor(img_x)), int(math.floor(img_y)))
            if not self.points or self.points[-1] != point:
                self.points.append(point)
                self.redraw()
                self.update_info()

    def undo_point(self):
        if self.points:
            self.points.pop()
            self.redraw()
            self.update_info()

    def clear_points(self):
        if self.points:
            self.points.clear()
            self.redraw()
            self.update_info()

    # ============================ ЭКСПОРТ С РАЗМЕТКОЙ ============================
    def _load_font(self, size):
        """Ищем читаемый системный шрифт; не нашли — встроенный fallback."""
        candidates = [
            # Windows
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/verdana.ttf",
            "C:/Windows/Fonts/tahoma.ttf",
            # macOS
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            # Linux
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]
        for path in candidates:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
        try:
            return ImageFont.load_default(size=size)   # Pillow >= 10.1
        except TypeError:
            return ImageFont.load_default()            # старая Pillow

    def export_marked_image(self):
        if not self.original or len(self.points) < 2:
            messagebox.showinfo(tr("app_title", self.lang), tr("msg_need_points", self.lang))
            return

        base = os.path.splitext(os.path.basename(self.image_path))[0] if self.image_path else "image"
        initial = base + "_marked.png"
        path = filedialog.asksaveasfilename(
            parent=self.root,
            title=tr("dlg_export_title", self.lang),
            defaultextension=".png",
            initialfile=initial,
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg *.jpeg")],
        )
        if not path:
            return

        try:
            img = self.original.copy()                 # НЕ мутируем оригинал
            draw = ImageDraw.Draw(img)

            short = min(img.size)
            line_w   = max(2,  round(short * 0.002))
            font_sz  = max(12, round(short * 0.012))
            r        = max(3,  round(short * 0.004))
            ow       = max(1,  line_w // 2)
            stroke_w = max(1,  font_sz // 12)
            font = self._load_font(font_sz)

            # отрезки + подписи длин (координаты уже в пикселях фото — переиспользуем)
            for a, b, label in self.get_segments():
                dist = math.hypot(b[0] - a[0], b[1] - a[1])
                is_closing = (
                    self.closed_var.get()
                    and len(self.points) >= 3
                    and label == len(self.points)
                )
                color = "#0a84ff" if is_closing else "#ff3b30"
                draw.line([a, b], fill=color, width=line_w)
                if dist > 0:
                    mx = (a[0] + b[0]) / 2.0
                    my = (a[1] + b[1]) / 2.0
                    draw.text(
                        (mx, my - r * 2 - stroke_w),
                        f"{dist:.1f} px",
                        fill="white", font=font, anchor="mb",
                        stroke_width=stroke_w, stroke_fill="black",
                    )

            # точки + их номера поверх линий
            for i, p in enumerate(self.points, start=1):
                x, y = p
                draw.ellipse([x - r, y - r, x + r, y + r],
                             fill="#ffd60a", outline="black", width=ow)
                draw.text((x + r * 2, y - r * 2), str(i),
                          fill="#ffd60a", font=font, anchor="lm",
                          stroke_width=stroke_w, stroke_fill="black")

            low = path.lower()
            if low.endswith((".jpg", ".jpeg")) and img.mode == "RGBA":
                img = img.convert("RGB")               # JPEG не умеет альфа-канал
            img.save(path)

            messagebox.showinfo(tr("app_title", self.lang), tr("msg_export_ok", self.lang) + path)
        except Exception as e:
            messagebox.showerror(tr("msg_error", self.lang),
                                 tr("msg_export_fail", self.lang) + str(e))
    # ============================================================================

    def canvas_to_image(self, cx, cy):
        return (
            (cx - self.offset_x) / self.scale,
            (cy - self.offset_y) / self.scale
        )

    def image_to_canvas(self, point):
        x, y = point
        return (
            self.offset_x + (x + 0.5) * self.scale,
            self.offset_y + (y + 0.5) * self.scale
        )

    def get_segments(self):
        segments = []
        for i in range(len(self.points) - 1):
            segments.append((self.points[i], self.points[i + 1], i + 1))
        if self.closed_var.get() and len(self.points) >= 3:
            segments.append((self.points[-1], self.points[0], len(self.points)))
        return segments

    def redraw(self):
        self.canvas.delete("all")
        cw, ch = self.get_canvas_size()

        if not self.original:
            self.canvas.create_text(
                cw // 2, ch // 2,
                text=tr("canvas_empty", self.lang),
                fill="#cccccc", font=(FONT_FAMILY, 14, "bold")
            )
            self.scale_var.set("—")
            return

        left = int(math.floor((-self.offset_x) / self.scale))
        top = int(math.floor((-self.offset_y) / self.scale))
        right = int(math.ceil((cw - self.offset_x) / self.scale))
        bottom = int(math.ceil((ch - self.offset_y) / self.scale))

        left = max(0, min(self.original.width, left))
        right = max(0, min(self.original.width, right))
        top = max(0, min(self.original.height, top))
        bottom = max(0, min(self.original.height, bottom))

        if right > left and bottom > top:
            tw = max(1, int(round((right - left) * self.scale)))
            th = max(1, int(round((bottom - top) * self.scale)))
            key = (left, top, right, bottom, tw, th, round(self.scale, 6), cw, ch)

            if key != self.render_key or self.viewport_photo is None:
                # --- АДАПТИВНЫЙ ФИЛЬТР (рычаг А): при уменьшении LANCZOS (резче),
                #     при увеличении/1:1 NEAREST (жёсткие пиксели, видно сетку).
                #     Если не хочешь кубиков при зуме — замени строку ниже на
                #     resample_mode = RESAMPLE   (и тогда всегда как раньше). ---
                resample_mode = LANCZOS_RESAMPLE if self.scale < 1.0 else NEAREST_RESAMPLE
                # ----------------------------------------------------------------
                try:
                    crop = self.original.crop((left, top, right, bottom))
                    resized = crop.resize((tw, th), resample_mode)
                    self.viewport_photo = ImageTk.PhotoImage(resized)
                except MemoryError:
                    try:
                        crop = self.original.crop((left, top, right, bottom))
                        resized = crop.resize((tw, th), NEAREST_RESAMPLE)
                        self.viewport_photo = ImageTk.PhotoImage(resized)
                    except Exception as e:
                        messagebox.showerror(tr("msg_error", self.lang),
                                             tr("msg_render_error", self.lang) + "\n" + str(e))
                        return
                except Exception as e:
                    messagebox.showerror(tr("msg_error", self.lang),
                                         tr("msg_render_error", self.lang) + "\n" + str(e))
                    return
                self.render_key = key

            self.viewport_x = self.offset_x + left * self.scale
            self.viewport_y = self.offset_y + top * self.scale
            self.canvas.create_image(self.viewport_x, self.viewport_y,
                                     anchor="nw", image=self.viewport_photo, tags="image")

        # --- DPI (слой 2б): пиксельные константы разметки в масштабе dpi_scale ---
        line_w = max(2, round(2 * self.dpi_scale))
        len_off = round(12 * self.dpi_scale)
        pt_off = round(8 * self.dpi_scale)
        pt_outline = max(1, round(1 * self.dpi_scale))
        # ------------------------------------------------------------------------

        for a, b, label in self.get_segments():
            x1, y1 = self.image_to_canvas(a)
            x2, y2 = self.image_to_canvas(b)
            is_closing = (
                self.closed_var.get() and len(self.points) >= 3 and label == len(self.points)
            )
            color = "#0a84ff" if is_closing else "#ff3b30"
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=line_w, tags="measure")
            dist = math.hypot(b[0] - a[0], b[1] - a[1])
            if dist > 0:
                mx = (x1 + x2) / 2.0
                my = (y1 + y2) / 2.0
                self.canvas.create_text(mx, my - len_off, text=f"{dist:.1f} px",
                                        fill="white", font=(FONT_FAMILY, 9, "bold"), tags="measure")

        for i, p in enumerate(self.points, start=1):
            x, y = self.image_to_canvas(p)
            r = max(4, round(4 * self.dpi_scale))
            self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                    fill="#ffd60a", outline="black", width=pt_outline, tags="measure")
            self.canvas.create_text(x + pt_off, y - pt_off, text=str(i),
                                    fill="#ffd60a", font=(FONT_FAMILY, 9, "bold"), tags="measure")

        self.scale_var.set(f"{self.scale * 100:.1f}%")

    def update_info(self):
        total = 0.0
        total_pixels = 0
        self.info.configure(state="normal")
        self.info.delete("1.0", "end")

        if not self.original:
            self.info.insert("end", tr("help_intro", self.lang) + "\n\n")
            self.info.insert("end", tr("help_1", self.lang) + "\n")
            self.info.insert("end", tr("help_2", self.lang) + "\n")
            self.info.insert("end", tr("help_3", self.lang) + "\n")
            self.info.insert("end", tr("help_4", self.lang) + "\n")
            self.info.insert("end", tr("help_5", self.lang) + "\n")
            self.info.insert("end", tr("help_6", self.lang) + "\n")
            self.info.insert("end", tr("help_7", self.lang) + "\n")
            self.info.configure(state="disabled")
            self.total_var.set(f"{tr('lbl_total', self.lang)}: 0.00 px / 0")
            return

        self.info.insert("end", tr("lbl_file", self.lang) + os.path.basename(self.image_path) + "\n")
        self.info.insert("end", tr("lbl_size", self.lang) + f"{self.original.width}×{self.original.height} px\n")
        self.info.insert("end", tr("lbl_points", self.lang) + f"{len(self.points)}\n\n")

        if not self.points:
            self.info.insert("end", tr("hint_first", self.lang) + "\n")
        elif len(self.points) == 1:
            x, y = self.points[0]
            self.info.insert("end", tr("hint_point1", self.lang) + f"({x}, {y})\n")
            self.info.insert("end", tr("hint_second", self.lang) + "\n")
        else:
            for a, b, label in self.get_segments():
                dx = b[0] - a[0]
                dy = b[1] - a[1]
                dist = math.hypot(dx, dy)
                pixel_count = int(math.ceil(dist)) if dist > 0 else 0
                total += dist
                total_pixels += pixel_count
                self.info.insert("end", tr("lbl_segment", self.lang) + f"{label}: ({a[0]}, {a[1]}) → ({b[0]}, {b[1]})\n")
                self.info.insert("end", tr("lbl_len", self.lang) + f"{dist:.2f}" + tr("lbl_pxcount", self.lang) + f"{pixel_count}\n")
            self.info.insert("end", "\n")
            self.info.insert("end", tr("lbl_total_len", self.lang) + f"{total:.2f} px\n")
            self.info.insert("end", tr("lbl_total_px", self.lang) + f"{total_pixels}\n")
            if self.closed_var.get() and len(self.points) >= 3:
                self.info.insert("end", tr("lbl_closed", self.lang) + "\n")

        if self.points:
            self.info.insert("end", tr("lbl_list", self.lang))
            for i, (x, y) in enumerate(self.points, start=1):
                self.info.insert("end", f"{i}: ({x}, {y})\n")

        self.info.configure(state="disabled")
        self.total_var.set(f"{tr('lbl_total', self.lang)}: {total:.2f} px / {total_pixels}")


def main():
    enable_dpi_awareness()          # --- DPI (слой 1): ОБЯЗАТЕЛЬНО до tk.Tk() ---
    root = tk.Tk()
    PixelRulerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
