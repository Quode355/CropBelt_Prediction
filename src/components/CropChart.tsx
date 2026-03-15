import ReactECharts from 'echarts-for-react'

interface YearData {
  year: number;
  crops: {
    [key: string]: Array<{ 省: string; 面积: number }>;
  };
}

interface CropChartProps {
  data: YearData[];
  selectedCrops: string[];
  cropColors: { [key: string]: string };
}

function CropChart({ data, selectedCrops, cropColors }: CropChartProps) {
  // 准备图表数据
  const years = data.map(d => d.year)
  
  // 为每个作物创建数据系列
  const series: any[] = []
  
  selectedCrops.forEach(crop => {
    // 全国总种植面积
    const totalData = data.map(yearData => {
      const cropData = yearData.crops[crop]
      if (!cropData) return 0
      return cropData.reduce((sum, p) => sum + p.面积, 0) / 10000 // 转为万公顷
    })
    
    series.push({
      name: crop,
      type: 'line',
      data: totalData,
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: {
        width: 3
      },
      itemStyle: {
        color: cropColors[crop]
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: cropColors[crop] + '40' },
            { offset: 1, color: cropColors[crop] + '10' }
          ]
        }
      }
    })
  })
  
  // 预测虚线（2025年后的趋势预测）
  if (data.length > 0) {
    const lastYear = Math.max(...data.map(d => d.year))
    if (lastYear >= 2020) {
      selectedCrops.forEach(crop => {
        const lastIndex = data.length - 1
        const lastData = data[lastIndex]
        const lastValue = lastData?.crops[crop]
          ?.reduce((sum, p) => sum + p.面积, 0) / 10000 || 0
        
        // 简单的线性趋势预测
        const prevData = data[lastIndex - 1]
        const secondLastValue = prevData?.crops[crop]
          ?.reduce((sum, p) => sum + p.面积, 0) / 10000 || lastValue
        const trend = (lastValue - secondLastValue) / 2
        
        const predictValue = lastValue + trend
        
        series.push({
          name: `${crop}预测`,
          type: 'line',
          data: [...Array(data.length - 1).fill(null), lastValue, predictValue],
          smooth: true,
          symbol: 'emptyCircle',
          symbolSize: 6,
          lineStyle: {
            type: 'dashed',
            width: 2,
            color: cropColors[crop]
          },
          itemStyle: {
            color: cropColors[crop]
          },
          markPoint: {
            data: [
              {
                coord: [data.length, predictValue],
                value: predictValue.toFixed(0),
                itemStyle: { color: cropColors[crop] }
              }
            ]
          }
        })
      })
    }
  }

  // 没有选中作物时显示提示
  if (selectedCrops.length === 0) {
    return (
      <div style={{ 
        height: '100%', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        color: '#999'
      }}>
        请在左侧选择作物查看趋势图
      </div>
    )
  }

  const option = {
    title: {
      text: '全国农作物种植面积变化趋势',
      left: 'center',
      textStyle: {
        fontSize: 14
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        let result = `<strong>${params[0].axisValue}年</strong><br/>`
        params.forEach((item: any) => {
          result += `${item.marker} ${item.seriesName}: ${item.value?.toFixed(2) || 0} 万公顷<br/>`
        })
        return result
      }
    },
    legend: {
      data: selectedCrops,
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: years,
      axisLabel: {
        interval: 4,  // 每5年显示一个标签
        rotate: 0
      }
    },
    yAxis: {
      type: 'value',
      name: '面积 (万公顷)',
      splitLine: {
        lineStyle: {
          type: 'dashed'
        }
      }
    },
    series
  }

  return (
    <ReactECharts 
      option={option} 
      style={{ height: '100%', width: '100%' }}
      opts={{ renderer: 'svg' }}
    />
  )
}

export default CropChart
