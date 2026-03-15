# 农作物种植分布可视化系统

## 项目简介

这是一个用于可视化中国农作物种植分布的 Web 应用，支持：
- 地图展示各省作物分布
- 年份滑块切换（1990-2025）
- 多作物复选框筛选
- 悬停查看详细面积
- 时序变化折线图（含预测趋势）

## 目录结构

```
CropBelt_Prediction/
├── package.json              # 项目配置
├── vite.config.ts           # Vite 配置
├── tsconfig.json            # TypeScript 配置
├── index.html               # 入口 HTML
├── src/
│   ├── main.tsx             # React 入口
│   ├── App.tsx              # 主应用组件
│   ├── App.css              # 主应用样式
│   ├── index.css            # 全局样式
│   ├── data/
│   │   └── mockData.ts      # 示例数据
│   └── components/
│       ├── Map.tsx          # 地图组件
│       ├── YearSlider.tsx   # 年份滑块
│       └── CropChart.tsx    # 统计图表
└── scripts/
    └── process_crop_data.py # 数据处理脚本
```

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

### 3. 构建生产版本

```bash
npm run build
```

## 数据处理

### 准备您的 TIF 数据

1. 将水稻 TIF 文件放入 `data/水稻/` 目录
2. 文件命名格式：`CCD-Rice-China-{年份}-v1.1.tif`
   - 例如：`CCD-Rice-China-1990-v1.1.tif`

### 运行数据处理脚本

```bash
# 安装 Python 依赖
pip install rasterio geopandas numpy pandas tqdm

# 运行处理脚本
python scripts/process_crop_data.py
```

### 输出数据格式

处理完成后，生成 `data/processed/crop_data.json`：

```json
[
  {
    "year": 1990,
    "crops": {
      "水稻": [
        {
          "省": "黑龙江",
          "面积": 1200000.00,
          "作物类型1": 800000.00,
          "作物类型2": 400000.00
        }
      ]
    }
  }
]
```

## 技术栈

- **前端框架**: React 18 + TypeScript
- **构建工具**: Vite
- **地图库**: Leaflet + React-Leaflet
- **图表库**: ECharts
- **UI组件**: Ant Design
- **数据处理**: Python (rasterio, geopandas)

## 功能说明

1. **地图可视化**: 使用圆圈大小表示种植面积
2. **年份切换**: 滑块选择 1990-2025 年
3. **作物筛选**: 勾选水稻/小麦/玉米/大豆/棉花
4. **悬停信息**: 鼠标悬停显示省份详细信息
5. **趋势预测**: 虚线显示未来趋势预测

## 注意事项

- 确保省界线文件 `china_provinces.json` 存在且格式正确
- TIF 文件需要是正确的 GeoTIFF 格式
- 首次运行可能需要较长时间处理多年数据
