import { useEffect, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// 修复 Leaflet 默认图标问题
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

interface MapProps {
  data: any | null;
  selectedCrops: string[];
  cropColors: { [key: string]: string };
  selectedYear?: number;
}

// 裁剪后的TIF边界（中国陆地范围）
const TIF_BOUNDS: L.LatLngBoundsExpression = [
  [18.159892626118193, 97.52685646183363],  // 西南 [bottom, left]
  [51.66130350595798, 135.08793377366635]   // 东北 [top, right]
]

// 各作物的PNG图片映射（使用裁剪后的图片）
const CROP_MAP_URLS: { [key: string]: { [year: number]: string } } = {
  水稻: {
    1990: 'data/rice_map_clipped.png',
    // 其他年份可以继续添加
  }
}

function Map({ data, selectedCrops, cropColors, selectedYear }: MapProps) {
  const mapRef = useRef<L.Map | null>(null)
  const markersRef = useRef<L.LayerGroup | null>(null)
  const cropLayerRef = useRef<L.ImageOverlay | null>(null)

  // 加载作物图层
  useEffect(() => {
    if (!mapRef.current) return

    // 先移除之前的作物图层
    if (cropLayerRef.current) {
      mapRef.current.removeLayer(cropLayerRef.current)
      cropLayerRef.current = null
    }

    // 检查是否有选中的作物有对应的图片
    const crop = selectedCrops[0]
    if (crop && selectedYear && CROP_MAP_URLS[crop]?.[selectedYear]) {
      const url = CROP_MAP_URLS[crop][selectedYear]
      cropLayerRef.current = L.imageOverlay(url, TIF_BOUNDS, {
        opacity: 0.7
      }).addTo(mapRef.current)
      
      mapRef.current.fitBounds(TIF_BOUNDS)
    }
  }, [selectedCrops, selectedYear])

  useEffect(() => {
    if (!mapRef.current) {
      mapRef.current = L.map('map-container', {
        center: [35, 105],
        zoom: 4,
        minZoom: 3,
        maxZoom: 7
      })

      L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap & CARTO',
        maxZoom: 20
      }).addTo(mapRef.current)

      mapRef.current.setMaxBounds(L.latLngBounds([15, 70], [55, 140]))
      markersRef.current = L.layerGroup().addTo(mapRef.current)
    }

    return () => {
      if (mapRef.current) {
        mapRef.current.remove()
        mapRef.current = null
      }
    }
  }, [])

  useEffect(() => {
    if (!markersRef.current || !data) return
    markersRef.current.clearLayers()

    selectedCrops.forEach(crop => {
      const cropData = data.crops[crop as keyof typeof data.crops]
      if (!cropData) return

      cropData.forEach((province: any) => {
        const area = province.面积 || province.area || 0
        if (area > 0) {
          const circle = L.circleMarker([35, 105], {
            radius: Math.max(5, Math.log10(area + 1) * 15),
            fillColor: cropColors[crop] || '#4CAF50',
            color: '#fff',
            weight: 1.5,
            fillOpacity: 0.8
          })
          circle.bindTooltip(`<strong>${province.省}</strong><br/>${crop}: ${(area/10000).toFixed(2)}万公顷`)
          markersRef.current?.addLayer(circle)
        }
      })
    })
  }, [data, selectedCrops, cropColors])

  return (
    <div style={{ position: 'relative' }}>
      <div id="map-container" style={{ width: '100%', height: '100%', minHeight: '400px' }} />
    </div>
  )
}

export default Map
