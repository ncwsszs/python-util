import os
import pypandoc

# ===== 配置 =====
src_dir = r"G:\OneDrive\文档\工作\瑞景中台\对接文档\对接文档\智慧生态园林对接"
dst_dir = r"G:\OneDrive\文档\工作\瑞景中台\对接文档\word\智慧生态园林对接"
reference_doc = r"G:\OneDrive\文档\工作\瑞景中台\一般文档模板.docx"  # 模板路径，可为空

# ===== 工具函数 =====
def convert_to_utf8(file_path):
    """将文件编码转换为 UTF-8（如果不是）"""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        # 先尝试 UTF-8
        content = content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            content = content.decode('gbk')
        except UnicodeDecodeError:
            content = content.decode('latin-1', errors='ignore')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

# ===== 主逻辑 =====
for root, _, files in os.walk(src_dir):
    for file in files:
        if file.lower().endswith(".md"):
            md_path = os.path.join(root, file)

            # 转换前统一编码
            try:
                convert_to_utf8(md_path)
            except Exception as e:
                print(f"⚠️ [编码失败] {md_path}, 错误: {e}")
                continue

            # 生成输出路径（保持目录结构）
            relative_path = os.path.relpath(md_path, src_dir)
            docx_path = os.path.join(dst_dir, os.path.splitext(relative_path)[0] + ".docx")
            os.makedirs(os.path.dirname(docx_path), exist_ok=True)

            # Pandoc 转换
            try:
                args = ['--standalone']
                if reference_doc and os.path.exists(reference_doc):
                    args.insert(0, f'--reference-doc={reference_doc}')

                pypandoc.convert_file(
                    md_path,
                    'docx',
                    outputfile=docx_path,
                    extra_args=args
                )
                print(f"✅ 成功: {md_path} -> {docx_path}")
            except Exception as e:
                print(f"❌ [转换失败] {md_path}, 错误: {e}")
