import glob
import os
from PIL import Image

# Папка, где лежит ЭТОТ скрипт — не зависим от того, где запущен терминал
here = os.path.dirname(os.path.abspath(__file__))

# Берём первую картинку png/jpg рядом со скриптом (имя может быть любым)
candidates = sorted(
    glob.glob(os.path.join(here, "*.png"))
    + glob.glob(os.path.join(here, "*.jpg"))
    + glob.glob(os.path.join(here, "*.jpeg"))
)

if not candidates:
    raise SystemExit(
        "Не нашёл ни одного .png/.jpg рядом со скриптом.\n"
        "Положи свою картинку в папку pixel_ruler и запусти снова."
    )

src_path = candidates[0]
print("Открываю картинку:", src_path)

img = Image.open(src_path).convert("RGBA")

# Режем квадрат по центру, чтобы иконка не сплющилась
w, h = img.size
side = min(w, h)
left = (w - side) // 2
top = (h - side) // 2
img = img.crop((left, top, left + side, top + side))

# Сохраняем сразу все размеры в один .ico (рядом со скриптом)
out = os.path.join(here, "icon.ico")
img.save(
    out,
    sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
)
print("Готово, появился файл:", out)
