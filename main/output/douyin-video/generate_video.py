"""
Generate Douyin short video: 9:16 vertical, 6 images, subtitles, background music.
Uses ffmpeg directly via subprocess.
"""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

# === CONFIG ===
OUT_DIR = r'C:\Users\Administrator\.openclaw\workspace\douyin-video'
IMG_DIR = r'C:\Users\Administrator\.openclaw\workspace\xhs-images\openclaw-xhs-tutorial'
FONT_PATH = r'C:\Windows\Fonts\simhei.ttf'
BGM_FILE = os.path.join(OUT_DIR, 'bgm.wav')
FFMPEG = r'C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'

image_files = [
    ('01-cover.png',   5.0, "救命！AI帮我发公众号，我只说了4句话😭"),
    ('02-before.png',  4.5, "以前发一篇，要搞一整天😭"),
    ('03-after.png',   4.0, "现在？一句话就搞定！✨"),
    ('04-steps.png',   5.5, "4步：安装→配置→生成→发布"),
    ('05-result.png',  4.0, "看！草稿箱2分钟搞定👇"),
    ('06-ending.png',  3.5, "你不需要懂技术，只需说清楚你要什么💡"),
]

TARGET_W = 1080
TARGET_H = 1920

def make_frame(img_path, text, output_path):
    """Create a single 1080x1920 frame with subtitle."""
    img = Image.open(img_path).convert('RGB')
    iw, ih = img.size
    scale = max(TARGET_W / iw, TARGET_H / ih)
    new_w = int(iw * scale)
    new_h = int(ih * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - TARGET_W) // 2
    top = (new_h - TARGET_H) // 2
    img = img.crop((left, top, left + TARGET_W, top + TARGET_H))
    
    # Add subtitle pill
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_PATH, 52)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    pad = 18
    pill_w = tw + pad * 2
    pill_h = th + pad * 2
    # center x
    px = (TARGET_W - pill_w) // 2
    py = int(TARGET_H * 0.77)
    
    # Draw rounded rect bg
    r = min(pill_h // 2, 25)
    draw.rounded_rectangle([px, py, px + pill_w, py + pill_h], radius=r, fill=(0, 0, 0, 180))
    draw.text((px + pad, py + pad), text, font=font, fill=(255, 255, 255))
    
    img.save(output_path, 'PNG')
    print(f"  Saved frame: {output_path}")

def run_ffmpeg(cmd, desc=""):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error {desc}: {result.stderr[-500:]}")
        return False
    return True

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    
    print("Step 1: Creating frame images...")
    frame_pngs = []
    for i, (fname, duration, text) in enumerate(image_files):
        img_path = os.path.join(IMG_DIR, fname)
        frame_out = os.path.join(OUT_DIR, f'frame_{i:02d}.png')
        make_frame(img_path, text, frame_out)
        frame_pngs.append((frame_out, duration))
    
    print("Step 2: Generating individual video clips...")
    clip_files = []
    for i, (frame_png, duration) in enumerate(frame_pngs):
        clip_out = os.path.join(OUT_DIR, f'clip_{i:02d}.mp4')
        cmd = [
            FFMPEG, '-y',
            '-loop', '1',
            '-i', frame_png,
            '-t', str(duration),
            '-vf', f'scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=increase,crop={TARGET_W}:{TARGET_H},setsar=1',
            '-r', '30',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'fast',
            clip_out
        ]
        ok = run_ffmpeg(cmd, f"clip {i}")
        if not ok:
            print(f"Failed clip {i}")
            return
        clip_files.append(clip_out)
    
    print("Step 3: Concatenating clips...")
    concat_file = os.path.join(OUT_DIR, 'concat.txt')
    with open(concat_file, 'w') as f:
        for clip in clip_files:
            f.write(f"file '{clip}'\n")
    
    video_only = os.path.join(OUT_DIR, 'video_no_audio.mp4')
    cmd = [
        FFMPEG, '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', concat_file,
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'fast',
        video_only
    ]
    ok = run_ffmpeg(cmd, "concat")
    if not ok:
        return
    
    total_dur = sum(d for _, d in frame_pngs)
    print(f"Step 4: Looping BGM to {total_dur}s...")
    looped_bgm = os.path.join(OUT_DIR, 'bgm_looped.wav')
    cmd = [
        FFMPEG, '-y',
        '-stream_loop', '5',
        '-i', BGM_FILE,
        '-t', str(total_dur),
        '-acodec', 'pcm_s16le',
        looped_bgm
    ]
    run_ffmpeg(cmd, "BGM loop")
    
    print("Step 5: Combining video + BGM...")
    final = os.path.join(OUT_DIR, 'douyin_final.mp4')
    cmd = [
        FFMPEG, '-y',
        '-i', video_only,
        '-i', looped_bgm,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-shortest',
        final
    ]
    ok = run_ffmpeg(cmd, "combine")
    if ok:
        print(f"\n✅ Final video: {final}")
        size = os.path.getsize(final) / (1024 * 1024)
        print(f"   Size: {size:.1f} MB")
    
    # Cleanup intermediate files
    for f in clip_files + [video_only, looped_bgm, concat_file]:
        try:
            os.remove(f)
        except:
            pass
    for f in frame_pngs:
        try:
            os.remove(f[0])
        except:
            pass

if __name__ == '__main__':
    main()
