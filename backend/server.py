from flask import Flask, jsonify, send_file
from flask_cors import CORS
import numpy as np
from PIL import Image
import io
import os
import json
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling

app = Flask(__name__)
CORS(app)

# TIF文件路径
TIF_PATH = r"D:\HBNU\2026InnovationCompetition\data\rice\CCD-Rice-China-1990-v1.1.tif"
OUTPUT_PNG = "public/data/rice_map.png"

def process_tif_to_png():
    """处理TIF文件生成PNG"""
    print(f"正在读取: {TIF_PATH}")
    
    with rasterio.open(TIF_PATH) as src:
        print(f"原始尺寸: {src.width} x {src.height}")
        print(f"CRS: {src.crs}")
        print(f"Bounds: {src.bounds}")
        
        # 读取数据
        band1 = src.read(1)
        
        # 统计
        valid_data = band1[(band1 > 0) & (band1 < 255)]
        if len(valid_data) > 0:
            min_val, max_val = valid_data.min(), valid_data.max()
            print(f"值范围: {min_val} - {max_val}")
        
        # 缩小到10%尺寸
        scale = 0.1
        w = int(src.width * scale)
        h = int(src.height * scale)
        print(f"缩放后: {w} x {h}")
        
        # 使用PIL缩放
        img = Image.fromarray(band1)
        img_small = img.resize((w, h), Image.NEAREST)
        arr = np.array(img_small)
        
        # 创建RGBA图像
        rgba = np.zeros((h, w, 4), dtype=np.uint8)
        
        # 绿色 (76, 175, 80)
        mask = (arr > 0) & (arr < 255)
        rgba[mask, 0] = 76   # R
        rgba[mask, 1] = 175 # G
        rgba[mask, 2] = 80  # B
        rgba[mask, 3] = 180 # A (透明度)
        
        # 保存PNG
        result = Image.fromarray(rgba, 'RGBA')
        result.save(OUTPUT_PNG)
        print(f"已保存: {OUTPUT_PNG}")

# 启动时处理一次
if os.path.exists(TIF_PATH):
    process_tif_to_png()
else:
    print(f"TIF文件不存在: {TIF_PATH}")

@app.route('/api/rice-map')
def get_rice_map():
    """返回水稻地图PNG"""
    if os.path.exists(OUTPUT_PNG):
        return send_file(OUTPUT_PNG, mimetype='image/png')
    return jsonify({"error": "文件不存在"}), 404

@app.route('/api/status')
def status():
    return jsonify({"ready": os.path.exists(OUTPUT_PNG)})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
