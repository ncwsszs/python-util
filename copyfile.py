import os
import shutil
import time
from pathlib import Path

# ======== 配置路径 ========
src_dir = Path(r"G:\桌面文件\文档\瑞景中台\对接文档3")  # 源文件夹
dst_dir = Path(r"G:\桌面文件\文档\瑞景中台\对接文档")  # 目标文件夹

# 如果目标目录存在，可以选择覆盖
shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)

# 获取当前时间戳
current_time = time.time()

# 先更新文件夹的时间（先递归文件夹，再文件），防止文件夹时间被内部文件覆盖
for folder in sorted(dst_dir.rglob("*"), key=lambda p: p.is_file()):
    try:
        os.utime(folder, (current_time, current_time))
    except Exception as e:
        print(f"无法更新时间: {folder}，原因: {e}")

print(f"已完成复制，并更新 {dst_dir} 下所有文件和文件夹的修改时间")
