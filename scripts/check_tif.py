import rasterio

TIF_PATH = r"D:\HBNU\2026InnovationCompetition\data\rice\CCD-Rice-China-1990-v1.1.tif"

with rasterio.open(TIF_PATH) as src:
    print("宽度:", src.width)
    print("高度:", src.height)
    print("Bounds:", src.bounds)
    print("CRS:", src.crs)
    print("Transform:", src.transform)
    print("Origin:", src.transform * (0, 0))
    print("Pixel scale:", (src.transform.a, src.transform.e))
