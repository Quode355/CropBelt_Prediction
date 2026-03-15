import { useState, useEffect, useMemo } from 'react'
import { Card, Row, Col, Checkbox, Typography, Spin } from 'antd'
import Map from './components/Map'
import CropChart from './components/CropChart'
import YearSlider from './components/YearSlider'
import './App.css'

const { Title, Text } = Typography

// 作物颜色配置 - 5种作物
const cropColors: { [key: string]: string } = {
  水稻: '#4CAF50',
  小麦: '#FFC107',
  玉米: '#FF9800',
  大豆: '#8BC34A',
  棉花: '#03A9F4',
}

const ALL_CROPS = ['水稻', '小麦', '玉米', '大豆', '棉花']

// 生成1990-2025年的模拟数据（全部为0）
function generateMockData() {
  const years = []
  for (let year = 1990; year <= 2025; year++) {
    const yearData: any = { year, crops: {} }
    
    ALL_CROPS.forEach(crop => {
      yearData.crops[crop] = [
        { 省: '黑龙江', 面积: 0 },
        { 省: '吉林', 面积: 0 },
        { 省: '辽宁', 面积: 0 },
        { 省: '内蒙古', 面积: 0 },
        { 省: '河北', 面积: 0 },
        { 省: '山西', 面积: 0 },
        { 省: '山东', 面积: 0 },
        { 省: '河南', 面积: 0 },
        { 省: '江苏', 面积: 0 },
        { 省: '安徽', 面积: 0 },
        { 省: '浙江', 面积: 0 },
        { 省: '江西', 面积: 0 },
        { 省: '湖北', 面积: 0 },
        { 省: '湖南', 面积: 0 },
        { 省: '四川', 面积: 0 },
        { 省: '云南', 面积: 0 },
        { 省: '贵州', 面积: 0 },
        { 省: '广东', 面积: 0 },
        { 省: '广西', 面积: 0 },
        { 省: '新疆', 面积: 0 },
      ]
    })
    
    years.push(yearData)
  }
  return years
}

const mockCropData = generateMockData()

function App() {
  const [selectedYear, setSelectedYear] = useState<number>(2020)
  const [selectedCrops, setSelectedCrops] = useState<string[]>([])
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  // 加载数据
  useEffect(() => {
    // 使用模拟数据（全部为0）
    setData(mockCropData)
    setLoading(false)
  }, [])

  // 获取当前年份数据
  const currentYearData = useMemo(() => {
    return data.find(d => d.year === selectedYear) || null
  }, [data, selectedYear])

  // 处理作物选择变化
  const handleCropChange = (checkedValues: string[]) => {
    setSelectedCrops(checkedValues)
  }

  // 年份范围
  const yearRange = [1990, 2025]

  if (loading) {
    return (
      <div className="loading-container">
        <Spin size="large" />
        <Text>加载数据中...</Text>
      </div>
    )
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <Title level={2} className="app-title">
          🌾 中国农作物种植分布可视化系统
        </Title>
        <Text type="secondary">
          空间分布 · 时序变化 · 趋势预测
        </Text>
      </header>

      <Row gutter={[16, 16]}>
        {/* 左侧控制面板 */}
        <Col xs={24} md={6}>
          <Card className="control-panel" title="控制面板">
            <div className="control-section">
              <Text strong>选择作物类型</Text>
              <Checkbox.Group
                value={selectedCrops}
                onChange={handleCropChange}
                className="crop-checkbox-group"
              >
                {ALL_CROPS.map(crop => (
                  <Checkbox key={crop} value={crop}>
                    <span style={{ color: cropColors[crop] }}>
                      {crop}
                    </span>
                  </Checkbox>
                ))}
              </Checkbox.Group>
            </div>

            <div className="control-section">
              <Text strong>选择年份: {selectedYear} 年</Text>
              <YearSlider
                min={yearRange[0]}
                max={yearRange[1]}
                value={selectedYear}
                onChange={setSelectedYear}
              />
            </div>

            <div className="control-section">
              <Text strong>图例说明</Text>
              <div className="legend">
                {selectedCrops.length === 0 ? (
                  <Text type="secondary">请先选择作物</Text>
                ) : (
                  selectedCrops.map(crop => (
                    <div key={crop} className="legend-item">
                      <span 
                        className="legend-color" 
                        style={{ backgroundColor: cropColors[crop] }}
                      />
                      <span>{crop}</span>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="hover-info">
              <Text strong>悬停信息</Text>
              <div className="province-info">
                {selectedCrops.length === 0 ? (
                  <Text type="secondary">请先选择作物</Text>
                ) : (
                  <Text type="secondary">将鼠标悬停在地图上查看详情</Text>
                )}
              </div>
            </div>
          </Card>

          {/* 统计信息卡片 */}
          <Card className="stats-card" title="年度统计" style={{ marginTop: 16 }}>
            {selectedCrops.length === 0 ? (
              <Text type="secondary">请先选择作物</Text>
            ) : (
              selectedCrops.map(crop => {
                const cropData = currentYearData?.crops[crop]
                const total = cropData?.reduce((sum: number, p: any) => sum + p.面积, 0) || 0
                return (
                  <div key={crop} className="stat-item">
                    <span style={{ color: cropColors[crop] }}>{crop}</span>
                    <Text strong>{(total / 10000).toFixed(2)} 万公顷</Text>
                  </div>
                )
              })
            )}
          </Card>
        </Col>

        {/* 右侧地图和图表 */}
        <Col xs={24} md={18}>
          <Card className="map-card" title={`${selectedYear}年农作物分布图`}>
            <Map
              data={currentYearData}
              selectedCrops={selectedCrops}
              cropColors={cropColors}
              selectedYear={selectedYear}
            />
          </Card>

          <Card className="chart-card" title="种植面积时序变化 (1990-2025)" style={{ marginTop: 16 }}>
            <CropChart
              data={data}
              selectedCrops={selectedCrops}
              cropColors={cropColors}
            />
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default App
