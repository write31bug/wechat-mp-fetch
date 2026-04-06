from PIL import Image
import os

base = "E:/openclaw-work/comic/dark-openclaw"
pages = [f"{base}/p0{i}.png" for i in range(1, 8)]

imgs = [Image.open(p).convert("RGB") for p in pages]
total_h = sum(i.height for i in imgs)
max_w = max(i.width for i in imgs)
result = Image.new("RGB", (max_w, total_h), (0, 0, 0))

y = 0
for img in imgs:
    result.paste(img, (0, y))
    y += img.height

out = f"{base}/dark-openclaw-long.png"
result.save(out, "PNG", quality=95)
print(f"Saved: {out}")
print(f"Size: {os.path.getsize(out)/1024/1024:.2f} MB")
print(f"Dimensions: {result.width} x {result.height}")
