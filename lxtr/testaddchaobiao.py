import math
from pyproj import CRS, Transformer
import requests
import json





import math
from pyproj import CRS, Transformer


def cgcs2000_points_to_bd09(points):
    """
    CGCS2000 高斯投影坐标批量转换为 BD-09
    :param points: [(x, y), ...]
    :return: [[lon, lat], ...]
    """

    # -------- 坐标系定义（只初始化一次）--------
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
    crs_geo = CRS.from_epsg(4490)

    transformer = Transformer.from_crs(crs_gauss, crs_geo, always_xy=True)

    a = 6378245.0
    ee = 0.00669342162296594323

    def wgs84_to_gcj02(lon, lat):
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

    def gcj02_to_bd09(lon, lat):
        z = math.sqrt(lon * lon + lat * lat) + 0.00002 * math.sin(lat * math.pi * 3000.0 / 180.0)
        theta = math.atan2(lat, lon) + 0.000003 * math.cos(lon * math.pi * 3000.0 / 180.0)
        bd_lon = z * math.cos(theta) + 0.0065
        bd_lat = z * math.sin(theta) + 0.006
        return bd_lon, bd_lat

    # -------- 批量转换 --------
    result = []
    for x, y in points:
        lon, lat = transformer.transform(x, y)
        gcj_lon, gcj_lat = wgs84_to_gcj02(lon, lat)
        bd_lon, bd_lat = gcj02_to_bd09(gcj_lon, gcj_lat)
        result.append([bd_lon, bd_lat])

    return json.dumps(result)





# ======================================================
# 你已有的坐标转换方法（直接调用你自己的）
# ======================================================
# def cgcs2000_gk_to_bd09(points):
#     """
#     points: [(x, y), ...]
#     return: [(bd_lng, bd_lat), ...]
#     """
#     raise NotImplementedError


# ======================================================
# 接口配置
# ======================================================
URL = "http://172.21.22.26:5007/lxhb/repairRegion/save"

HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Origin": "https://app.apifox.com",
    "Pragma": "no-cache",
    "User-Agent": "Mozilla/5.0"
}

MASSIF_ID = "1961265136073211905"


# ======================================================
# 工具函数
# ======================================================
def format_points(points):
    return ",".join([f"{lng} {lat}" for lng, lat in points])


def save_region(region):
    bd09_points = cgcs2000_points_to_bd09(region["points"])
    payload = {
        "massifId": MASSIF_ID,
        "regionName": region["regionName"],
        "points": ''.join(bd09_points),
        "styleConfig": "",
        "remark": "污染土超标区域",
        "minDepth": region["minDepth"],
        "maxDepth": region["maxDepth"],
        "area": region["area"],
        "volume": region["volume"]
    }

    resp = requests.post(
        URL,
        headers=HEADERS,
        data=json.dumps(payload),
        verify=False
    )

    if resp.status_code != 200:
        raise RuntimeError(f"保存失败: {region['regionName']} {resp.text}")

    print(f"✅ 已保存 {region['regionName']}")


