import imageio.v3 as iio
from PIL import Image
import numpy as np

VIDEO_PATH = "bad_apple.mp4"
OUTPUT_PATH = "badapple.bin"
FPS = 12
CHAR_W = 82
CHAR_H = 38

meta = iio.immeta(VIDEO_PATH, plugin="pyav")
video_fps = meta.get("fps", 30)
step = max(1, int(round(video_fps / FPS)))

frames_data = bytearray()
frame_count = 0

print("Conversion...")
for idx, frame in enumerate(iio.imiter(VIDEO_PATH, plugin="pyav")):
    if idx % step == 0:
        img = Image.fromarray(frame).convert("L")
        img = img.resize((CHAR_W * 2, CHAR_H * 3), Image.Resampling.BILINEAR)
        
        binary = (np.array(img) > 127).astype(np.uint8)

        raw_bytes = bytearray()
        for y in range(CHAR_H):
            for x in range(CHAR_W):
                block = binary[y*3:(y+1)*3, x*2:(x+1)*2]
                p1, p2, p3, p4, p5, p6 = block.flatten()
                if p6 == 0:
                    val = (p1 << 0) | (p2 << 1) | (p3 << 2) | (p4 << 3) | (p5 << 4)
                else:
                    val = 32 | ((1-p1) << 0) | ((1-p2) << 1) | ((1-p3) << 2) | ((1-p4) << 3) | ((1-p5) << 4)
                raw_bytes.append(val)

        i = 0
        while i < len(raw_bytes):
            val = raw_bytes[i]
            run = 1
            while i + run < len(raw_bytes) and raw_bytes[i + run] == val and run < 255:
                run += 1
            frames_data.append(run)
            frames_data.append(val)
            i += run

        frame_count += 1

with open(OUTPUT_PATH, "wb") as f:
    f.write(bytes([CHAR_W, CHAR_H, FPS]))
    f.write(frame_count.to_bytes(2, "big"))
    f.write(frames_data)

print(f"Done! File {OUTPUT_PATH} created. Personnel: {frame_count}, Size: {len(frames_data)//1024} KB")
