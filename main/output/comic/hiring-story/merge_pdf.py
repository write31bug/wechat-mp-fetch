from PIL import Image
import os

base = "E:/openclaw-work/comic/hiring-story"
pages = ["cover.png", "page-02.png", "page-03.png", "page-04.png", "page-05.png",
         "page-06.png", "page-07.png", "page-08.png", "page-09.png", "page-10.png"]

images = []
for p in pages:
    path = os.path.join(base, p)
    img = Image.open(path).convert("RGB")
    images.append(img)

out_path = os.path.join(base, "一份让人心动的招聘广告.pdf")
images[0].save(out_path, save_all=True, append_images=images[1:], dpi=(300, 300))
print(f"PDF saved: {out_path}")

import os
size = os.path.getsize(out_path)
print(f"File size: {size / 1024 / 1024:.2f} MB")
