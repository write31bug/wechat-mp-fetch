import fitz
from PIL import Image
import io, os

pdf_path = "E:/openclaw-work/comic/mayday-mayday/mayday-mayday-comic.pdf"
out_path = "E:/openclaw-work/comic/mayday-mayday/mayday-mayday-long.png"

doc = fitz.open(pdf_path)
pages = []
for i, page in enumerate(doc):
    mat = fitz.Matrix(2, 2)  # 2x zoom for higher quality
    pix = page.get_pixmap(matrix=mat)
    img_data = pix.tobytes("png")
    img = Image.open(io.BytesIO(img_data))
    pages.append(img)
    print(f"Page {i+1}: {img.size}")

doc.close()

# Stitch vertically
total_height = sum(p.height for p in pages)
max_width = max(p.width for p in pages)
result = Image.new("RGB", (max_width, total_height), (255, 255, 255))

y_offset = 0
for p in pages:
    result.paste(p, (0, y_offset))
    y_offset += p.height

result.save(out_path, "PNG")
size = os.path.getsize(out_path)
print(f"\nLong image saved: {out_path}")
print(f"Size: {size/1024/1024:.2f} MB")
print(f"Dimensions: {result.width} x {result.height}")
