#!/usr/bin/env python3
"""
用中国省界线裁剪水稻影像 - 先缩放再裁剪
"""

import json
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.mask import mask
from shapely.geometry import shape
from shapely.ops import unary_union

# 路径配置
TIF_PATH = r"d:\HBNU\2026InnovationCompetition\CropBelt_Prediction\public\data\CCD-Rice-China-1990-v1.1.tif"
PROVINCES_PATH = r"D:\HBNU\2026InnovationCompetition\data\china_provinces.json"
OUTPUT_PATH = r"d:\HBNU\2026InnovationCompetition\CropBelt_Prediction\public\data\rice_map_clipped.tif"

# 缩放倍数（越大越清晰，但内存占用越高）
SCALE = 8  # 缩小8倍

def load_china_boundary():
    """加载中国省界线，合并成单一多边形"""
    print("加载省界线...")
    with open(PROVINCES_PATH, encoding='utf-8') as f:
        data = json.load(f)
    
    polygons = []
    for feature in data['features']:
        geom = feature['geometry']
        if geom['type'] == 'Polygon':
            poly = shape(geom)
            polygons.append(poly)
        elif geom['type'] == 'MultiPolygon':
            for p in geom['coordinates']:
                poly = shape({'type': 'Polygon', 'coordinates': p})
                polygons.append(poly)
    
    polygons = [p.buffer(0) for p in polygons]
    china_boundary = unary_union(polygons)
    print(f"中国边界加载完成，包含 {len(polygons)} 个多边形")
    return china_boundary

def clip_tif_with_boundary():
    """用中国边界裁剪 TIF"""
    print("读取 TIF 文件...")
    
    with rasterio.open(TIF_PATH) as src:
        print(f"原始 TIF 尺寸: {src.width} x {src.height}")
        
        # 计算缩放后的尺寸
        new_width = src.width // SCALE
        new_height = src.height // SCALE
        print(f"缩放后尺寸: {new_width} x {new_height}")
        
        # 缩放读取
        print("缩放中...")
        data = src.read(
            out_shape=(src.count, new_height, new_width),
            resampling=Resampling.bilinear
        )
        
        # 更新 transform
        transform = src.transform * src.transform.scale(SCALE, SCALE)
        
        # 创建临时数据集用于裁剪
        from rasterio.io import MemoryFile
        temp_meta = src.meta.copy()
        temp_meta.update({
            "height": new_height,
            "width": new_width,
            "transform": transform
        })
        
        china_boundary = load_china_boundary()
        
        # 执行裁剪
        print("裁剪中...")
        
        with MemoryFile() as memfile:
            with memfile.open(**temp_meta) as tmp:
                tmp.write(data)
            
            with memfile.open() as tmp:
                geoms = [china_boundary]
                out_image, out_transform = mask(tmp, geoms, crop=True, nodata=0)
                out_meta = tmp.meta.copy()
                
                out_meta.update({
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform
                })
                
                # 保存
                print(f"保存裁剪结果到: {OUTPUT_PATH}")
                with rasterio.open(OUTPUT_PATH, 'w', **out_meta) as dst:
                    dst.write(out_image)
                
                print(f"最终尺寸: {out_image.shape[2]} x {out_image.shape[1]}")
                print("完成!")

if __name__ == "__main__":
    clip_tif_with_boundary()
