#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把查询到的所有用户的密码统一改为 gjs@2025（根据 userId 调用修改接口）
用法示例:
  python batch_set_gjs2025.py --dry-run
  python batch_set_gjs2025.py --limit 10
"""

import requests
import argparse
import time
import sys

# ========== 配置区：请替换为你的真实值 ==========
BASE_URL = "https://xfjg.jseet.cn"
QUERY_API = "/lxhb/massif-user/page"
UPDATE_API = "/lxhb/massif-user/update/password"  # GET ?userId=...&password=...
FIXED_PASSWORD = "gjs@2025"

# 把下面 headers / cookies 换成你实际的（可以直接复制浏览器的请求头/cookie）
DEFAULT_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json;charset=UTF-8",
    "token": "a91GfQ5Qbm52Zh7KB52CpLatCOAyyEgOHGvePvkkcoGKBEujIVhFtVzCTdK4gyntrMBW1ZpOJrUDKWTiXaYjiN0A3F0pOObytz7bu7BgasgZxVVwq7tFgJuusCcd3pUd",  # 示例
    "projectId": "1955145647355101186",
    "Origin": "https://xfjg.jseet.cn",
    "Referer": "https://xfjg.jseet.cn/",
    "User-Agent": "python-requests/2.x",
}
DEFAULT_COOKIES = {
    # 如果需要也可以把 cookie 放这里，例如:
    # "HMACCOUNT": "3080B9036D2E8538",
    # "X-Auth-Token": "...",
}

# ========== 运行参数 ==========
REQUEST_TIMEOUT = 15
RETRY_COUNT = 3
RETRY_BACKOFF = 1.5  # 重试指数退避


def request_with_retries(session: requests.Session, method: str, url: str, **kwargs) -> requests.Response:
    last_exc = None
    for attempt in range(1, RETRY_COUNT + 1):
        try:
            resp = session.request(method, url, timeout=REQUEST_TIMEOUT, **kwargs)
            return resp
        except Exception as e:
            last_exc = e
            wait = RETRY_BACKOFF ** (attempt - 1)
            print(f"[WARN] 请求失败（{attempt}/{RETRY_COUNT}）：{e}，{wait:.1f}s后重试")
            time.sleep(wait)
    raise RuntimeError(f"请求全部重试失败: {last_exc}")


def fetch_users_page(session: requests.Session, page_num: int = 1, page_size: int = 100):
    url = BASE_URL + QUERY_API
    payload = {"pageNum": page_num, "pageSize": page_size, "condition": {}, "total": 0}
    resp = request_with_retries(session, "POST", url, json=payload)
    resp.raise_for_status()
    return resp.json()


def fetch_all_users(session: requests.Session, page_size: int = 100):
    all_users = []
    page = 1
    while True:
        j = fetch_users_page(session, page_num=page, page_size=page_size)
        if not isinstance(j, dict):
            raise RuntimeError("查询接口返回非 JSON")
        if j.get("code") != 0:
            raise RuntimeError(f"查询接口异常: {j}")
        data = j.get("data", {})
        records = data.get("records", [])
        if not records:
            break
        all_users.extend(records)
        pages = data.get("pages")
        if pages is not None and page >= pages:
            break
        page += 1
    return all_users


def update_password(session: requests.Session, user_id: str, new_password: str):
    url = f"{BASE_URL}{UPDATE_API}"
    params = {"userId": user_id, "password": new_password}
    resp = request_with_retries(session, "GET", url, params=params)
    resp.raise_for_status()
    return resp.json()


def main():
    parser = argparse.ArgumentParser(description="批量将用户密码改为 gjs@2025（按 userId）")
    parser.add_argument("--page-size", type=int, default=100, help="分页 size，默认 100")
    parser.add_argument("--dry-run", action="store_true", help="只打印将要修改的 userId 列表，不提交")
    parser.add_argument("--limit", type=int, default=0, help="最多修改多少个用户（0 表示不限制）")
    parser.add_argument("--skip-role-zero", action="store_true", help="示例：跳过 role == 0 的用户（通常 admin），按需使用或注释掉")
    args = parser.parse_args()

    # 创建 session，注入 headers/cookies
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    if DEFAULT_COOKIES:
        session.cookies.update(DEFAULT_COOKIES)

    print("[INFO] 查询用户中...")
    users = fetch_all_users(session, page_size=args.page_size)
    print(f"[INFO] 查询到 {len(users)} 个用户")

    if not users:
        print("[WARN] 没有用户可处理，退出。")
        return

    # 准备要修改的 userId 列表
    to_change = []
    for u in users:
        uid = u.get("id")
        if not uid:
            continue
        if args.skip_role_zero:
            role = u.get("role")
            if role is not None and str(role) == "0":
                # 跳过 admin/system 用户（可选）
                print(f"[DEBUG] 跳过系统用户 {uid} (role={role})")
                continue
        to_change.append((str(uid), u.get("name")))

        if args.limit and len(to_change) >= args.limit:
            break

    print(f"[INFO] 将要处理的数量: {len(to_change)} (password -> {FIXED_PASSWORD})")
    if args.dry_run:
        print("[DRY-RUN] 以下为将要修改的 userId 列表：")
        for uid, name in to_change:
            print(f"  {uid}    name={name}")
        print("[DRY-RUN] 结束（未提交）。")
        return

    successes = []
    failures = []
    for uid, name in to_change:
        try:
            print(f"[INFO] 修改 userId={uid} name={name} ...", end="")
            res = update_password(session, uid, FIXED_PASSWORD)
            if isinstance(res, dict) and res.get("code") == 0:
                print(" 成功")
                successes.append(uid)
            else:
                print(f" 失败: {res}")
                failures.append((uid, res))
        except Exception as e:
            print(f" 异常: {e}")
            failures.append((uid, str(e)))
        # 若服务器有限流要求，可在此处加 sleep，例如 time.sleep(0.1)

    print("=" * 40)
    print(f"完成。成功: {len(successes)}，失败: {len(failures)}")
    if failures:
        print("失败前 20 条：")
        for uid, info in failures[:20]:
            print(f"  {uid} -> {info}")

    # 写结果文件
    with open("batch_set_gjs2025_result.txt", "w", encoding="utf-8") as f:
        f.write(f"成功 {len(successes)} 条\n")
        for s in successes:
            f.write(s + "\n")
        f.write(f"\n失败 {len(failures)} 条\n")
        for uid, info in failures:
            f.write(f"{uid}\t{info}\n")

if __name__ == "__main__":
    main()
