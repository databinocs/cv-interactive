import base64
from fpdf import FPDF

def strip_non_ascii(text):
    """
    Loại bỏ ký tự không thuộc bảng mã ASCII (tránh lỗi khi ghi PDF với fpdf)
    """
    return ''.join(c for c in text if ord(c) < 128)

def export_text_as_md(text, filename="report.md"):
    """
    Tạo link tải file Markdown
    """
    b64 = base64.b64encode(text.encode()).decode()
    return f'<a href="data:file/markdown;base64,{b64}" download="{filename}">📥 Download Markdown</a>'

def export_text_as_pdf(text, filename="report.pdf"):
    """
    Xuất nội dung thành PDF và tạo link tải
    """
    # Loại bỏ ký tự đặc biệt (emoji, unicode)
    text = strip_non_ascii(text)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_auto_page_break(auto=True, margin=15)

    for line in text.split("\n"):
        pdf.multi_cell(0, 10, line)

    pdf.output(filename)

    with open(filename, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">📥 Download PDF</a>'
