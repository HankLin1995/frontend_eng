import requests
from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

# 註冊中文字型（放一份 TTF 檔於 fonts 資料夾中）
pdfmetrics.registerFont(TTFont('NotoSansTC', 'fonts/NotoSansTC-Regular.ttf'))

def generate_inspection_pdf(data, output_path):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    margin = 1.5 * cm
    current_y = height - margin
    
    # 設定字型為 NotoSansTC，並提高字型大小為 16
    c.setFont("NotoSansTC", 16)
    c.drawCentredString(width / 2, current_y, f"{data.get('project_id', '0000')}工程")
    current_y -= 1 * cm
    
    company_name = data.get('company_name', '無公司名稱')
    c.setFont("NotoSansTC", 14)  # 增加字型大小
    c.drawCentredString(width / 2, current_y, f"工程名稱: {company_name}")
    current_y -= 1.5 * cm
    
    # 設定表格寬度和行高
    table_width = width - 2 * margin
    row_height = 1.5 * cm  # 增加表格的行高
    photo_width = 5 * cm  # 設定圖片的寬度
    photo_height = 5 * cm  # 設定圖片的高度
    
    # 表格資料生成
    for i in range(3):
        inspection_data = data.get('inspections', [])[i] if i < len(data.get('inspections', [])) else {
            'date': f'<<日期-{i+1}>>',
            'location': f'<<位置-{i+1}>>',
            'description': f'<<說明-{i+1}>>',
            'photo_path': None
        }
        
        # 表格內容：左邊顯示文字，右邊顯示圖片
        left_cell = [
            ['日期:', f"{inspection_data.get('date', '')}"],
            ['位置:', f"{inspection_data.get('location', '')}"],  # 顯示位置
            ['說明:', f"{inspection_data.get('description', '')}"]
        ]
        
        # 修正：設定內嵌表格的行高
        left_cell_row_heights = [row_height, row_height, row_height]
        
        table_data = [
            [
                Table(left_cell, colWidths=[2 * cm, table_width - 3 * cm], rowHeights=left_cell_row_heights),
                f"<<附件-{i+1}>>"  # 預設文字，後續會顯示圖片
            ]
        ]
        
        # 修正：設定外部表格的行高
        main_table = Table(table_data, colWidths=[table_width / 2, photo_width], rowHeights=[row_height] * 1)
        main_table.setStyle(TableStyle([  
            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # 設定網格邊框
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # 垂直對齊
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # 左對齊
            ('FONTNAME', (0, 0), (-1, -1), 'NotoSansTC'),  # 設定字型
            ('FONTSIZE', (0, 0), (-1, -1), 12),  # 設定字型大小
            ('TOPPADDING', (0, 0), (-1, -1), 6),  # 表格的上下內邊距
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),  # 表格的上下內邊距
            ('LEFTPADDING', (0, 0), (-1, -1), 8),  # 表格的左右內邊距
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),  # 表格的左右內邊距
        ]))
        
        # 繪製表格
        main_table.wrapOn(c, width, height)
        main_table.drawOn(c, margin, current_y - 3 * row_height)
        
        # 處理圖片顯示
        photo_path = inspection_data.get('photo_path')
        if photo_path:
            try:
                photo_url = f"http://localhost:8000/{photo_path}"
                resp = requests.get(photo_url)
                if resp.status_code == 200:
                    image = Image.open(BytesIO(resp.content)).convert("RGB")
                    image.thumbnail((photo_width, photo_height))
                    compressed_io = BytesIO()
                    image.save(compressed_io, format='JPEG', quality=60)
                    compressed_io.seek(0)
                    
                    img = Image.open(compressed_io)
                    aspect = img.width / img.height
                    
                    max_img_width = photo_width
                    max_img_height = photo_height
                    
                    if aspect > 1:
                        img_width = min(max_img_width, max_img_height * aspect)
                        img_height = img_width / aspect
                    else:
                        img_height = min(max_img_height, max_img_width / aspect)
                        img_width = img_height * aspect
                    
                    x = margin + table_width / 2 - img_width / 2
                    y = current_y - 3 * row_height + (row_height - img_height) / 2
                    c.drawImage(ImageReader(compressed_io), x, y, width=img_width, height=img_height)
                else:
                    c.setFont("NotoSansTC", 10)
                    c.drawString(margin + table_width / 2 + 0.5 * cm, current_y - 3 * row_height + 0.5 * cm, "圖片下載錯誤")
            except Exception as e:
                c.setFont("NotoSansTC", 10)
                c.drawString(margin + table_width / 2 + 0.5 * cm, current_y - 3 * row_height + 0.5 * cm, f"圖片錯誤：{e}")
        
        current_y -= 4 * row_height  # 每個檢查項目結束後，移動到下一行
    
    c.save()

# === 示範用 JSON 資料 ===
sample_data = {
    "project_id": "0000",
    "company_name": "南科高階製造中心公司(第一期)機電工程",
    "inspections": [
        {
            "date": "2023-05-01",
            "location": "1AAAAA",
            "description": "混凝土澆置檢查",
            "photo_path": "app/static/uploads/photos/8ecc65f8-1b3a-4e41-801f-26626bcae41c_LINE_ALBUM_202337_230807_1.jpg"
        },
        {
            "date": "2023-05-02",
            "location": "2FFFFSD",
            "description": "鋼筋綁紮檢查",
            "photo_path": "app/static/uploads/photos/fe460ded-e12b-46d0-98fb-70097b0ab250_S__8871976.jpg"
        },
        {
            "date": "2023-05-03",
            "location": "3FFFFFF",
            "description": "管線配置檢查",
            "photo_path": "app/static/uploads/photos/bb9311fc-e036-4ea5-912e-cdf61d807bde_S__55828535.jpg"
        }
    ]
}

# === 產出 PDF ===
generate_inspection_pdf(sample_data, "output_inspection_improved.pdf")
