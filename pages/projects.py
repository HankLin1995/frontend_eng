import streamlit as st
import pandas as pd
import time
from datetime import datetime
from api import (
    get_projects,
    get_project,
    create_project,
    update_project,
    delete_project
)
from convert import get_projects_df

st.subheader("🏢 專案管理")

# 顯示專案列表
@st.cache_data()
def display_projects():
    df = get_projects_df()
    if df.empty:
        st.info("目前沒有專案資料")
        return
    
    # 顯示專案資料表
    st.dataframe(
        df[["專案編號", "專案名稱", "專案位置", "承包商", "開始日期", "結束日期"]].style.format({
            "開始日期": lambda x: x,
            "結束日期": lambda x: x
        }),
        use_container_width=True,
        hide_index=True
    )

# 新增專案對話框
@st.dialog("📝新增專案")
def add_project_ui():
    with st.form("create_project_form"):
        name = st.text_input("專案名稱", placeholder="請輸入專案名稱")
        location = st.text_input("專案位置", placeholder="請輸入專案位置")
        contractor = st.text_input("承包商", placeholder="請輸入承包商")
        start_date = st.date_input("開始日期", value=datetime.now())
        end_date = st.date_input("結束日期", value=datetime.now())
        
        submitted = st.form_submit_button("建立")
        if submitted:
            if not all([name, location, contractor]):
                st.error("請填寫所有必填欄位")
                return
            
            # 檢查結束日期是否大於等於開始日期
            if end_date < start_date:
                st.error("結束日期必須大於或等於開始日期")
                return
            
            data = {
                "name": name,
                "location": location,
                "contractor": contractor,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d")
            }
            
            response = create_project(data)
            if "error" not in response:
                st.toast("專案建立成功", icon="✅")
                st.cache_data.clear()
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"建立失敗: {response['error']}")

# 編輯專案對話框
@st.dialog("✏️編輯專案")
def update_project_ui():
    # 取得專案列表
    df = get_projects_df()
    if df.empty:
        st.warning("目前沒有專案可編輯")
        return
    
    # 選擇專案
    project_names = df["專案名稱"].tolist()
    selected_project = st.selectbox("選擇專案", project_names)
    
    if not selected_project:
        st.warning("請選擇要編輯的專案")
        return
    
    # 取得專案 ID
    project_id = df[df["專案名稱"] == selected_project]["專案編號"].values[0]
    
    # 取得專案詳細資料
    project = get_project(project_id)
    if not project:
        st.error("無法取得專案資料")
        return
    
    # 編輯表單
    with st.form("edit_project_form"):
        name = st.text_input("專案名稱", value=project["name"])
        location = st.text_input("專案位置", value=project["location"])
        contractor = st.text_input("承包商", value=project["contractor"])
        start_date = st.date_input("開始日期", value=datetime.strptime(project["start_date"], "%Y-%m-%d"))
        end_date = st.date_input("結束日期", value=datetime.strptime(project["end_date"], "%Y-%m-%d"))
        
        submitted = st.form_submit_button("更新")
        if submitted:
            if not all([name, location, contractor]):
                st.error("請填寫所有必填欄位")
                return
            
            # 檢查結束日期是否大於等於開始日期
            if end_date < start_date:
                st.error("結束日期必須大於或等於開始日期")
                return
            
            data = {
                "name": name,
                "location": location,
                "contractor": contractor,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d")
            }
            
            response = update_project(project_id, data)
            if "error" not in response:
                st.toast("專案更新成功", icon="✅")
                st.cache_data.clear()
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"更新失敗: {response['error']}")

# 刪除專案對話框
@st.dialog("🗑️刪除專案")
def delete_project_ui():
    # 取得專案列表
    df = get_projects_df()
    if df.empty:
        st.warning("目前沒有專案可刪除")
        return
    
    # 選擇專案
    project_names = df["專案名稱"].tolist()
    selected_project = st.selectbox("選擇專案", project_names)
    
    if not selected_project:
        st.warning("請選擇要刪除的專案")
        return
    
    # 取得專案 ID
    project_id = df[df["專案名稱"] == selected_project]["專案編號"].values[0]
    
    # 確認刪除
    st.warning("⚠️ 刪除專案將同時刪除所有相關抽查與照片，此操作無法復原！")
    
    if st.button("確認刪除"):
        response = delete_project(project_id)
        if "error" not in response:
            st.toast("專案刪除成功", icon="✅")
            st.cache_data.clear()
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"刪除失敗: {response['error']}")


# 顯示專案列表
display_projects()

# 按鈕列
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📝新增專案", use_container_width=True):
        add_project_ui()

with col2:
    if st.button("✏️編輯專案", use_container_width=True):
        update_project_ui()

with col3:
    if st.button("🗑️刪除專案", use_container_width=True):
        delete_project_ui()

