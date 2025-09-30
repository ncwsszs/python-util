import os
import pathlib
import html2text


def html_to_md_file(html_path, md_path):
    """将 HTML 文件转换为 Markdown 文件"""
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 用 html2text 转换
    h = html2text.HTML2Text()
    h.ignore_links = False  # 保留链接
    md_content = h.handle(html_content)

    # 写入 markdown
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)


def traverse_and_convert(root_dir, output_dir):
    """遍历 root_dir 下所有 HTML 文件并转换为 MD 存储在 output_dir"""
    root_path = pathlib.Path(root_dir)
    output_path = pathlib.Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for html_file in root_path.rglob("*.html"):
        relative_path = html_file.relative_to(root_path)  # 相对路径
        md_file_path = output_path / relative_path.with_suffix(".md")  # 改为 .md
        md_file_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"正在转换: {html_file} -> {md_file_path}")
        html_to_md_file(html_file, md_file_path)


if __name__ == "__main__":
    source_dir = "saved_docs"  # 这里换成你的HTML目录
    target_dir = "markdown"  # 输出的Markdown目录
    traverse_and_convert(source_dir, target_dir)
