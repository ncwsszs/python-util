import cv2
import pytesseract
import re

# === 1. 读取图像 ===
image = cv2.imread("example/ocr-id/img.png")

# === 2. 灰度处理 ===
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# === 3. 二值化处理（适应干扰）===
thresh = cv2.adaptiveThreshold(gray, 255,
                               cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY_INV, 11, 3)

# === 4. 可选：膨胀操作加强字体结构（防止 OCR 识别断裂）===
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
dilate = cv2.dilate(thresh, kernel, iterations=1)

# 保存调试图像（你可以查看这一步效果）
cv2.imwrite("processed.png", dilate)

# === 5. OCR 识别（指定允许的字符集）===
custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789+-*/='
text = pytesseract.image_to_string(dilate, config=custom_config)

# === 6. 打印识别结果并提取计算 ===
print("识别内容:", text.strip())

match = re.search(r'(\d+)\s*([\+\-\*/])\s*(\d+)', text)
if match:
    num1, op, num2 = match.groups()
    try:
        result = eval(f"{num1}{op}{num2}")
        print(f"验证码表达式: {num1} {op} {num2} = {result}")
    except Exception as e:
        print("表达式无法计算:", e)
else:
    print("未能正确识别数学表达式")
