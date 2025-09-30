import re
import requests
import urllib.parse
from datetime import datetime

# 配置参数
log_file_path = 'info.log'  # 日志文件路径
target_cid = '860065074167539'
url = 'https://xfjg.jseet.cn/lxhb/index/gps?jsonStr='
start_time = datetime.strptime('2025-04-17 11:30:30', '%Y-%m-%d %H:%M:%S')
end_time = datetime.strptime('2025-04-17 13:30:30', '%Y-%m-%d %H:%M:%S')

# 提取上传位置信息并发送
def extract_and_send(log_path):
    with open(log_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    current_time = None
    valid_lines = []

    # 提取有效日志段
    for line in lines:
        # 尝试提取日志时间
        time_match = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
        if time_match:
            current_time = datetime.strptime(time_match.group(1), '%Y-%m-%d %H:%M:%S')

        # 判断时间范围
        if current_time and start_time <= current_time <= end_time:
            # 必须包含目标cid
            if target_cid in line and '上传位置信息：' in line:
                valid_lines.append(line.strip())

    # 处理每一行上传位置信息
    for i, line in enumerate(valid_lines, 1):
        match = re.search(r'上传位置信息：(.*)', line)
        if match:
            json_str = match.group(1).strip()
            # encoded_str = urllib.parse.quote(json_str, safe='')
            full_url = f"{url}{json_str}"

            print(full_url)

            try:
                response = requests.get(full_url)
                print(f"[{i}] Sent at {current_time}: {json_str}")
                print(f"    Response: {response.status_code}, {response.text}\n")
            except Exception as e:
                print(f"[{i}] Failed to send: {json_str}")
                print(f"    Error: {e}\n")

if __name__ == "__main__":
    extract_and_send(log_file_path)
