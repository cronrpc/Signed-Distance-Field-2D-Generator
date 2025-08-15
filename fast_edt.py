import sys
import os
import numpy as np
from PIL import Image
from scipy import ndimage

scale = 10

def load_image_binary(path, threshold=128):
    im = Image.open(path).convert('L')
    arr = np.array(im, dtype=np.uint8)
    inside = arr < threshold
    return inside

def save_sdf_16bit(signed, out_path):
    # 直接转 uint16 保存，不做归一化
    signed = signed * scale + 32767.5
    signed_uint16 = np.clip(signed, 0, 65535).astype(np.uint16)
    out = Image.fromarray(signed_uint16, mode='I;16')
    out.save(out_path)

def fast_signed_sdf(mask):
    dist_inside = ndimage.distance_transform_edt(mask)
    dist_outside = ndimage.distance_transform_edt(~mask)
    return dist_outside - dist_inside  # inside 正，outside 负

def main():
    if len(sys.argv) < 2:
        print("Usage: python fast_sdf.py input1.png [input2.png ...]")
        sys.exit(1)

    for in_path in sys.argv[1:]:
        if not os.path.exists(in_path):
            print("File not found:", in_path)
            continue

        inside = load_image_binary(in_path)
        signed = fast_signed_sdf(inside)

        base, _ = os.path.splitext(in_path)
        out_path = base + "_sdf16.png"
        save_sdf_16bit(signed, out_path)
        print(f"Saved SDF to {out_path}")

if __name__ == "__main__":
    main()
