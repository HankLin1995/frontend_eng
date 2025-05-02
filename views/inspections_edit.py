import streamlit as st
import pypdfium2 as pdfium
import datetime

from api import get_projects, create_inspection, upload_inspection_pdf, upload_photo

if "photos" not in st.session_state:
    st.session_state.photos = []  # 用來儲存多張照片的列表
if "pdf_file" not in st.session_state:
    st.session_state.pdf_file = None  # 用來儲存上傳的 PDF 檔案

# PDF 初始化（不儲存檔案）
def initialize_pdf(uploaded_file):
    """直接使用上傳的檔案初始化 PDF 並返回頁數與圖像"""
    try:
        pdf = pdfium.PdfDocument(uploaded_file)
        total_pages = len(pdf)
        pdf_images = {i: pdf[i].render(scale=2).to_pil() for i in range(total_pages)}
        return total_pages, pdf_images
    except Exception as e:
        st.error(f"❌ PDF 初始化錯誤: {e}")
        return None, None

# 顯示 PDF 頁面
def display_pdf_page(total_pages, pdf_images):
    """顯示目前頁面"""
    if "current_page" not in st.session_state:
        st.session_state.current_page = 0

    current_page = st.session_state.current_page
    if 0 <= current_page < total_pages:
        image_to_show = pdf_images[current_page]
        st.image(image_to_show, caption=f"📄 頁數 {current_page + 1} / {total_pages}")

# 分頁控制
def pagination_controls(total_pages):
    """建立翻頁按鈕"""
    col0, col1, col2, col3 = st.columns([1, 1, 1, 1])
    with col1:
        if st.button("⬆️ 上一頁") and st.session_state.current_page > 0:
            st.session_state.current_page -= 1
    with col2:
        if st.button("⬇️ 下一頁") and st.session_state.current_page < total_pages - 1:
            st.session_state.current_page += 1

@st.dialog("📤 上傳抽查表")
def upload_pdf_ui():

    pdf_file = st.file_uploader("請選擇", type=["pdf", "jpg", "jpeg", "png"])

    if st.button("確認上傳"):
        st.session_state.pdf_file = pdf_file
        st.rerun()

@st.dialog("📤 上傳照片")
def upload_photos_ui():

    # capture_date = st.date_input("📅 照片日期")
    caption = st.text_input("照片說明", placeholder="例如：檢查結果、問題點等")
    # Define the accepted file types explicitly
    uploaded_file = st.file_uploader("請選擇", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption='Uploaded Image')

        # Append the uploaded file to the session state

        if st.button("確認上傳"):
            st.session_state.photos.append({
                "file": uploaded_file,
                # "date": capture_date,
                "caption": caption
            })
            st.success("照片上傳成功！")
            st.rerun()


# 主應用介面

st.subheader("⭐ 編輯抽查表")

col3, col4 = st.columns([1,1])

with col3.container(border=True):

    prjs=get_projects()
    get_project_list = [item["name"] for item in prjs]

    check_project = st.selectbox("🏗️ 專案名稱", options=get_project_list)
    check_date = st.date_input("📅 日期")
    check_location = st.text_input("🗺️ 地點")
    check_item = st.text_input("📝 抽查項目")
    check_type = st.pills("🕒 抽查時機", options=["檢驗停留點", "隨機抽查", "其他"])
    check_result = st.pills("✅ 抽查結果", options=["合格", "不合格"])
    check_note = st.text_area("🗒️ 備註", height=100)

with col4:

    # 先建立 tab 標題：第一個是 PDF，後面依據照片數量建立
    photo_tabs = [f"🖼️ 照片 {i+1}" for i in range(len(st.session_state.photos))]
    tab_titles = ["📑 PDF 預覽"] + photo_tabs

    # 建立 tabs
    tabs = st.tabs(tab_titles)

    # === PDF 預覽 Tab ===
    with tabs[0]:
        # with st.expander("📑 PDF 預覽", expanded=True):
        pdf_file = st.session_state.get("pdf_file", None)
        if pdf_file:
            total_pages, pdf_images = initialize_pdf(pdf_file)
            if total_pages and pdf_images:
                display_pdf_page(total_pages, pdf_images)
                pagination_controls(total_pages)
        else:
            st.info("尚未上傳 PDF。")

    # === 每張照片一個 Tab ===
    for i, photo in enumerate(st.session_state.photos):
        with tabs[i + 1]:  # tabs[1] 是第一張照片
            st.image(photo["file"], caption="圖片說明: "+photo["caption"])
            st.button("刪除照片", key=f"delete_photo_{i}", on_click=lambda i=i: st.session_state.photos.pop(i) if len(st.session_state.photos) > 1 else st.session_state.photos.clear())  # 刪除照片按鈕

st.markdown("---")

if st.button("4.儲存資料", type="primary"):
    pass