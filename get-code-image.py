import requests
import base64
import time
import os
from datetime import datetime

# 配置部分
url = "http://172.21.21.101:8800/captchaImage"
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8,en-US;q=0.7,en-IE;q=0.6,en-GB-oxendict;q=0.5,en-GB;q=0.4,zh-TW;q=0.3',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Language': 'zh_CN',
    'Pragma': 'no-cache',
    'Referer': 'http://172.21.23.165/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    'clientid': 'e5cd7e4891bf95d1d19206ce24a7b32e'
}

# 目标目录（根据需要修改）
save_dir = "./test2/"

# 确保目录存在
os.makedirs(save_dir, exist_ok=True)

# 保存图片函数
def save_captcha_image(base64_img, index):
    if base64_img.startswith("data:image"):
        base64_img = base64_img.split(",")[1]

    image_data = base64.b64decode(base64_img)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"captcha_{index}_{timestamp}.png"
    file_path = os.path.join(save_dir, filename)
    with open(file_path, 'wb') as f:
        f.write(image_data)
    print(f"已保存验证码图片: {file_path}")

# 请求次数和间隔
num_requests = 100
delay_seconds = 6.1

# 执行循环请求
for i in range(num_requests):
    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            json_data = response.json()
            save_captcha_image(json_data['img'], i + 1)
        else:
            print(f"[请求 {i + 1}] HTTP状态码异常：{response.status_code}")
    except Exception as e:
        print(f"[请求 {i + 1}] 发生异常：{e}")

    time.sleep(delay_seconds)
