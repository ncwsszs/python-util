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

# 正则匹配 Nginx 日志
pattern = re.compile(
    r'(?P<ip>\d+\.\d+\.\d+\.\d+) - - \[(?P<day>\d{2})/(?P<mon>[A-Za-z]{3})/(?P<year>\d{4}):(?P<time>\d{2}:\d{2}:\d{2}) [+\-]\d+\] '
    r'"GET (?P<url>/prod-api/file/downloadFIle\?file=[^ ]+)'

)

# pattern = re.compile(
#     r'(?P<ip>\d+\.\d+\.\d+\.\d+)\s+- -\s+\['
#     r'(?P<day>\d{2})/(?P<mon>[A-Za-z]{3})/(?P<year>\d{4}):'
#     r'(?P<time>\d{2}:\d{2}:\d{2}) [+\-]\d+\]\s+'
#     r'"GET\s+/+/prod-api/file/downloadFIle\?file=[^ ]+'
# )


def parse_lines(lines):
    """解析日志行，返回一个 dict {日期: [记录]}"""
    downloads_by_date = defaultdict(list)
    for line in lines:
        m = pattern.search(line)
        if not m:
            continue
        ip = m.group("ip")
        day, mon_str, year, time_str = m.group("day"), m.group("mon"), m.group("year"), m.group("time")
        month = month_map[mon_str]
        date_str = f"{year}年{month}月{int(day)}日"

        # 解析文件名
        url = m.group("url")
        qs = parse_qs(urlsplit(url).query)
        file_val = qs.get('file', [''])[0]
        filename = unquote(file_val).split("/")[-1]

        downloads_by_date[date_str].append(f"{ip} - [{time_str}] 下载文件：《{filename}》")
    return downloads_by_date

def merge_results(results):
    """合并多个进程的 dict"""
    merged = defaultdict(list)
    for d in results:
        for k, v in d.items():
            merged[k].extend(v)
    return merged

def chunked_iterable(iterable, size):
    """按 size 分块"""
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk

if __name__ == "__main__":
    workers = cpu_count()  # 自动使用全部 CPU 核
    chunk_size = 50000     # 每个进程处理的行数，可以调整

    with open(logfile, "r", encoding="utf-8") as f:
        chunks = list(chunked_iterable(f, chunk_size))

    with Pool(processes=workers) as pool:
        results = pool.map(parse_lines, chunks)

    merged = merge_results(results)

    # 按日期倒序输出
    for date in merged.keys():
        print(date)
        for entry in merged[date]:
            print(entry)
        print()
