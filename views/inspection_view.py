import streamlit as st
import pypdfium2 as pdfium
import datetime
import pandas as pd

from api import get_projects, get_inspection, get_photos, upload_photo

# PDF 初始化（不儲存檔案）
def initialize_pdf(pdf_path):
    """初始化 PDF 並返回頁數與圖像"""
    try:
        # 這裡假設 pdf_path 是從 API 返回的相對路徑
        full_path = f"http://localhost:8000/{pdf_path}"
        pdf = pdfium.PdfDocument(full_path)
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


# 從URL參數獲取抽查ID
query_params = st.query_params
inspection_id = query_params.get("id", None)

if not inspection_id:
    st.warning("請提供抽查ID")
    # 顯示抽查列表供選擇
    from convert import get_inspections_df
    inspections_df = get_inspections_df()
    if not inspections_df.empty:
        st.sidebar.subheader("請選擇抽查表")
        for _, row in inspections_df.iterrows():
            if st.sidebar.button(f"{row['抽查表名稱']} - 第{row['抽查次數']}次 - {row['檢查位置']} ({row['抽查日期']})", key=f"inspection_{row['抽查編號']}"):
                st.query_params["id"] = row['抽查編號']
                st.rerun()

# 獲取抽查詳細資訊
inspection = get_inspection(inspection_id)
if not inspection:
    st.error("無法獲取抽查資料")

# 獲取專案資訊
projects = get_projects()
project_name = "未知專案"
for project in projects:
    if project["id"] == inspection["project_id"]:
        project_name = project["name"]
        break

# 顯示抽查基本資訊
col1, col2 = st.columns([1, 1])

with col1.container(border=True):
    st.markdown("### 抽查基本資訊")
    st.markdown(f"**🏗️ 專案名稱:** {project_name}")
    st.markdown(f"**📝 抽查項目:** {inspection['inspection_form_name']}")
    st.markdown(f"**📅 日期:** {inspection['inspection_date']}")
    st.markdown(f"**🗺️ 地點:** {inspection['location']}")
    st.markdown(f"**🕒 抽查時機:** {inspection['timing']}")
    st.markdown(f"**✅ 抽查結果:** {inspection['result'] or '未設定'}")
    
    if inspection.get("remark"):
        st.markdown(f"**🗒️ 備註:**")
        st.markdown(f"{inspection['remark']}")

with col2:
    # 顯示PDF（如果有）
    if inspection.get("pdf_path"):
        st.markdown("### 📑 抽查表")
        # 在實際應用中，這裡應該顯示PDF的內容
        st.markdown(f"[查看PDF文件](http://localhost:8000/{inspection['pdf_path']})")
        # 如果能夠直接顯示PDF，可以使用以下代碼
        # total_pages, pdf_images = initialize_pdf(inspection['pdf_path'])
        # if total_pages and pdf_images:
        #     display_pdf_page(total_pages, pdf_images)
        #     pagination_controls(total_pages)
    else:
        st.info("此抽查表沒有上傳PDF文件")

# 顯示照片
st.markdown("### 📸 相關照片")

# 獲取照片資料
photos = inspection.get("photos", [])
if not photos:
    st.info("此抽查表沒有相關照片")

else:
        
    # 顯示照片
    cols = st.columns(3)
    for i, photo in enumerate(photos):
        with cols[i % 3]:
            # 顯示抽查編號在最上方
            st.caption(f"抽查編號: {inspection_id}")
            # 顯示照片
            st.image(f"http://localhost:8000/{photo['photo_path']}")
            # 顯示檢查位置
            st.caption(f"檢查位置: {inspection['location']}")
            # 顯示照片說明
            if photo.get("caption"):
                st.caption(f"照片說明: {photo['caption']}")
            # 顯示上傳時間
            st.caption(f"上傳時間: {photo['capture_date']}")
