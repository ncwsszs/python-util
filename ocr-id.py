import cv2
import ddddocr
from PIL import Image
import pytesseract
import re
from PIL import Image

def main():
    # pytesseract.pytesseract.tesseract_cmd = r'G:\project\python\Tesseract-OCR\tesseract.exe'
    # # 打开验证码图像
    # image = Image.open('test2/captcha_1_20250519_104814.png')
    # # 使用 pytesseract 进行识别
    # result = pytesseract.image_to_string(image)
    # # 打印识别结果
    # print(result)

    # ocr = ddddocr.DdddOcr(det=False, ocr=False,
    #                       import_onnx_path="myproject_0.984375_139_13000_2022-02-26-15-34-13.onnx",
    #                       charsets_path="charsets.json")
    #
    # with open('888e28774f815b01e871d474e5c84ff2.jpg', 'rb') as f:
    #     image_bytes = f.read()
    #
    # res = ocr.classification(image_bytes)
    # print(res)

    # det = ddddocr.DdddOcr(det=True)
    #
    # with open("example/ocr-id/img.png", 'rb') as f:
    #     image = f.read()
    #
    # bboxes = det.detection(image)
    # print(bboxes)
    #
    # im = cv2.imread("example/ocr-id/img.png")
    #
    # for bbox in bboxes:
    #     x1, y1, x2, y2 = bbox
    #     im = cv2.rectangle(im, (x1, y1), (x2, y2), color=(0, 0, 255), thickness=2)
    #
    # cv2.imwrite("result.jpg", im)


    # ocr = ddddocr.DdddOcr()
    #
    # image = open("example/ocr-id/img.png", "rb").read()
    # ocr.set_ranges("0123456789+-x/=")
    # result = ocr.classification(image, probability=True)
    # s = ""
    # for i in result['probability']:
    #     s += result['charsets'][i.index(max(i))]
    #
    # print(s)



    # 加载图片
    # image = Image.open("example/ocr-id/img.png")
    #
    # # 使用 Tesseract 识别（注意 config 参数）
    # text = pytesseract.image_to_string(image, config='--psm 7')
    # print("识别内容:", text)
    #
    # # 匹配数学表达式
    # match = re.search(r'(\d+)\s*[\-+*/]\s*\d+', text)
    # if match:
    #     # 直接用 eval 计算（需先清理）
    #     expr = match.group(0).replace('=', '').strip()
    #     result = eval(expr)
    #     print("验证码答案:", result)
    # else:
    #     print("无法识别数学表达式")


if __name__ == '__main__':
    main()
