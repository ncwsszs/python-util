import json
import re
import time
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler

import requests
from bs4 import BeautifulSoup


def getPubHtml(year):
    url = "https://sousuoht.www.gov.cn/athena/forward/486B5ABFBAD0FF5743F5E82E007EF04DDD6388E7989E9EC9CC7B84917AC81A5F"

    data = {
        "code": "18122f54c5c",
        "thirdPartyCode": "thirdparty_code_107",
        "thirdPartyTableId": 30,
        "resultFields": [
            "pub_url",
            "maintitle",
            "fwzh",
            "cwrq",
            "publish_time"
        ],
        "trackTotalHits": "true",
        "searchFields": [
            {
                "fieldName": "maintitle",
                "searchWord": "节假日" + str(year)
            }
        ],
        "isPreciseSearch": 0,
        "sorts": [
            {
                "sortField": "publish_time",
                "sortOrder": "DESC"
            }
        ],
        "childrenInfoIds": [
            [
                "1102"
            ]
        ],
        "pageSize": 10,
        "pageNo": 1
    }

    # 定义请求头
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,en-IE;q=0.6,en-GB-oxendict;q=0.5,en-GB;q=0.4',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'https://www.gov.cn',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'athenaAppKey': 'LFOL0jku4XoD%2FAjX7vaYQj45AJrIIEfsQnHXKNdRDU8crE5tXgfAhuCi69UGOTTCFDARYGa%2F6PHg3hMLgI1X9a8tCxoic%2Bhm5rm5Eoum2rrih%2B6ynljeBP52KzqTkCylwzeCS3vgmFw48tIobsB0DIHJnA24m0OkEP88nv0e8dE%3D',
        'athenaAppName': '%E5%9B%BD%E7%BD%91%E6%90%9C%E7%B4%A2',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Cookie': 'acw_tc=2760778516884476193401666e1b975b3a4311b7ffe9adeda44d525a532f48'
    }
    json_data = json.dumps(data)

    proxies = {
        'http': 'http://127.0.0.1:10808',
        'https': 'http://127.0.0.1:10808'  # https -> http
    }
    response = requests.post(url, headers=headers, data=json_data.encode('utf-8') ,proxies=proxies)

    # 设置响应的编码方式为UTF-8
    response.encoding = 'utf-8'

    # 检查请求是否成功
    if response.status_code == 200:
        response_data = response.json()
        return response_data['result']['data']['list'][0]['pub_url']
    else:
        print('请求失败，状态码：', response.status_code)

    print(response.text)
    return


# def getContent(url, year):
#     url = url
#     response = requests.get(url)
#     response.encoding = 'utf-8'  # 手动指定正确的编码方式
#     html_content = response.content.decode('utf-8')
#     soup = BeautifulSoup(html_content, 'html.parser')
#     title = soup.title.string
#
#     ps = soup.find_all('p')
#     separators = ['一、', '二、', '三、', '四、', '五、', '六、', '七、', '八、', '九、', '十、']
#     array = []
#     for p in ps:
#         array.append(p.text)
#
#     filtered_array = [element for element in array if any(value in element for value in separators)]
#
#     result = []
#     tiao_ban = []
#     for text in filtered_array:
#         # 根据句号分割
#         array_1 = text.split('。')
#         text_1 = array_1[0]
#         array_2 = text_1.split('至')
#         result += get_date(array_2, match_year=year, is_tiaoban=False)
#
#         if len(array_1) >= 2:
#             # 调休
#             text_2 = array_1[1]
#             array_3 = text_2.split('）、')
#             tiao_ban += get_date(array_3, match_year=year, is_tiaoban=True)
#
#     return {
#         'vacation_date': result,
#         'work_date': tiao_ban,
#         'title': title
#     }

def parse_vacation_dates(text, year):
    result = []

    # 正常完整的起止日期：X月X日 至 X月X日
    full_ranges = re.findall(r'(\d{1,2})月(\d{1,2})日（.*?）?至(\d{1,2})月(\d{1,2})日', text)

    for m1, d1, m2, d2 in full_ranges:
        start_date = datetime(year, int(m1), int(d1))
        end_date = datetime(year, int(m2), int(d2))
        while start_date <= end_date:
            result.append(start_date.strftime('%Y-%m-%d'))
            start_date += timedelta(days=1)

    # 省略结束月份：X月X日 至 X日
    partial_ranges = re.findall(r'(\d{1,2})月(\d{1,2})日（.*?）?至(\d{1,2})日', text)

    for m1, d1, d2 in partial_ranges:
        start_date = datetime(year, int(m1), int(d1))
        end_date = datetime(year, int(m1), int(d2))  # 默认结束月与开始月相同
        while start_date <= end_date:
            result.append(start_date.strftime('%Y-%m-%d'))
            start_date += timedelta(days=1)

    # 单日放假，如 “1月1日（周三）放假1天”
    singles = re.findall(r'(\d{1,2})月(\d{1,2})日（.*?）?放假\d+天', text)

    for m, d in singles:
        try:
            result.append(datetime(year, int(m), int(d)).strftime('%Y-%m-%d'))
        except:
            continue

    return result



