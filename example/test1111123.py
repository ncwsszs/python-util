import re
from collections import Counter

log_file_path = 'access.log'

# 正则提取 URI
log_pattern = re.compile(r'"(?:GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD) (\S+) HTTP/')

# 模糊匹配路径前缀 => 分类名称
prefix_mapping = {
    "/prod-api/getInfo": "统一门户",
    "/prod-api/oauth/token": "统一身份认证",
    "/prod-api/municipal/get": "生产调度平台",
    "/prod-api/parkFirstScreen": "可视化大屏",
    "/prod-api/park": "数据中台",
}

counter = Counter()

with open(log_file_path, 'r', encoding='utf-8') as f:
    for line in f:
        match = log_pattern.search(line)
        if not match:
            continue
        uri = match.group(1)

        # 匹配路径前缀
        for prefix, category in prefix_mapping.items():
            if uri.startswith(prefix):
                counter[category] += 1
                break  # 只取第一个匹配项

# 打印格式化结果
total = sum(counter.values())

print("\n📊 模块访问统计结果")
print("=" * 40)
print(f"{'模块名称':<20} {'访问次数':>10}")
print("-" * 40)
for category, count in counter.most_common():
    print(f"{category:<20} {count:>10}")
print("-" * 40)
print(f"{'总访问量':<20} {total:>10}")
print("=" * 40)
