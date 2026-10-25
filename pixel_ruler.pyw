#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    from PIL import Image, ImageTk
    try:
        from PIL import ImageOps
    except ImportError:
        ImageOps = None
except ImportError:
    raise SystemExit("Нужна библиотека Pillow. Установите её командой: pip install pillow")


if hasattr(Image, "Resampling"):
    RESAMPLE = Image.Resampling.BILINEAR
    NEAREST_RESAMPLE = Image.Resampling.NEAREST
else:
    RESAMPLE = Image.BILINEAR
    NEAREST_RESAMPLE = Image.NEAREST


FONT_FAMILY = "TkDefaultFont"


class PixelRulerApp:
    MIN_SCALE = 0.01
    MAX_SCALE = 100.0
    DRAG_THRESHOLD = 3

    def __init__(self, root):
        self.root = root
        self.root.title("Пиксельная линейка")
        self.root.geometry("1200x760")

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

        self.build_ui()
        self.bind_events()
        self.redraw()
        self.update_info()

    def build_ui(self):
        toolbar = ttk.Frame(self.root)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        ttk.Button(toolbar, text="Открыть изображение", command=self.open_image).pack(side="left")
        ttk.Button(toolbar, text="По размеру окна", command=self.fit_image_action).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Масштаб 100%", command=self.reset_zoom).pack(side="left")
        ttk.Button(toolbar, text="Отменить точку", command=self.undo_point).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Очистить точки", command=self.clear_points).pack(side="left")

        ttk.Checkbutton(
            toolbar,
            text="Замкнуть контур",
            variable=self.closed_var,
            command=self.on_closed_toggled
        ).pack(side="left", padx=10)

        ttk.Label(toolbar, text="Масштаб:").pack(side="left", padx=(15, 2))
        self.scale_var = tk.StringVar(value="—")
        ttk.Label(toolbar, textvariable=self.scale_var, width=8).pack(side="left")

        self.total_var = tk.StringVar(value="Всего: 0.00 px / 0")
        ttk.Label(
            toolbar,
            textvariable=self.total_var,
            font=(FONT_FAMILY, 10, "bold")
        ).pack(side="right")

        self.canvas = tk.Canvas(
            self.root,
            bg="#2b2b2b",
            highlightthickness=0,
            width=900,
            height=650
        )
        self.canvas.grid(row=1, column=0, sticky="nsew")

        info_frame = ttk.Frame(self.root)
        info_frame.grid(row=1, column=1, sticky="nsew", padx=(0, 5), pady=5)

        ttk.Label(
            info_frame,
            text="Замеры",
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
            text=(
                "ЛКМ: поставить точку; зажать и тянуть — перемещение; "
                "ПКМ — удалить последнюю точку; колесо — приближение/отдаление"
            ),
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

        if cw <= 1:
            cw = 900
        if ch <= 1:
            ch = 650

        return cw, ch

    def on_closed_toggled(self):
        self.redraw()
        self.update_info()

    def open_image(self):
        path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[
                ("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif *.tif *.tiff *.webp"),
                ("Все файлы", "*.*")
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
            messagebox.showerror("Ошибка", f"Не удалось открыть изображение:\n{e}")
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

        if not self.dragged and (abs(dx) > self.DRAG_THRESHOLD or abs(dy) > self.DRAG_THRESHOLD):
            self.dragged = True

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
                cw // 2,
                ch // 2,
                text="Откройте изображение, чтобы начать измерять",
                fill="#cccccc",
                font=(FONT_FAMILY, 14, "bold")
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

            key = (
                left,
                top,
                right,
                bottom,
                tw,
                th,
                round(self.scale, 6),
                cw,
                ch
            )

            if key != self.render_key or self.viewport_photo is None:
                try:
                    crop = self.original.crop((left, top, right, bottom))
                    resized = crop.resize((tw, th), RESAMPLE)
                    self.viewport_photo = ImageTk.PhotoImage(resized)

                except MemoryError:
                    try:
                        crop = self.original.crop((left, top, right, bottom))
                        resized = crop.resize((tw, th), NEAREST_RESAMPLE)
                        self.viewport_photo = ImageTk.PhotoImage(resized)

                    except Exception as e:
                        messagebox.showerror("Ошибка рендеринга", str(e))
                        return

                except Exception as e:
                    messagebox.showerror("Ошибка рендеринга", str(e))
                    return

                self.render_key = key

            self.viewport_x = self.offset_x + left * self.scale
            self.viewport_y = self.offset_y + top * self.scale

            self.canvas.create_image(
                self.viewport_x,
                self.viewport_y,
                anchor="nw",
                image=self.viewport_photo,
                tags="image"
            )

        for a, b, label in self.get_segments():
            x1, y1 = self.image_to_canvas(a)
            x2, y2 = self.image_to_canvas(b)

            is_closing = (
                self.closed_var.get()
                and len(self.points) >= 3
                and label == len(self.points)
            )

            color = "#0a84ff" if is_closing else "#ff3b30"

            self.canvas.create_line(
                x1, y1, x2, y2,
                fill=color,
                width=2,
                tags="measure"
            )

            dist = math.hypot(b[0] - a[0], b[1] - a[1])

            if dist > 0:
                mx = (x1 + x2) / 2.0
                my = (y1 + y2) / 2.0

                self.canvas.create_text(
                    mx,
                    my - 12,
                    text=f"{dist:.1f} px",
                    fill="white",
                    font=(FONT_FAMILY, 9, "bold"),
                    tags="measure"
                )

        for i, p in enumerate(self.points, start=1):
            x, y = self.image_to_canvas(p)
            r = 4

            self.canvas.create_oval(
                x - r,
                y - r,
                x + r,
                y + r,
                fill="#ffd60a",
                outline="black",
                width=1,
                tags="measure"
            )

            self.canvas.create_text(
                x + 8,
                y - 8,
                text=str(i),
                fill="#ffd60a",
                font=(FONT_FAMILY, 9, "bold"),
                tags="measure"
            )

        self.scale_var.set(f"{self.scale * 100:.1f}%")

    def update_info(self):
        total = 0.0
        total_pixels = 0

        self.info.configure(state="normal")
        self.info.delete("1.0", "end")

        if not self.original:
            self.info.insert("end", "Пиксельная линейка\n\n")
            self.info.insert("end", "1. Нажмите «Открыть изображение».\n")
            self.info.insert("end", "2. Ставьте точки левым кликом.\n")
            self.info.insert("end", "3. Точки соединяются в ломаную.\n")
            self.info.insert("end", "4. Колесо мыши приближает/отдаляет фото.\n")
            self.info.insert("end", "5. Перетаскивание левой кнопкой — перемещение.\n")
            self.info.insert("end", "6. Правый клик — удалить последнюю точку.\n")
            self.info.insert(
                "end",
                "7. Галочка «Замкнуть контур» соединит последнюю точку с первой.\n"
            )

            self.info.configure(state="disabled")
            self.total_var.set("Всего: 0.00 px / 0")
            return

        self.info.insert("end", f"Файл: {os.path.basename(self.image_path)}\n")
        self.info.insert(
            "end",
            f"Размер изображения: {self.original.width}×{self.original.height} px\n"
        )
        self.info.insert("end", f"Точек: {len(self.points)}\n\n")

        if not self.points:
            self.info.insert("end", "Поставьте первую точку на изображении.\n")

        elif len(self.points) == 1:
            x, y = self.points[0]
            self.info.insert("end", f"Точка 1: ({x}, {y})\n")
            self.info.insert(
                "end",
                "Поставьте вторую точку, чтобы получить длину отрезка.\n"
            )

        else:
            for a, b, label in self.get_segments():
                dx = b[0] - a[0]
                dy = b[1] - a[1]

                dist = math.hypot(dx, dy)

                # Целое число пикселей для текущего отрезка.
                # Сейчас используется округление вверх геометрической длины.
                pixel_count = int(math.ceil(dist)) if dist > 0 else 0

                total += dist
                total_pixels += pixel_count

                self.info.insert(
                    "end",
                    f"Отрезок {label}: ({a[0]}, {a[1]}) → ({b[0]}, {b[1]})\n"
                )
                self.info.insert(
                    "end",
                    f"    Длина: {dist:.2f} px | целых пикселей: {pixel_count}\n"
                )

            self.info.insert("end", "\n")
            self.info.insert("end", f"ИТОГО длина: {total:.2f} px\n")
            self.info.insert("end", f"ИТОГО целых пикселей: {total_pixels}\n")

            if self.closed_var.get() and len(self.points) >= 3:
                self.info.insert("end", "Контур замкнут.\n")

        if self.points:
            self.info.insert("end", "\nСписок точек:\n")
            for i, (x, y) in enumerate(self.points, start=1):
                self.info.insert("end", f"{i}: ({x}, {y})\n")

        self.info.configure(state="disabled")
        self.total_var.set(f"Всего: {total:.2f} px / {total_pixels}")


def main():
    root = tk.Tk()
    PixelRulerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()