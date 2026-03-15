# -*- coding: utf-8 -*-
"""
农作物种植分布数据处理脚本
用于处理TIF格式的遥感数据，生成可用于前端可视化的JSON数据
支持多进程并行处理
"""

import os
import json
import numpy as np
import rasterio
import geopandas as gpd
from rasterio.mask import mask
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

# ==================== 配置路径 ====================
DATA_DIR = Path("D:/HBNU/2026InnovationCompetition/data")
OUTPUT_DIR = DATA_DIR / "processed"
OUTPUT_DIR.mkdir(exist_ok=True)

PROVINCES_FILE = DATA_DIR / "china_provinces.json"
RICE_DIR = DATA_DIR / "rice"

# 作物配置
CROPS = {
    "水稻": {
        "dir": DATA_DIR / "rice",
        "filename_pattern": "CCD-Rice-China-{year}-v1.1.tif",
        "values": {0: "无种植", 1: "水稻类型1", 2: "水稻类型2"}
    },
}

# 并行进程数
NUM_WORKERS = min(multiprocessing.cpu_count(), 8)


def get_tif_file(crop_dir: Path, year: int, pattern: str) -> Path:
    """获取指定年份的TIF文件"""
    filename = pattern.format(year=year)
    filepath = crop_dir / filename
    
    # 如果找不到文件，尝试通配符匹配
    if not filepath.exists():
        tif_files = list(crop_dir.glob(f"*{year}*.tif"))
        if tif_files:
            return tif_files[0]
        raise FileNotFoundError(f"找不到文件: {filepath}")
    
    return filepath


def calculate_area_ha(pixel_count: int, pixel_size_x: float, pixel_size_y: float) -> float:
    """计算面积（公顷）"""
    # 假设数据是地理坐标（经纬度），需要根据实际CRS转换
    # 这里简化处理，假设30米分辨率
    area_m2 = pixel_count * abs(pixel_size_x * pixel_size_y)
    area_ha = area_m2 / 10000  # 平方米转公顷
    return area_ha


def process_single_year_tif(tif_path: Path, provinces_gdf: gpd.GeoDataFrame, crop_name: str):
    """处理单一年份的TIF数据"""
    year_str = tif_path.stem
    # 从文件名提取年份
    for part in year_str.split('-'):
        if part.isdigit() and len(part) == 4:
            year = int(part)
            break
    else:
        year = 2000  # 默认值
    
    # 只处理1990年
    if year != 1990:
        return None
    
    result = {
        "year": year,
        "crops": {
            crop_name: []
        }
    }
    
    with rasterio.open(tif_path) as src:
        print(f"  TIF文件: {tif_path.name}")
        print(f"  分辨率: {src.res}, CRS: {src.crs}")
        
        for idx, province in provinces_gdf.iterrows():
            try:
                # 获取省份名称（根据实际字段调整）
                province_name = province.get('name', province.get('省', f'Province_{idx}'))
                
                # 裁剪该省的区域
                out_image, out_transform = mask(src, [province.geometry], crop=True, nodata=0)
                band = out_image[0]
                
                # 移除nodata值
                valid_data = band[band != 0]
                
                if len(valid_data) == 0:
                    continue
                
                # 统计各类别的像元数
                unique, counts = np.unique(valid_data, return_counts=True)
                value_counts = dict(zip(unique, counts))
                
                # 计算总面积（公顷）
                pixel_size = abs(src.res[0] * src.res[1])
                total_pixels = sum(counts)
                total_area = calculate_area_ha(total_pixels, src.res[0], src.res[1])
                
                province_data = {
                    "省": province_name,
                    "面积": round(total_area, 2),
                }
                
                # 添加各类型详情
                for val, count in value_counts.items():
                    if val in [1, 2]:
                        area = calculate_area_ha(count, src.res[0], src.res[1])
                        province_data[f"作物类型{int(val)}"] = round(area, 2)
                
                result["crops"][crop_name].append(province_data)
                
            except Exception as e:
                print(f"    处理 {province_name} 时出错: {e}")
                continue
    
    return result


def process_all_years(crop_name: str, crop_config: dict):
    """处理某作物所有年份的数据"""
    print(f"\n{'='*50}")
    print(f"处理作物: {crop_name}")
    print(f"{'='*50}")
    
    crop_dir = crop_config["dir"]
    pattern = crop_config["filename_pattern"]
    
    if not crop_dir.exists():
        print(f"  警告: 目录不存在 - {crop_dir}")
        return None
    
    # 获取所有TIF文件
    tif_files = sorted(crop_dir.glob("*.tif"))
    
    if not tif_files:
        print(f"  警告: 目录中没有TIF文件 - {crop_dir}")
        return None
    
    print(f"  找到 {len(tif_files)} 个TIF文件")
    
    # 读取省界线
    print(f"  读取省界线: {PROVINCES_FILE}")
    provinces_gdf = gpd.read_file(PROVINCES_FILE)
    print(f"  共有 {len(provinces_gdf)} 个省份")
    
    all_results = []
    
    for tif_file in tqdm(tif_files, desc=f"处理{crop_name}"):
        try:
            result = process_single_year_tif(tif_file, provinces_gdf, crop_name)
            if result:  # 只添加非None的结果
                all_results.append(result)
        except Exception as e:
            print(f"  处理文件 {tif_file.name} 失败: {e}")
            continue
    
    # 按年份排序
    all_results.sort(key=lambda x: x["year"])
    
    return all_results


def main():
    """主函数"""
    print("=" * 60)
    print("农作物种植分布数据处理")
    print("=" * 60)
    
    # 检查必要文件
    if not PROVINCES_FILE.exists():
        print(f"错误: 省界线文件不存在 - {PROVINCES_FILE}")
        return
    
    print(f"\n省界线文件: {PROVINCES_FILE}")
    print(f"输出目录: {OUTPUT_DIR}")
    
    # 处理各作物数据
    all_data = {}
    
    for crop_name, crop_config in CROPS.items():
        results = process_all_years(crop_name, crop_config)
        if results:
            all_data[crop_name] = results
    
    # 转换为年份组织的格式
    if all_data and "水稻" in all_data:
        # 以水稻数据为基准年份
        rice_years = all_data["水稻"]
        final_data = []
        
        for year_data in rice_years:
            year = year_data["year"]
            year_entry = {"year": year, "crops": {}}
            
            for crop_name in all_data.keys():
                crop_year_data = next(
                    (d for d in all_data[crop_name] if d["year"] == year),
                    None
                )
                if crop_year_data:
                    year_entry["crops"][crop_name] = crop_year_data["crops"][crop_name]
            
            final_data.append(year_entry)
        
        # 保存为JSON
        output_file = OUTPUT_DIR / "crop_data.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*50}")
        print(f"处理完成！")
        print(f"数据已保存到: {output_file}")
        print(f"共处理 {len(final_data)} 年数据")
        print(f"{'='*50}")
    else:
        print("\n警告: 没有成功处理任何作物数据")


if __name__ == "__main__":
    main()
