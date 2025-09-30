import re
from urllib.parse import unquote
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# 日志文件路径
logfile = "access.log"

# 正则匹配
pattern = re.compile(
    r'(?P<ip>\d+\.\d+\.\d+\.\d+).*?\[(?P<datetime>\d{2}/[A-Za-z]{3}/\d{4}):(?P<time>\d{2}:\d{2}:\d{2}) .*?\] '
    r'"GET\s+/prod-api/file/downloadFIle\?file=(?P<file>[^ ]+)"'
)

# 月份映射
month_map = {
    "Jan": "1", "Feb": "2", "Mar": "3", "Apr": "4", "May": "5", "Jun": "6",
    "Jul": "7", "Aug": "8", "Sep": "9", "Oct": "10", "Nov": "11", "Dec": "12"
}

def parse_line(line):
    """解析一行日志，返回 (日期字符串, 格式化输出)"""
    m = pattern.search(line)
    if not m:
        return None
    ip = m.group("ip")
    log_date = m.group("datetime")
    log_time = m.group("time")
    file_encoded = m.group("file")

    # URL 解码
    file_decoded = unquote(file_encoded)

    # 只取文件名
    filename = file_decoded.split("/")[-1]

    # 日期格式化
    day, mon_str, year = log_date.split("/")
    month = month_map[mon_str]
    date_str = f"{year}年{month}月{int(day)}日"

    return date_str, f"{ip} - [{log_time}] 下载文件：《{filename}》"

downloads_by_date = defaultdict(list)

# 多线程解析
with open(logfile, "r", encoding="utf-8") as f:
    lines = f.readlines()

with ThreadPoolExecutor(max_workers=8) as executor:  # 可以改 max_workers
    for result in executor.map(parse_line, lines):
        if result:
            date_str, entry = result
            downloads_by_date[date_str].append(entry)

# 按日期倒序输出
for date in sorted(downloads_by_date.keys(), reverse=True):
    print(date)
    for entry in downloads_by_date[date]:
        print(entry)
    print()
