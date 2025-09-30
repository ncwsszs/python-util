import re
from urllib.parse import urlsplit, parse_qs, unquote
from collections import defaultdict
from multiprocessing import Pool, cpu_count

logfile = "access.log"

# 月份映射
month_map = {
    "Jan": "1", "Feb": "2", "Mar": "3", "Apr": "4", "May": "5", "Jun": "6",
    "Jul": "7", "Aug": "8", "Sep": "9", "Oct": "10", "Nov": "11", "Dec": "12"
}

# 宽松匹配 downloadFIle（忽略大小写，允许多 /）
pattern = re.compile(
    r'(?P<ip>\d+\.\d+\.\d+\.\d+)\s+- -\s+\['
    r'(?P<day>\d{2})/(?P<mon>[A-Za-z]{3})/(?P<year>\d{4}):'
    r'(?P<time>\d{2}:\d{2}:\d{2}) [+\-]\d+\]\s+'
    r'"GET\s+/+prod-api/file/downloadfile\?file=[^ ]+',
    re.IGNORECASE
)

def parse_lines(lines):
    """解析日志行"""
    downloads_by_date = defaultdict(list)
    for line in lines:
        m = pattern.search(line)
        if not m:
            continue

        ip = m.group("ip")
        day, mon_str, year, time_str = m.group("day"), m.group("mon"), m.group("year"), m.group("time")
        month = month_map[mon_str]
        date_str = f"{year}年{month}月{int(day)}日"

        # 从整行提取 URL
        url_match = re.search(r'GET\s+(/+prod-api/file/downloadfile\?file=[^ ]+)', line, re.IGNORECASE)
        if not url_match:
            continue

        url = url_match.group(1)
        qs = parse_qs(urlsplit(url).query)
        file_val = qs.get('file', [''])[0]
        filename = unquote(file_val).split("/")[-1]

        downloads_by_date[date_str].append(f"{ip} - [{time_str}] 下载文件：《{filename}》")
    return downloads_by_date

def merge_results(results):
    merged = defaultdict(list)
    for d in results:
        for k, v in d.items():
            merged[k].extend(v)
    return merged

def chunked_iterable(iterable, size):
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk

if __name__ == "__main__":
    workers = cpu_count()
    chunk_size = 50000

    with open(logfile, "r", encoding="utf-8") as f:
        chunks = list(chunked_iterable(f, chunk_size))

    with Pool(processes=workers) as pool:
        results = pool.map(parse_lines, chunks)

    merged = merge_results(results)

    # 输出
    for date in merged.keys():
        print(date)
        for entry in merged[date]:
            print(entry)
        print()