# ======================================================
# 全部超标区块数据（表 1.4-9 ～ 1.4-12）
# ======================================================
regions = [

    # ===================== 表 3.2.1-1 0–1m =====================
    {
        "regionName": "砷-0-1m-区块1-1",
        "minDepth": 0,
        "maxDepth": 1,
        "points": [
            (529023.68, 3498472.89),
            (529043.69, 3498458.27),
            (529076.61, 3498433.74),
            (529074.73, 3498401.89),
            (529042.29, 3498360.10),
            (529040.70, 3498338.31),
            (529028.65, 3498328.96),
            (528991.82, 3498320.98),
            (528969.09, 3498346.66),
            (528962.16, 3498365.02),
            (528921.45, 3498370.54),
            (528882.92, 3498362.44),
            (528885.01, 3498339.07),
            (528884.84, 3498315.50),
            (528845.29, 3498271.86),
            (528803.46, 3498299.29),
            (528769.60, 3498311.93),
            (528767.96, 3498335.73),
            (528728.15, 3498331.14),
            (528688.61, 3498333.37),
            (528678.71, 3498321.71),
            (528670.18, 3498308.27),
            (528673.54, 3498337.89),
            (528751.94, 3498342.92),
            (528772.30, 3498386.58),
            (528803.83, 3498374.70),
            (528807.80, 3498432.48),
            (528884.67, 3498432.10),
            (528893.65, 3498496.96),
            (528919.39, 3498490.04),
            (528937.59, 3498493.04),
            (529008.11, 3498464.38),
            (529014.96, 3498475.13)
        ]
    },
    {
        "regionName": "砷-0-1m-区块1-2",
        "minDepth": 0,
        "maxDepth": 1,
        "points": [
            (529041.34, 3498323.62),
            (529064.53, 3498324.56),
            (529088.71, 3498335.17),
            (529095.35, 3498335.21),
            (529096.66, 3498278.18),
            (529025.91, 3498297.12)
        ]
    },
    {
        "regionName": "砷-0-1m-区块1-3",
        "minDepth": 0,
        "maxDepth": 1,
        "points": [
            (528670.18, 3498308.27),
            (528633.06, 3498308.19),
            (528631.03, 3498301.96),
            (528662.27, 3498302.59)
        ]
    },

    # ===================== 表 3.2.1-2 1–2m =====================
    {
        "regionName": "砷-1-2m-区块1-4",
        "minDepth": 1,
        "maxDepth": 2,
        "points": [
            (528919.09, 3498489.50),
            (528922.64, 3498471.66),
            (528920.93, 3498446.90),
            (528949.99, 3498431.37),
            (528929.65, 3498407.67),
            (528967.57, 3498410.96),
            (528962.47, 3498391.11),
            (528962.16, 3498365.02),
            (528927.29, 3498391.79),
            (528921.45, 3498370.54),
            (528921.22, 3498351.05),
            (528884.84, 3498315.50),
            (528848.47, 3498304.92),
            (528830.42, 3498269.88),
            (528823.31, 3498263.90),
            (528778.09, 3498264.22),
            (528777.96, 3498278.66),
            (528745.14, 3498281.11),
            (528726.47, 3498297.98),
            (528722.64, 3498301.83),
            (528727.39, 3498318.43),
            (528709.26, 3498318.27),
            (528688.70, 3498318.40),
            (528689.86, 3498303.73),
            (528670.18, 3498308.27),
            (528673.54, 3498337.89),
            (528749.79, 3498338.30),
            (528772.30, 3498386.58),
            (528803.83, 3498374.70),
            (528807.80, 3498432.48),
            (528884.67, 3498432.10),
            (528893.65, 3498496.96)
        ]
    },

    # ===================== 表 3.2.1-3 2–3m =====================
    {
        "regionName": "砷-2-3m-区块1-10",
        "minDepth": 2,
        "maxDepth": 3,
        "points": [
            (528999.05, 3498468.94),
            (528963.25, 3498442.07),
            (528943.52, 3498468.86),
            (528944.62, 3498490.18)
        ]
    },

    # ===================== 表 3.2.1-4 3–4m =====================
    {
        "regionName": "砷-3-4m-区块1-20",
        "minDepth": 3,
        "maxDepth": 4,
        "points": [
            (528849.42, 3498419.55),
            (528868.56, 3498403.57),
            (528845.45, 3498388.59),
            (528823.75, 3498406.90)
        ]
    },

    # ===================== 表 3.2.1-5 6–7m =====================
    {
        "regionName": "砷-6-7m-区块1-22",
        "minDepth": 6,
        "maxDepth": 7,
        "points": [
            (529018.54, 3498481.05),
            (529044.97, 3498473.52),
            (529041.81, 3498432.49),
            (529010.49, 3498467.77)
        ]
    }

]

# ======================================================
# 主入口
# ======================================================
if __name__ == "__main__":
    print(f"开始入库，共 {len(regions)} 个超标区块...\n")
    for r in regions:
        save_region(r)
    print("\n🎉 全部污染土超标区域已成功入库")
