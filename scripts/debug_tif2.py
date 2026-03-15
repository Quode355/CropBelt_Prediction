# -*- coding: utf-8 -*-
"""测试脚本 - 检查TIF数据的实际值"""
import numpy as np
import rasterio
from pathlib import Path

DATA_DIR = Path("D:/HBNU/2026InnovationCompetition/data")
RICE_DIR = DATA_DIR / "rice"

# 读取一个TIF文件测试
tif_file = RICE_DIR / "CCD-Rice-China-2020-v1.2.tif"
print(f"测试文件: {tif_file}")

with rasterio.open(tif_file) as src:
    print(f"\nTIF信息:")
    print(f"  CRS: {src.crs}")
    print(f"  nodata: {src.nodata}")
    print(f"  数据类型: {src.dtypes}")
    
    # 读取一小块数据测试（读取中心区域）
    # 原图约132064 x 140690，读取中间部分
    row_start = 66000
    col_start = 70000
    window = ((row_start, row_start + 1000), (col_start, col_start + 1000))
    
    data = src.read(1, window=window)
    
    print(f"\n读取窗口: {window}")
    print(f"数据形状: {data.shape}")
    print(f"数据 min/max: {data.min()}, {data.max()}")
    print(f"唯一值: {np.unique(data)}")
    
    # 检查nodata值
    nodata_val = src.nodata
    if nodata_val is not None:
        non_nodata = data[data != nodata_val]
        print(f"\n非nodata像素数: {len(non_nodata)}")
        if len(non_nodata) > 0:
            print(f"非nodata值: {np.unique(non_nodata)}")
