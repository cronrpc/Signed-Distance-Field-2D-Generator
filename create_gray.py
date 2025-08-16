import argparse
import numpy as np
from PIL import Image

def create_gray(width, height, value, bitdepth, output):
    if bitdepth == 8:
        value = max(0, min(255, value))
        img = np.full((height, width), value, dtype=np.uint8)
        im = Image.fromarray(img, mode="L")
    elif bitdepth == 16:
        value = max(0, min(65535, value))
        img = np.full((height, width), value, dtype=np.uint16)
        im = Image.fromarray(img, mode="I;16")
    else:
        raise ValueError("bitdepth must be 8 or 16")
    
    im.save(output)
    print(f"Saved {output} ({bitdepth}-bit, {width}x{height}, value={value})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a gray PNG")
    parser.add_argument("-u", "--unit", type=int, choices=[8, 16], default=16, help="bit depth (8 or 16)")
    parser.add_argument("-W", "--width", default=2048, type=int, help="image width")
    parser.add_argument("-H", "--height", default=2048, type=int, help="image height")
    parser.add_argument("-v", "--value", default=32760, type=int, help="gray value")
    parser.add_argument("output", type=str, help="output filename")
    args = parser.parse_args()

    create_gray(args.width, args.height, args.value, args.unit, args.output)
