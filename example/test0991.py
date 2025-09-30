import re
from collections import Counter

log_file_path = 'access.log'
log_pattern = re.compile(r'"(?:GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD) (\S+) HTTP/')

# 单独模块前缀匹配
prefix_mapping = {
    "/prod-api/getInfo": "统一门户",
    "/prod-api/oauth/token": "统一身份认证",
    "/prod-api/municipal/get": "生产调度平台",
    "/prod-api/parkFirstScreen/": "可视化大屏"
}

# 专门统计“数据中台”（包括 park/ 下所有请求）
data_platform_prefix = "/prod-api/park/"

# 初始化计数器
module_counter = Counter()
data_platform_count = 0

with open(log_file_path, 'r', encoding='utf-8') as f:
    for line in f:
        match = log_pattern.search(line)
        if not match:
            continue
        uri = match.group(1)

        # 统计可视化大屏、统一门户等
        matched = False
        for prefix, name in prefix_mapping.items():
            if uri.startswith(prefix):
                module_counter[name] += 1
                matched = True
                break

        # 统计所有 /prod-api/park/ 路径（包括可视化大屏）
        if uri.startswith(data_platform_prefix):
            data_platform_count += 1

# 添加数据中台汇总
module_counter["数据中台"] = data_platform_count

# 输出美观格式
print("\n📊 模块访问统计结果")
print("=" * 40)
print(f"{'模块名称':<20} {'访问次数':>10}")
print("-" * 40)
for module, count in module_counter.most_common():
    print(f"{module:<20} {count:>10}")
print("-" * 40)
print(f"{'总访问量':<20} {sum(module_counter.values()):>10}")
print("=" * 40)
