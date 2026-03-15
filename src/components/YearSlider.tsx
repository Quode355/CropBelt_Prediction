import { Slider, Typography } from 'antd'
import { LeftOutlined, RightOutlined } from '@ant-design/icons'

const { Text } = Typography

interface YearSliderProps {
  min: number
  max: number
  value: number
  onChange: (value: number) => void
}

function YearSlider({ min, max, value, onChange }: YearSliderProps) {
  const marks = {
    [min]: `${min}`,
    [Math.floor((min + max) / 2)]: `${Math.floor((min + max) / 2)}`,
    [max]: `${max}`
  }

  // 预测区域标记
  const currentYear = new Date().getFullYear()
  const isPrediction = value > currentYear

  return (
    <div style={{ padding: '16px 0' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
        <LeftOutlined />
        <Text type={isPrediction ? 'warning' : undefined}>
          {isPrediction ? '🔮 预测数据' : '实际数据'}
        </Text>
        <RightOutlined />
      </div>
      
      <Slider
        min={min}
        max={max}
        value={value}
        onChange={onChange}
        marks={marks}
        tooltip={{ 
          formatter: (val) => val ? `${val}年` : ''
        }}
        styles={{
          track: {
            background: isPrediction ? '#faad14' : undefined
          }
        }}
      />
      
      {isPrediction && (
        <Text type="secondary" style={{ fontSize: 12, display: 'block', marginTop: 8 }}>
          虚线部分为基于历史数据的预测结果
        </Text>
      )}
    </div>
  )
}

export default YearSlider
