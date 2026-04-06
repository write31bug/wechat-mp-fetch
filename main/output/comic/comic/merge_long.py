from PIL import Image
import os

src = r'E:\openclaw-work\comic\13spice-hallucination'
pages = sorted([f for f in os.listdir(src) if f.endswith('.png') and f[0].isdigit()])

imgs = [Image.open(os.path.join(src, p)) for p in pages]
w = max(im.width for im in imgs)
total_h = sum(im.height for im in imgs)

canvas = Image.new('RGB', (w, total_h), (255,255,255))
y = 0
for im, p in zip(imgs, pages):
    canvas.paste(im, ((w - im.width)//2, y))
    y += im.height

out = os.path.join(src, 'long.png')
canvas.save(out, quality=90)
size_kb = os.path.getsize(out) // 1024
print(f'Saved: {w}x{total_h}, {size_kb}KB')
