import rasterio
import numpy as np
from PIL import Image, ImageOps

TIF_PATH = r"D:\HBNU\2026InnovationCompetition\data\rice\CCD-Rice-China-1990-v1.1.tif"
OUTPUT_PNG = r"d:\HBNU\2026InnovationCompetition\CropBelt_Prediction\public\data\rice_map.png"

print(f"读取: {TIF_PATH}")

with rasterio.open(TIF_PATH) as src:
    width = src.width
    height = src.height
    print(f"原始尺寸: {width} x {height}")
    print(f"Bounds: left={src.bounds.left}, right={src.bounds.right}, bottom={src.bounds.bottom}, top={src.bounds.top}")
    
    # 缩小到1%
    scale = 0.01
    w = int(width * scale)
    h = int(height * scale)
    
    print(f"缩放: {w} x {h}")
    
    # 使用正确的重采样读取
    band1 = src.read(1, out_shape=(h, w), resampling=rasterio.enums.Resampling.nearest)
    
    # 创建RGBA
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    mask = (band1 > 0) & (band1 < 255)
    rgba[mask, 0] = 76
    rgba[mask, 1] = 175
    rgba[mask, 2] = 80
    rgba[mask, 3] = 180
    
    result = Image.fromarray(rgba, 'RGBA')
    
    # TIF的第一行是北(上)，最后一行是南(下)
    # 但PIL读取时是正常的，不需要翻转
    # 只需要确认边界顺序: [south, west], [north, east]
    # 对于Leaflet: [[bottom, left], [top, right]]
    
    # 保存
    result.save(OUTPUT_PNG)
    print(f"已保存: {OUTPUT_PNG}")
    
    # 输出用于Leaflet的边界
    bounds = [[src.bounds.bottom, src.bounds.left], [src.bounds.top, src.bounds.right]]
    print(f"Leaflet bounds: {bounds}")
