import math
from pyproj import CRS, Transformer

# -----------------------------
# 1. CGCS2000 高斯-克吕格 → 经纬度
# -----------------------------
def gauss_to_lonlat(x, y):
    """
    CGCS2000 高斯-克吕格 3°带（40带，中央经线120°）
    x: 东坐标
    y: 北坐标
    return: lon, lat (degrees)
    """
    crs_gauss = CRS.from_proj4(
        "+proj=tmerc "
        "+lat_0=0 "
        "+lon_0=120 "
        "+k=1 "
        "+x_0=500000 "
        "+y_0=0 "
        "+ellps=GRS80 "
        "+units=m "
        "+no_defs"
    )

    crs_geo = CRS.from_epsg(4490)  # CGCS2000 geographic

    transformer = Transformer.from_crs(
        crs_gauss, crs_geo, always_xy=True
    )

    lon, lat = transformer.transform(x, y)
    return lon, lat


# -----------------------------
# 2. WGS84/CGCS2000 → GCJ-02
# -----------------------------
def wgs84_to_gcj02(lon, lat):
    a = 6378245.0
    ee = 0.00669342162296594323

    def transform_lat(x, y):
        ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y
        ret += 0.1 * x * y + 0.2 * math.sqrt(abs(x))
        ret += (20.0 * math.sin(6.0 * x * math.pi)
                + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(y * math.pi)
                + 40.0 * math.sin(y / 3.0 * math.pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(y / 12.0 * math.pi)
                + 320 * math.sin(y * math.pi / 30.0)) * 2.0 / 3.0
        return ret

    def transform_lon(x, y):
        ret = 300.0 + x + 2.0 * y + 0.1 * x * x
        ret += 0.1 * x * y + 0.1 * math.sqrt(abs(x))
        ret += (20.0 * math.sin(6.0 * x * math.pi)
                + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(x * math.pi)
                + 40.0 * math.sin(x / 3.0 * math.pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(x / 12.0 * math.pi)
                + 300.0 * math.sin(x / 30.0 * math.pi)) * 2.0 / 3.0
        return ret

    dlat = transform_lat(lon - 105.0, lat - 35.0)
    dlon = transform_lon(lon - 105.0, lat - 35.0)

    radlat = lat / 180.0 * math.pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)

    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * math.pi)
    dlon = (dlon * 180.0) / (a / sqrtmagic * math.cos(radlat) * math.pi)

    return lon + dlon, lat + dlat


# -----------------------------
# 3. GCJ-02 → BD-09
# -----------------------------
def gcj02_to_bd09(lon, lat):
    z = math.sqrt(lon * lon + lat * lat) + 0.00002 * math.sin(lat * math.pi * 3000.0 / 180.0)
    theta = math.atan2(lat, lon) + 0.000003 * math.cos(lon * math.pi * 3000.0 / 180.0)
    bd_lon = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return bd_lon, bd_lat


# -----------------------------
# 4. 总封装函数
# -----------------------------
def cgcs2000_to_bd09(x, y):
    lon, lat = gauss_to_lonlat(x, y)
    gcj_lon, gcj_lat = wgs84_to_gcj02(lon, lat)
    bd_lon, bd_lat = gcj02_to_bd09(gcj_lon, gcj_lat)
    return bd_lon, bd_lat


# -----------------------------
# 5. 示例（你的4个点）
# -----------------------------
points = [
    (528468.62, 3498330.10),
    (528496.87, 3498329.46),
    (528483.83, 3498318.13),
    (528467.99, 3498319.01),
]

for i, (x, y) in enumerate(points, 1):
    bd_lon, bd_lat = cgcs2000_to_bd09(x, y)
    print(f"Point {i}: BD-09 -> lon={bd_lon:.8f}, lat={bd_lat:.8f}")
