"""
extract_pdf.py - 从 PDF 文件提取文本并保存
用法: python extract_pdf.py <pdf_path> <output_txt_path> [max_pages]
"""
import sys
import pdfplumber
import os

def extract(pdf_path, output_path, max_pages=None):
    if not os.path.exists(pdf_path):
        print(f"ERROR: 文件不存在: {pdf_path}")
        sys.exit(1)

    text = ''
    page_count = 0
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        pages_to_read = min(total, max_pages) if max_pages else total
        print(f"总页数: {total}，读取: {pages_to_read}")
        for i, page in enumerate(pdf.pages[:pages_to_read]):
            t = page.extract_text() or ''
            text += f"\n--- Page {i+1} ---\n" + t

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"提取完成，字符数: {len(text)}，保存至: {output_path}")
    return text

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python extract_pdf.py <pdf_path> <output_txt_path> [max_pages]")
        sys.exit(1)
    max_p = int(sys.argv[3]) if len(sys.argv) > 3 else None
    extract(sys.argv[1], sys.argv[2], max_p)
