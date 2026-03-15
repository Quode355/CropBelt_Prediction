# -*- coding: utf-8 -*-
"""测试脚本 - 检查TIF文件和省份边界是否正确"""
import json
import numpy as np
import rasterio
import geopandas as gpd
from rasterio.mask import mask
from pathlib import Path

DATA_DIR = Path("D:/HBNU/2026InnovationCompetition/data")
PROVINCES_FILE = DATA_DIR / "china_provinces.json"
RICE_DIR = DATA_DIR / "rice"

# 读取一个TIF文件测试
tif_file = RICE_DIR / "CCD-Rice-China-2020-v1.2.tif"
print(f"测试文件: {tif_file}")

# 读取省份数据
provinces_gdf = gpd.read_file(PROVINCES_FILE)
print(f"省份数量: {len(provinces_gdf)}")
print(f"省份列名: {provinces_gdf.columns.tolist()}")
print(f"第一个省份: {provinces_gdf.iloc[0]}")

# 打开TIF文件
with rasterio.open(tif_file) as src:
    print(f"\nTIF信息:")
    print(f"  CRS: {src.crs}")
    print(f"  分辨率: {src.res}")
    print(f"  边界: {src.bounds}")
    print(f"  形状: {src.shape}")
    
    # 测试读取一个省份
    province = provinces_gdf.iloc[0]
    province_name = province.get('name', province.get('省', 'Unknown'))
    print(f"\n测试省份: {province_name}")
    print(f"省份几何: {province.geometry}")
    
    try:
        out_image, out_transform = mask(src, [province.geometry], crop=True, nodata=0)
        band = out_image[0]
        
        print(f"裁剪后形状: {band.shape}")
        
        valid_data = band[band != 0]
        print(f"有效像素数: {len(valid_data)}")
        
        if len(valid_data) > 0:
            unique, counts = np.unique(valid_data, return_counts=True)
            print(f"唯一值: {unique}")
            print(f"计数: {counts}")
    except Exception as e:
        print(f"错误: {e}")