def parse_work_dates(text, year):
    result = []

    # 1月26日（周日）、2月8日（周六）上班
    matches = re.findall(r'(\d{1,2})月(\d{1,2})日（.*?）?', text)
    if '上班' in text:
        for m, d in matches:
            try:
                date_obj = datetime(year, int(m), int(d))
                result.append(date_obj.strftime('%Y-%m-%d'))
            except:
                continue

    return result


def getContent(url, year):
    response = requests.get(url)
    response.encoding = 'utf-8'
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    title = soup.title.string if soup.title else ""

    ps = soup.find_all('p')
    separators = ['一、', '二、', '三、', '四、', '五、', '六、', '七、', '八、', '九、', '十、']

    array = []
    for p in ps:
        text = p.get_text(strip=True)
        if any(sep in text for sep in separators):
            array.append(text)

    vacation_dates = []
    work_dates = []

    for text in array:
        # 起止日期放假部分（至、放假共几天）
        vacation_dates += parse_vacation_dates(text, year)

        # 上班日、调休部分（上班日期或“不调休”）
        work_dates += parse_work_dates(text, year)

    return {
        'vacation_date': sorted(set(vacation_dates)),
        'work_date': sorted(set(work_dates)),
        'title': title
    }


def get_date(array, match_year, is_tiaoban):
    result = []
    for arr_1 in array:
        # 获取年份
        pattern = r"\d+(?=[年])"
        matches = re.findall(pattern, arr_1)
        if len(matches) > 0:
            year = matches[0]
        else:
            year = match_year
        # 获取月份
        pattern = r"\d+(?=[月])"
        matches_month = re.findall(pattern, arr_1)
        if len(matches_month) > 0:
            month = matches_month[0]
        else:
            continue
        # 获取天数
        pattern = r"\d+(?=[日])"
        matches_day = re.findall(pattern, arr_1)
        if len(matches_day) == 0:
            return []
        day = matches_day[0]
        date = datetime(int(year), int(month), int(day))
        # formatted_date = date.strftime("%Y-%m-%d")
        result.append(date)
    date_list = []

    if is_tiaoban:
        for item in result:
            date_list.append(item.strftime('%Y-%m-%d'))
        return date_list

    if len(result) > 1:
        while result[0] <= result[1]:
            date_list.append(result[0].strftime("%Y-%m-%d"))
            result[0] += timedelta(days=1)
    else:
        date_list.append(result[0].strftime("%Y-%m-%d"))
    return date_list


def get_list(year):
    pub_url = getPubHtml(year)
    return getContent(pub_url, year)


def main():
    run_server()


# 定义自定义的请求处理类
# class RequestHandler(BaseHTTPRequestHandler):
#     def do_POST(self):
#         # 获取请求体的内容
#         content_length = int(self.headers['Content-Length'])
#         post_data = self.rfile.read(content_length).decode('utf-8')
#
#         # 解析JSON数据
#         try:
#             json_data = json.loads(post_data)
#         except json.JSONDecodeError:
#             self.send_response(400)
#             self.send_header('Content-type', 'text/html')
#             self.end_headers()
#             self.wfile.write(b'Invalid JSON data')
#             return
#
#         data = json_data['year']
#
#         result = get_list(data)
#         # 处理请求
#         # 在这里可以根据需要对接收到的JSON数据进行处理
#         # ...
#         # 构造要返回的数据
#         response_data = {
#             'status': 'success',
#             'message': 'Request processed successfully',
#             'data': result
#         }
#         response_json = json.dumps(response_data)
#
#         # 发送响应
#         self.send_response(200)
#         self.send_header('Content-type', 'application/json')
#         self.end_headers()
#         self.wfile.write(response_json.encode('utf-8'))
from urllib.parse import urlparse, parse_qs

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 解析查询参数
        query_components = parse_qs(urlparse(self.path).query)
        if 'year' not in query_components:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "error", "message": "Missing year parameter"}')
            return

        try:
            year = int(query_components['year'][0])
        except ValueError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "error", "message": "Invalid year format"}')
            return

        result = get_list(year)

        # 构造响应
        response_data = {
            'status': 'success',
            'message': 'Request processed successfully',
            'data': result
        }
        response_json = json.dumps(response_data)

        # 返回响应
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(response_json.encode('utf-8'))


def run_server():
    host = '127.0.0.1'  # 监听的主机地址
    port = 7786  # 监听的端口号

    server = HTTPServer((host, port), RequestHandler)
    print(f'Server listening on {host}:{port}')
    server.serve_forever()


if __name__ == '__main__':
    main()
