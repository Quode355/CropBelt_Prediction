# -*- coding: utf-8 -*-
"""
优化的水稻数据处理脚本
使用 rasterio 的窗口功能进行分块处理
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
DOWNSAMPLE = 20  # 约500m -> 10km


def calculate_area_ha(pixel_count: int, pixel_size_deg: float) -> float:
    """计算面积（公顷）"""
    # 1度 ≈ 111km
    # 像素面积 = (pixel_size_deg * 111000)^2
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
    
    # 使用降采样打开文件
    with rasterio.open(tif_path) as src:
        # 获取降采样后的分辨率（通过上层窗口）
        # 实际上是读取时跳过一些像素
        out_res = src.res[0] * DOWNSAMPLE
        
        # 创建降采样的数据集（缩小到原来的1/DOWNSAMPLE）
        from rasterio.enums import Resampling
        
        # 读取一小部分测试
        width = src.width // DOWNSAMPLE
        height = src.height // DOWNSAMPLE
        
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
                province_name = province.get('name', f'Province_{idx}')
                if '省' in province:
                    province_name = province['省']
                
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
                
                valid_data = cropped[cropped != 0]
                
                if len(valid_data) == 0:
                    continue
                
                unique, counts = np.unique(valid_data, return_counts=True)
                value_counts = dict(zip(unique, counts))
                
                # 计算面积（降采样后的像素代表 DOWNSAMPLE x DOWNSAMPLE 个原始像素）
                total_pixels = sum(counts) * (DOWNSAMPLE * DOWNSAMPLE)
                total_area = calculate_area_ha(total_pixels, src.res[0])
                
                province_data = {
                    "省": province_name,
                    "面积": round(total_area, 2),
                }
                
                for val, count in value_counts.items():
                    if val in [1, 2]:
                        area = calculate_area_ha(count * (DOWNSAMPLE * DOWNSAMPLE), src.res[0])
                        province_data[f"作物类型{int(val)}"] = round(area, 2)
                
                result["crops"]["水稻"].append(province_data)
                
            except Exception as e:
                continue
    
    return result


def main():
    print("=" * 60)
    print("水稻数据处理（高效版）")
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
            print(f"  完成: {tif_file.name}")
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


if __name__ == "__main__":
    main()
