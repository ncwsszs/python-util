from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import re

# 设置参数
URL = "http://rjopenipark.wxrjpark.com/#/doc"  # ← 替换成你的实际网址
SAVE_DIR = "saved_docs"
WAIT = 2.0  # 等待加载时间

# 初始化浏览器
options = Options()
# options.add_argument("--headless")  # 可选：无头模式
driver = webdriver.Chrome(options=options)
driver.get(URL)
wait = WebDriverWait(driver, 10)
time.sleep(WAIT)

os.makedirs(SAVE_DIR, exist_ok=True)

def safe_name(text):
    return re.sub(r'[\\/:*?"<>|]', "_", text.strip())

# 获取所有一级菜单（el-submenu）
submenu_elements = driver.find_elements(By.CSS_SELECTOR, ".el-submenu")

for i in range(len(submenu_elements)):
    submenu_elements = driver.find_elements(By.CSS_SELECTOR, ".el-submenu")
    submenu = submenu_elements[i]

    # 获取一级菜单名称
    try:
        title_el = submenu.find_element(By.CSS_SELECTOR, ".el-submenu__title span")
        first_level_name = safe_name(title_el.text)
    except:
        first_level_name = f"一级_{i+1}"

    print(f"\n📁 一级菜单: {first_level_name}")
    first_level_dir = os.path.join(SAVE_DIR, first_level_name)
    os.makedirs(first_level_dir, exist_ok=True)

    # 检查是否已展开
    class_attr = submenu.get_attribute("class")
    is_opened = "is-opened" in class_attr

    if not is_opened:
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", submenu)
            time.sleep(0.3)
            driver.execute_script("arguments[0].querySelector('.el-submenu__title').click();", submenu)
            time.sleep(WAIT)
        except Exception as e:
            print(f"⚠️ 展开失败: {e}")

    # 获取二级菜单项
    try:
        items = submenu.find_elements(By.CSS_SELECTOR, "ul.el-menu--inline > li.el-menu-item")
    except:
        items = []

    print(f"   共 {len(items)} 个二级菜单")

    for j, item in enumerate(items):
        try:
            span = item.find_element(By.TAG_NAME, "span")
            second_name = safe_name(span.text or f"子菜单_{j+1}")
        except:
            second_name = f"子菜单_{j+1}"

        print(f"   → 点击: {second_name}")

        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", item)
            time.sleep(0.2)
            driver.execute_script("arguments[0].click();", item)
            time.sleep(WAIT)

            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".doc-content")))
            time.sleep(0.5)

            # 获取内容及样式
            content_element = driver.find_element(By.CSS_SELECTOR, ".doc-content")
            content_html = content_element.get_attribute("outerHTML")
            head_html = driver.execute_script("return document.head.innerHTML")
            full_html = f"<html><head>{head_html}</head><body>{content_html}</body></html>"

            # 保存文件
            file_path = os.path.join(first_level_dir, f"{second_name}.html")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(full_html)

            print(f"      ✅ 保存成功: {file_path}")

        except Exception as e:
            print(f"      ⚠️ 点击或保存失败: {e}")

driver.quit()
print("\n✅ 所有页面保存完成！")
