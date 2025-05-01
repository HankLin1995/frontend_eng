import streamlit as st
import pandas as pd
import time
from api import (
    get_photos,
    get_photo,
    upload_photo,
    update_photo,
    delete_photo
)
from convert import get_inspections_df, get_photos_df

st.subheader("📸 照片管理")

# 篩選條件
inspections_df = get_inspections_df()
inspection_filter = st.sidebar.selectbox(
    "依抽查篩選", 
    ["全部抽查"] + [f"{row['抽查編號']} - {row['檢查位置']}" for _, row in inspections_df.iterrows()] if not inspections_df.empty else ["全部抽查"]
)

# 取得照片列表
@st.cache_data(ttl=60)
def display_photos(inspection_id=None):
    # 取得照片資料
    df = get_photos_df(inspection_id)
    
    if df.empty:
        st.info("目前沒有照片資料")
        return
    
    # 合併抽查資訊
    if not inspections_df.empty:
        df = pd.merge(
            df, 
            inspections_df[["抽查編號", "檢查位置"]], 
            left_on="抽查編號", 
            right_on="抽查編號", 
            how="left"
        )
    
    # 顯示照片資料表
    st.dataframe(
        df[["照片編號", "檢查位置", "描述", "上傳時間"]],
        use_container_width=True,
        hide_index=True
    )
    
    # 顯示照片預覽
    if not df.empty:
        st.subheader("照片預覽")
        cols = st.columns(3)
        for i, (_, row) in enumerate(df.iterrows()):
            with cols[i % 3]:
                # 實際應用中，這裡應該顯示照片的縮圖
                st.image(f"http://localhost:8000/{row['檔案路徑']}", caption=f"{row['描述']}")
                st.caption(f"檢查位置: {row['檢查位置']}")
                st.caption(f"上傳時間: {row['上傳時間']}")

# 上傳照片對話框
@st.dialog("📤上傳照片")
def upload_photo_ui():
    if inspections_df.empty:
        st.warning("請先建立抽查")
        return
    
    with st.form("upload_photo_form"):
        
        inspection_options = [f"{row['抽查編號']} - {row['檢查位置']}" for _, row in inspections_df.iterrows()]
        selected_inspection = st.selectbox("選擇抽查", inspection_options)
        capture_date = st.date_input("拍照日期")
        caption = st.text_input("照片描述", placeholder="請輸入照片描述")
        photo_file = st.file_uploader("選擇照片", type=["jpg", "jpeg", "png"])
        

        # if photo_file:
        #     st.image(photo_file)
        
        submitted = st.form_submit_button("上傳")
        if submitted:
            if not all([selected_inspection, photo_file]):
                st.error("請選擇抽查並上傳照片")
                return
            
            # 取得抽查 ID
            inspection_id = int(selected_inspection.split(" - ")[0])
            
            response = upload_photo(inspection_id, photo_file,capture_date.strftime("%Y-%m-%d"), caption)
            if "error" not in response:
                st.toast("照片上傳成功", icon="✅")
                st.cache_data.clear()
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"上傳失敗: {response['error']}")

# 編輯照片對話框
@st.dialog("✏️編輯照片")
def update_photo_ui():
    # 取得照片列表
    photos_df = get_photos_df()
    if photos_df.empty:
        st.warning("目前沒有照片可編輯")
        return
    
    # 合併抽查資訊
    if not inspections_df.empty:
        photos_df = pd.merge(
            photos_df, 
            inspections_df[["抽查編號", "檢查位置"]], 
            left_on="抽查編號", 
            right_on="抽查編號", 
            how="left"
        )
    
    # 選擇照片
    photo_options = [f"{row['照片編號']} - {row['檢查位置']} - {row['描述']}" for _, row in photos_df.iterrows()]
    selected_photo = st.selectbox("選擇照片", photo_options)
    
    if not selected_photo:
        st.warning("請選擇要編輯的照片")
        return
    
    # 取得照片 ID
    photo_id = int(selected_photo.split(" - ")[0])
    
    # 取得照片詳細資料
    photo = get_photo(photo_id)
    if not photo:
        st.error("無法取得照片資料")
        return
    
    # 編輯表單
    with st.form("edit_photo_form"):
        # 顯示照片預覽
        st.image(f"http://localhost:8000/{photo['photo_path']}")
        
        caption = st.text_input("照片描述", value=photo.get("caption", ""))
        
        submitted = st.form_submit_button("更新")
        if submitted:
            data = {
                "caption": caption,
            }
            
            response = update_photo(photo_id, data)
            if "error" not in response:
                st.toast("照片更新成功", icon="✅")
                st.cache_data.clear()
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"更新失敗: {response['error']}")

# 刪除照片對話框
@st.dialog("🗑️刪除照片")
def delete_photo_ui():
    # 取得照片列表
    photos_df = get_photos_df()
    if photos_df.empty:
        st.warning("目前沒有照片可刪除")
        return
    
    # 合併抽查資訊
    if not inspections_df.empty:
        photos_df = pd.merge(
            photos_df, 
            inspections_df[["抽查編號", "檢查位置"]], 
            left_on="抽查編號", 
            right_on="抽查編號", 
            how="left"
        )
    
    # 選擇照片
    photo_options = [f"{row['照片編號']} - {row['檢查位置']} - {row['描述']}" for _, row in photos_df.iterrows()]
    selected_photo = st.selectbox("選擇照片", photo_options)
    
    if not selected_photo:
        st.warning("請選擇要刪除的照片")
        return
    
    # 取得照片 ID
    photo_id = int(selected_photo.split(" - ")[0])
    
    # 確認刪除
    st.warning("⚠️ 刪除照片後無法復原！")
    
    if st.button("確認刪除"):
        response = delete_photo(photo_id)
        if "error" not in response:
            st.toast("照片刪除成功", icon="✅")
            st.cache_data.clear()
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"刪除失敗: {response['error']}")


# 顯示照片列表
if inspection_filter != "全部抽查":
    inspection_id = int(inspection_filter.split(" - ")[0])
    display_photos(inspection_id)
else:
    display_photos()

# 按鈕列
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📤上傳照片", use_container_width=True):
        upload_photo_ui()

with col2:
    if st.button("✏️編輯照片", use_container_width=True):
        update_photo_ui()

with col3:
    if st.button("🗑️刪除照片", use_container_width=True):
        delete_photo_ui()