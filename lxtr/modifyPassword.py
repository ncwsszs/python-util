#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修改密码脚本
用法举例:
  python batch_change_passwords.py --password "NewP@ssw0rd"            # 全体用户改为同一密码
  python batch_change_passwords.py --map passwords.csv                # 使用 CSV (userId,password)
  python batch_change_passwords.py --template "{name[:1]}gjs@2025"    # 按模板生成密码 (python 格式化)
  python batch_change_passwords.py --dry-run                          # 只是打印，不提交
"""

import requests
import argparse
import csv
import time
import sys
from typing import List, Dict, Optional

# ========== 配置区：把下面这些值替换成你自己的 ==========
BASE_URL = "https://xfjg.jseet.cn"
QUERY_API = "/lxhb/massif-user/page"
UPDATE_API = "/lxhb/massif-user/update/password"
# 下面的 HEADERS/Cookies 需要设置为你的有效值（来自浏览器的请求）
DEFAULT_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json;charset=UTF-8",
    # 若你用 token/header auth，把 token 放到下面两项或 cookie 中：
    "token": "a91GfQ5Qbm52Zh7KB52CpLatCOAyyEgOHGvePvkkcoGKBEujIVhFtVzCTdK4gyntrMBW1ZpOJrUDKWTiXaYjiN0A3F0pOObytz7bu7BgasgZxVVwq7tFgJuusCcd3pUd",
    "projectId": "1955145647355101186",  # 根据需要修改
    "Origin": "https://xfjg.jseet.cn",
    "Referer": "https://xfjg.jseet.cn/",
    "User-Agent": "python-requests/2.x",
}
# 如果需要 cookie，可以直接设置下面 COOKIE 字符串（或在 headers 中设置 X-Auth-Token 等）
DEFAULT_COOKIES = {
    # "Token": "....",
    # "HMACCOUNT": "...",
    # 把你需要的 cookie 都放进来
}

# ========== 参数 ==========
REQUEST_TIMEOUT = 15  # 秒
RETRY_COUNT = 3
RETRY_BACKOFF = 1.5  # 指数退避因子


# --------- 辅助函数 ----------
def request_with_retries(session: requests.Session, method: str, url: str, **kwargs) -> requests.Response:
    last_exc = None
    for attempt in range(1, RETRY_COUNT + 1):
        try:
            resp = session.request(method, url, timeout=REQUEST_TIMEOUT, **kwargs)
            return resp
        except Exception as e:
            last_exc = e
            wait = RETRY_BACKOFF ** (attempt - 1)
            print(f"[WARN] 请求失败（尝试 {attempt}/{RETRY_COUNT}）：{e}，{wait:.1f}s 后重试")
            time.sleep(wait)
    raise RuntimeError(f"请求全部重试失败: {last_exc}")


def fetch_users(session: requests.Session, page_num: int = 1, page_size: int = 100) -> Dict:
    """
    调用分页查询接口，返回解析后的 JSON (dict)
    """
    url = BASE_URL + QUERY_API
    payload = {
        "pageNum": page_num,
        "pageSize": page_size,
        "condition": {},
        "total": 0
    }
    resp = request_with_retries(session, "POST", url, json=payload)
    resp.raise_for_status()
    return resp.json()


def fetch_all_users(session: requests.Session, page_size: int = 100) -> List[Dict]:
    users = []
    page = 1
    while True:
        j = fetch_users(session, page_num=page, page_size=page_size)
        if not isinstance(j, dict):
            raise RuntimeError("查询接口返回非 JSON 对象")
        if j.get("code") != 0:
            raise RuntimeError(f"查询接口返回 code != 0: {j}")
        data = j.get("data", {})
        records = data.get("records", [])
        if not records:
            break
        users.extend(records)
        total = data.get("total", None)
        pages = data.get("pages", None)
        # 如果知道总页数，可停止；否则继续直到记录为空
        if pages is not None and page >= pages:
            break
        page += 1
    return users


def update_password(session: requests.Session, user_id: str, new_password: str) -> Dict:
    """
    调用修改密码接口（GET 请求形式，query 参数）
    返回解析后的 JSON
    """
    url = f"{BASE_URL}{UPDATE_API}"
    params = {"userId": user_id, "password": new_password}
    resp = request_with_retries(session, "GET", url, params=params)
    resp.raise_for_status()
    return resp.json()


# --------- 主逻辑 ----------
def load_map_csv(path: str) -> Dict[str, str]:
    """CSV 格式: userId,password（有表头或无表头皆可）"""
    mapping = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
        if not rows:
            return mapping
        # 如果第一行看起来是表头（包含 userId 或 password），跳过
        first = rows[0]
        if any(h.lower() in ("userid", "user_id", "user", "id") for h in first) and any(h.lower() in ("password", "pwd", "pass") for h in first):
            rows = rows[1:]
        for r in rows:
            if len(r) < 2:
                continue
            uid = r[0].strip()
            pwd = r[1].strip()
            if uid:
                mapping[uid] = pwd
    return mapping


def main():
    parser = argparse.ArgumentParser(description="批量修改密码脚本")
    parser.add_argument("--password", help="给所有用户设置相同的密码（与 --map/--template 互斥）")
    parser.add_argument("--map", help="指定 CSV 文件，格式: userId,password")
    parser.add_argument("--template", help="密码模板，例如 '{name[:1]}gjs@2025'，支持用户对象的字段格式化")
    parser.add_argument("--page-size", type=int, default=100, help="分页 size（默认 100）")
    parser.add_argument("--dry-run", action="store_true", help="仅打印将要修改的用户，不真正提交")
    parser.add_argument("--limit", type=int, default=0, help="限制修改数量（0 表示不限制）")
    parser.add_argument("--skip-system-users", action="store_true", help="跳过 role 或其他条件的系统用户（可根据需要扩展）")
    args = parser.parse_args()

    # 校验互斥
    mode_count = sum(bool(x) for x in (args.password, args.map, args.template))
    if mode_count == 0:
        print("错误：请指定 --password 或 --map 或 --template 其中之一。")
        sys.exit(2)
    if mode_count > 1:
        print("错误：--password, --map, --template 互斥，请只选一项。")
        sys.exit(2)

    # 创建 session 并注入 headers/cookies（你可以在上面 DEFAULT_HEADERS/DEFAULT_COOKIES 修改）
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    # 如果你想用原始 cookie 字符串，下面两行可以替换
    if DEFAULT_COOKIES:
        session.cookies.update(DEFAULT_COOKIES)

    print("[INFO] 开始查询用户...")
    users = fetch_all_users(session, page_size=args.page_size)
    print(f"[INFO] 查询到用户数: {len(users)}")
    if len(users) == 0:
        print("[WARN] 没有用户可处理，退出。")
        return

    # 构造要修改的列表
    mapping_from_csv = {}
    if args.map:
        mapping_from_csv = load_map_csv(args.map)
        print(f"[INFO] 从 CSV 加载到 {len(mapping_from_csv)} 条 userId->password 映射")

    to_update = []
    for u in users:
        uid = str(u.get("id"))
        if not uid:
            continue
        # 如果需要跳过系统用户，可基于 role/账号名等判断
        if args.skip_system_users:
            role = u.get("role")
            if role is not None and str(role) == "0":  # 仅示例：根据实际情况调整
                # 这里示例跳过 role==0 的用户（通常 admin），如果不想跳过请删除这段
                # 如果你不希望跳过，直接注释或删除上面 if 块
                print(f"[DEBUG] 跳过系统用户 {uid} (role={role})")
                continue

        # 决定密码
        if args.password:
            pwd = args.password
        elif args.map:
            if uid in mapping_from_csv:
                pwd = mapping_from_csv[uid]
            else:
                # 如果 CSV 中没有指定该用户，则跳过（或可设置默认）
                print(f"[WARN] CSV 中未找到 userId={uid} 的密码，跳过")
                continue
        else:  # template
            # 模板格式化时可用 user 的字段（比如 name）
            try:
                # 允许使用 u.get("name"), u["name"] 等
                # 将 u 的 key 映射为局部变量 name, phone, id 等便于格式化
                locals_for_template = dict(u)
                pwd = args.template.format(**locals_for_template)
            except Exception as e:
                print(f"[ERROR] 模板格式化 userId={uid} 出错: {e}; 跳过")
                continue

        to_update.append((uid, pwd, u))

        if args.limit and len(to_update) >= args.limit:
            break

    print(f"[INFO] 将要处理的用户数量: {len(to_update)}")
    if args.dry_run:
        print("[DRY-RUN] 以下为将要修改的 userId -> password 列表（仅显示前 200 字符）:")
        for uid, pwd, u in to_update:
            print(f"  {uid} -> {pwd}    name={u.get('name')}")
        print("[DRY-RUN] 结束，不会进行网络提交。")
        return

    # 真正执行
    success = []
    failures = []
    for uid, pwd, u in to_update:
        try:
            print(f"[INFO] 修改 userId={uid} name={u.get('name')} 密码为 '{pwd}' ...", end="")
            resp = update_password(session, uid, pwd)
            # 判断返回
            if isinstance(resp, dict) and resp.get("code") == 0:
                print(" 成功")
                success.append(uid)
            else:
                print(f" 失败: {resp}")
                failures.append((uid, resp))
        except Exception as e:
            print(f" 异常失败: {e}")
