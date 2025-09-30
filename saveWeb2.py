from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

URL = "https://open-icc.dahuatech.com/#/home?url=%3Fnav%3Dwiki%2Fevo-oauth%2FuserPass.html&version=enterprisebase/5.0.16&blank=true"  # 替换成你的网页
SAVE_DIR = "saved_pages"

driver = webdriver.Chrome()
driver.get(URL)
wait = WebDriverWait(driver, 10)

# 切换到左侧菜单iframe
menu_iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
driver.switch_to.frame(menu_iframe)

# 获取一级菜单
first_level_items = driver.find_elements(By.CSS_SELECTOR, "#api_list > li")

for li in first_level_items:
    first_name = li.find_element(By.TAG_NAME, "a").text.strip()

    # 展开一级菜单（如果有子菜单）
    driver.execute_script("arguments[0].click();", li.find_element(By.TAG_NAME, "a"))
    time.sleep(0.3)

    # 获取二级菜单（子菜单 ul 中的 a）
    sub_menus = li.find_elements(By.CSS_SELECTOR, "ul li a")

    for sub_a in sub_menus:
        second_name = sub_a.text.strip()
        print(f"正在处理: {first_name} -> {second_name}")

        # 点击子菜单
        driver.execute_script("arguments[0].click();", sub_a)
        time.sleep(0.5)

        # 切换到右侧 iframe 获取内容
        driver.switch_to.default_content()
        content_iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))  # 替换为右侧iframe选择器
        driver.switch_to.frame(content_iframe)

        content_div = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "doc_content")))
        content_html = content_div.get_attribute("innerHTML")

        # 保存文件
        save_path = os.path.join(SAVE_DIR, first_name, second_name)
        os.makedirs(save_path, exist_ok=True)
        file_path = os.path.join(save_path, "index.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content_html)
        print(f"已保存: {file_path}")

        # 回到左侧菜单 iframe
        driver.switch_to.default_content()
        driver.switch_to.frame(menu_iframe)

driver.quit()
