# -*- coding: utf-8 -*-
"""
修复后的水稻数据处理脚本
"""

import json
import numpy as np
import rasterio
import geopandas as gpd
from rasterio.mask import mask
from pathlib import Path
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# ==================== 配置 ====================
DATA_DIR = Path("D:/HBNU/2026InnovationCompetition/data")
OUTPUT_DIR = DATA_DIR / "processed"
OUTPUT_DIR.mkdir(exist_ok=True)
PROVINCES_FILE = DATA_DIR / "china_provinces.json"
RICE_DIR = DATA_DIR / "rice"

# 降采样因子
DOWNSAMPLE = 20


def calculate_area_ha(pixel_count: int, pixel_size_deg: float) -> float:
    """计算面积（公顷）"""
    meter_per_deg = 111000
    pixel_size_m = pixel_size_deg * meter_per_deg
    area_m2 = pixel_count * (pixel_size_m ** 2)
    return area_m2 / 10000


def process_single_tif(tif_path: Path, provinces_gdf: gpd.GeoDataFrame) -> dict:
    """处理单个TIF文件"""
    # 从文件名提取年份
    year = None
    for part in tif_path.stem.split('-'):
        if part.isdigit() and len(part) == 4:
            year = int(part)
            break
    if not year:
        year = 2000
    
    result = {
        "year": year,
        "crops": {
            "水稻": []
        }
    }
    
    with rasterio.open(tif_path) as src:
        # 获取降采样后的分辨率
        out_res = src.res[0] * DOWNSAMPLE
        
        # 读取降采样的数据
        width = src.width // DOWNSAMPLE
        height = src.height // DOWNSAMPLE
        
        from rasterio.enums import Resampling
        data = src.read(
            1,
            out_shape=(height, width),
            resampling=Resampling.bilinear
        )
        
        # 获取新的仿射变换
        out_transform = src.transform * src.transform.scale(DOWNSAMPLE, DOWNSAMPLE)
        
        # 遍历每个省份
        for idx, province in provinces_gdf.iterrows():
            try:
                # 获取省份名称 - 使用 'name' 列
                province_name = province.get('name', f'Province_{idx}')
                
                bounds = province.geometry.bounds
                
                # 将地理坐标转换为像素坐标
                col_start = max(0, int((bounds[0] - out_transform.c) / out_res))
                row_start = max(0, int((bounds[3] - out_transform.f) / out_res))
                col_stop = min(width, int((bounds[2] - out_transform.c) / out_res) + 1)
                row_stop = min(height, int((bounds[1] - out_transform.f) / out_res) + 1)
                
                if col_start >= col_stop or row_start >= row_stop:
                    continue
                
                # 裁剪数据
                cropped = data[row_start:row_stop, col_start:col_stop]
                
                if cropped.size == 0:
                    continue
                
                # 关键：0表示无种植，1表示有种植
                # 统计值为1的像素数
                valid_pixels = np.sum(cropped == 1)
                
                if valid_pixels == 0:
                    continue
                
                # 计算面积
                total_pixels = valid_pixels * (DOWNSAMPLE * DOWNSAMPLE)
                total_area = calculate_area_ha(total_pixels, src.res[0])
                
                province_data = {
                    "省": province_name,
                    "面积": round(total_area, 2),
                }
                
                result["crops"]["水稻"].append(province_data)
                
            except Exception as e:
                continue
    
    return result


def main():
    print("=" * 60)
    print("水稻数据处理（修复版）")
    print("=" * 60)
    
    if not PROVINCES_FILE.exists():
        print(f"错误: 省界线文件不存在")
        return
    
    print("读取省界线...")
    provinces_gdf = gpd.read_file(PROVINCES_FILE)
    print(f"共有 {len(provinces_gdf)} 个省份")
    
    tif_files = sorted(RICE_DIR.glob("*.tif"))
    print(f"找到 {len(tif_files)} 个TIF文件")
    
    all_results = []
    
    for tif_file in tqdm(tif_files, desc="处理中"):
        try:
            result = process_single_tif(tif_file, provinces_gdf)
            all_results.append(result)
            # 只打印有数据的
            if len(result["crops"]["水稻"]) > 0:
                print(f"  完成: {tif_file.name}, {len(result['crops']['水稻'])} 个省份有数据")
        except Exception as e:
            print(f"处理 {tif_file.name} 失败: {e}")
            continue
    
    all_results.sort(key=lambda x: x["year"])
    
    output_file = OUTPUT_DIR / "crop_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n处理完成！")
    print(f"已保存到: {output_file}")
    print(f"共处理 {len(all_results)} 年数据")
    
    # 打印一些统计
    total_provinces_with_data = sum(len(r["crops"]["水稻"]) for r in all_results)
    print(f"总共 {total_provinces_with_data} 条省份数据")


if __name__ == "__main__":
    main()
