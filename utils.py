from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import os
from datetime import datetime

# with open("data.json", "r", encoding="utf-8") as f:
#     data = json.load(f)

def generate_pdf(data):
    """生成 PDF 報表，返回 PDF 的 bytes 以便用於 Streamlit 的 download_button"""
    # 註冊中文字型
    import io
    
    font_path = os.path.join(os.path.dirname(__file__), "fonts", "NotoSansTC-Regular.ttf")
    pdfmetrics.registerFont(TTFont('NotoSansTC', font_path))
    chinese_font = 'NotoSansTC'

    # 使用 BytesIO 而不是實體文件
    buffer = io.BytesIO()

    # 創建 PDF 文件
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1*cm, leftMargin=1*cm, topMargin=1*cm, bottomMargin=1*cm)

    # 獲取樣式並創建中文樣式
    styles = getSampleStyleSheet()

    # 如果找到中文字型，則創建中文樣式
    if chinese_font:
        # 標題樣式
        styles.add(ParagraphStyle(
            name='ChineseTitle',
            parent=styles['Title'],
            fontName=chinese_font,
            fontSize=20,
            alignment=1,  # 置中
            spaceAfter=12
        ))
        
        # 一般文字樣式
        styles.add(ParagraphStyle(
            name='ChineseNormal',
            parent=styles['Normal'],
            fontName=chinese_font,
            fontSize=12,
            leading=14,
            spaceAfter=6
        ))
        
        # 標題3樣式
        styles.add(ParagraphStyle(
            name='ChineseHeading3',
            parent=styles['Heading3'],
            fontName=chinese_font,
            fontSize=14,
            leading=16,
            spaceAfter=6
        ))

    # 使用中文樣式或備用樣式
    title_style = styles['ChineseTitle'] if chinese_font else styles['Title']
    normal_style = styles['ChineseNormal'] if chinese_font else styles['Normal']
    heading3_style = styles['ChineseHeading3'] if chinese_font else styles['Heading3']

    # 創建內容元素列表
    elements = []

    # 標題與基本資料
    elements.append(Paragraph(f"<b>抽查紀錄表照片</b>", title_style))

    # 定義表格的資料（合併所有照片內容）
    table_data = []
    for idx, photo in enumerate(data["photos"], 1):
        # 設定每行的高度
        row_heights = [1* cm, 1 * cm, 9* cm]  # 不同的行高
        
        # 表格資料放 metadata + 圖片
        table_data.append([Paragraph("拍攝日期", normal_style), Paragraph(photo["capture_date"], normal_style)])
        # table_data.append([Paragraph("位置", normal_style), Paragraph(photo["location"], normal_style)])
        table_data.append([Paragraph("說明", normal_style), Paragraph(photo["caption"], normal_style)])
        table_data.append([Paragraph("圖片", normal_style), Image(f"http://localhost:8000/{photo['photo_path']}", width=9 * cm, height=9 * cm, kind='proportional')])

    # 創建單一表格並設定樣式
    table = Table(table_data, colWidths=[3 * cm, 12 * cm], rowHeights=None)  # 讓行高根據內容自動調整
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),  # 設定邊框
        ("VALIGN", (0, 0), (-1, -1), "TOP"),  # 垂直對齊
        ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),  # 設定背景顏色
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # 水平對齊
    ]))

    elements.append(table)

    # 建立 PDF
    try:
        doc.build(elements)
        # 獲取 PDF 的 bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
    except Exception as e:
        print(f"生成 PDF 時發生錯誤: {e}")
        return None
