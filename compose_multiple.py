import sys
import numpy as np
from PIL import Image

U8 = True

if len(sys.argv) < 3:
    print("用法: python compose.py img1.png img2.png [img3.png ...]")
    sys.exit(1)

def load_16bit_gray(path):
    img = Image.open(path)
    arr = np.array(img, dtype=np.uint16)
    return arr

# 读取所有图
images = [load_16bit_gray(path) for path in sys.argv[1:]]
arr = np.stack(images, axis=0)  # shape: (N, H, W)

if not np.all([img.shape == arr[0].shape for img in images]):
    raise ValueError("所有输入图片的尺寸必须相同")

THRESHOLD = 32768
MAX_VAL = 65535
N, H, W = arr.shape

# 全局 mask
all_below = np.all(arr < THRESHOLD, axis=0)
all_above = np.all(arr > THRESHOLD, axis=0)

output = np.zeros((H, W), dtype=np.float64)
output[all_below] = 0
output[all_above] = MAX_VAL

# 混合部分 mask
mix_mask = ~(all_below | all_above)

# 取混合部分像素
mix_pixels = arr[:, mix_mask].astype(np.float64)  # shape: (N, M)  M = 混合像素个数
M = mix_pixels.shape[1]

# 256 个采样权重
samples = 256
weights = np.linspace(0, 1, samples, endpoint=False)

# 每个采样点属于哪两个图之间
intervals = np.floor(weights * (N - 1)).astype(int)  # shape: (samples,)
local_w = (weights * (N - 1)) - intervals           # shape: (samples,)

# 插值批量计算
interp_results = np.zeros((samples, M), dtype=np.float64)

for k in range(samples):
    i1 = intervals[k]
    i2 = i1 + 1
    val = (1 - local_w[k]) * mix_pixels[i1] + local_w[k] * mix_pixels[i2]
    interp_results[k] = (val >= THRESHOLD) * MAX_VAL

# 平均
res = np.mean(interp_results, axis=0)

# 回写结果
output[mix_mask] = res

if U8:
    # 转为浮点数，映射到 0~255
    output_float = output.astype(np.float32)
    output_scaled = output_float / 65535.0 * 255.0
    output_uint8 = np.clip(np.floor(output_scaled + 0.5), 0, 255).astype(np.uint8)
    # 保存 8 位灰度图
    out_img = Image.fromarray(output_uint8, mode='L')
    out_img.save("output8.png")
    print(f"合成完成: output8.png，合并了 {N} 张图片")
else:
    output = np.clip(output, 0, MAX_VAL).astype(np.uint16)
    out_img = Image.fromarray(output, mode='I;16')
    out_img.save("output16.png")
    print(f"合成完成: output16.png，合并了 {N} 张图片")
