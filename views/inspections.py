import streamlit as st
import pandas as pd
from datetime import datetime
import time
from api import (
    get_inspections,
    get_inspection,
    create_inspection,
    update_inspection,
    delete_inspection,
    upload_inspection_pdf,
    generate_inspection_report
)
from convert import get_projects_df, get_inspections_df

st.subheader("🔍 抽查表清單")

# 篩選條件
projects_df = get_projects_df()
project_filter = st.sidebar.selectbox(
    "依專案篩選", 
    ["全部專案"] + projects_df["專案名稱"].tolist() if not projects_df.empty else ["全部專案"]
)

# 取得抽查列表
@st.cache_data()
def display_inspections(project_name=None):
    # 如果選擇特定專案，取得專案 ID
    project_id = None
    if project_name and project_name != "全部專案":
        project_id = int(projects_df[projects_df["專案名稱"] == project_name]["專案編號"].values[0])
    
    # 取得抽查資料
    df = get_inspections_df(project_id)
    
    if df.empty:
        st.info("目前沒有抽查資料")
        return
    
    # 合併專案名稱
    if not projects_df.empty:
        df = pd.merge(
            df, 
            projects_df[["專案編號", "專案名稱"]], 
            left_on="專案編號", 
            right_on="專案編號", 
            how="left"
        )
    
    # 顯示抽查資料表
    st.dataframe(
        df[["抽查編號", "專案名稱", "分項工程名稱", "抽查表名稱", "抽查次數", "檢查位置", "抽查時機", "抽查日期", "抽查結果"]].style.format({
            "抽查日期": lambda x: x
        }),
        use_container_width=True,
        hide_index=True
    )


@st.dialog("📝新增抽查")
def add_inspection_ui():
    if projects_df.empty:
        st.warning("請先建立專案")
        return
    
    st.subheader("新增抽查紀錄")
    with st.form("add_inspection_form", clear_on_submit=True):
        # 專案選擇
        project_options = [(str(p.專案編號), p.專案名稱) for p in get_projects_df().itertuples(index=False)]
        project_id = st.selectbox("所屬專案", options=[x[0] for x in project_options], format_func=lambda x: dict(project_options)[x])

        subproject_name = st.text_input("分項工程名稱")
        inspection_form_name = st.text_input("抽查表名稱")
        inspection_date = st.date_input("抽查日期")
        location = st.text_input("檢查位置")
        timing = st.selectbox("抽查時機", options=["檢驗停留點", "隨機抽查"])
        result = st.selectbox("抽查結果", options=["合格", "不合格"])
        remark = st.text_area("備註")

        submitted = st.form_submit_button("新增抽查")
        if submitted:
            if not all([project_id, subproject_name, inspection_form_name, inspection_date, location, timing, result]):
                st.warning("請填寫所有必填欄位")
            else:
                data = {
                    "project_id": int(project_id),
                    "subproject_name": subproject_name,
                    "inspection_form_name": inspection_form_name,
                    "inspection_date": inspection_date.strftime("%Y-%m-%d"),
                    "location": location,
                    "timing": timing,
                    "result": result,
                    "remark": remark
                }
                resp = create_inspection(data)
                if "error" not in resp:
                    st.toast("新增抽查成功", icon="✅")
                    st.cache_data.clear()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"新增抽查失敗: {resp['error']}")


# 編輯抽查對話框
@st.dialog("✏️編輯抽查")
def update_inspection_ui():
    # 取得抽查列表
    inspections_df = get_inspections_df()
    if inspections_df.empty:
        st.warning("目前沒有抽查可編輯")
        return
    
    # 合併專案名稱
    if not projects_df.empty:
        inspections_df = pd.merge(
            inspections_df, 
            projects_df[["專案編號", "專案名稱"]], 
            left_on="專案編號", 
            right_on="專案編號", 
            how="left"
        )
    
    # 選擇抽查
    inspection_options = [f"{row['抽查編號']} - {row['專案名稱']} - {row['檢查位置']}" for _, row in inspections_df.iterrows()]
    selected_inspection = st.selectbox("選擇抽查", inspection_options)
    
    if not selected_inspection:
        st.warning("請選擇要編輯的抽查")
        return
    
    # 取得抽查 ID
    inspection_id = int(selected_inspection.split(" - ")[0])
    
    # 取得抽查詳細資料
    inspection = get_inspection(inspection_id)
    if not inspection:
        st.error("無法取得抽查資料")
        return
    
    # 編輯表單
    with st.form("edit_inspection_form"):
        # 只能編輯結果和備註
        result = st.selectbox("抽查結果", ["合格", "不合格"], index=["合格", "不合格"].index(inspection.get("result", "合格") or "合格"))
        remark = st.text_area("備註", value=inspection.get("remark", ""))
        
        # 顯示其他不可編輯的欄位
        st.info(f"所屬專案: {projects_df[projects_df['專案編號'] == inspection['project_id']]['專案名稱'].values[0] if not projects_df.empty else ''}")
        st.info(f"分項工程名稱: {inspection.get('subproject_name', '')}")
        st.info(f"抽查表名稱: {inspection.get('inspection_form_name', '')}")
        st.info(f"檢查位置: {inspection.get('location', '')}")
        st.info(f"抽查時機: {inspection.get('timing', '')}")
        st.info(f"抽查日期: {inspection.get('inspection_date', '')}")
        
        # 上傳 PDF
        pdf_file = st.file_uploader("上傳報告 PDF", type=["pdf"])
        
        submitted = st.form_submit_button("更新")
        if submitted:
            data = {
                "result": result,
                "remark": remark
            }
            
            response = update_inspection(inspection_id, data)
            if "error" not in response:
                st.toast("抽查更新成功", icon="✅")
                
                # 如果有上傳 PDF
                if pdf_file:
                    pdf_response = upload_inspection_pdf(inspection_id, pdf_file)
                    if "error" not in pdf_response:
                        st.toast("PDF 上傳成功", icon="✅")
                    else:
                        st.error(f"PDF 上傳失敗: {pdf_response['error']}")
                
                st.cache_data.clear()
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"更新失敗: {response['error']}")


# 產生報告對話框
@st.dialog("📄產生報告")
def generate_report_ui():
    # 取得抽查列表
    inspections_df = get_inspections_df()
    if inspections_df.empty:
        st.warning("目前沒有抽查可產生報告")
        return
    
    # 合併專案名稱
    if not projects_df.empty:
        inspections_df = pd.merge(
            inspections_df, 
            projects_df[["專案編號", "專案名稱"]], 
            left_on="專案編號", 
            right_on="專案編號", 
            how="left"
        )
    
    # 選擇抽查
    inspection_options = [f"{row['抽查編號']} - {row['專案名稱']} - {row['檢查位置']}" for _, row in inspections_df.iterrows()]
    selected_inspection = st.selectbox("選擇抽查", inspection_options)
    
    if not selected_inspection:
        st.warning("請選擇要產生報告的抽查")
        return
    
    # 取得抽查 ID
    inspection_id = int(selected_inspection.split(" - ")[0])
    
    if st.button("產生報告"):
        with st.spinner("正在產生報告..."):
            response = generate_inspection_report(inspection_id)
            if "error" not in response:
                st.success("報告產生成功！")
                st.download_button(
                    label="下載報告",
                    data="報告內容將由後端提供".encode("utf-8"),  # 修正 bytes literal 中文問題
                    file_name=f"抽查報告_{inspection_id}.pdf",
                    mime="application/pdf"
                )
            else:
                st.error(f"報告產生失敗: {response['error']}")

# 刪除抽查對話框
@st.dialog("🗑️刪除抽查")
def delete_inspection_ui():
    # 取得抽查列表
    inspections_df = get_inspections_df()
    if inspections_df.empty:
        st.warning("目前沒有抽查可刪除")
        return
    
    # 合併專案名稱
    if not projects_df.empty:
        inspections_df = pd.merge(
            inspections_df, 
            projects_df[["專案編號", "專案名稱"]], 
            left_on="專案編號", 
            right_on="專案編號", 
            how="left"
        )
    
    # 選擇抽查
    inspection_options = [f"{row['抽查編號']} - {row['專案名稱']} - {row['檢查位置']}" for _, row in inspections_df.iterrows()]
    selected_inspection = st.selectbox("選擇抽查", inspection_options)
    
    if not selected_inspection:
        st.warning("請選擇要刪除的抽查")
        return
    
    # 取得抽查 ID
    inspection_id = int(selected_inspection.split(" - ")[0])
    
    # 確認刪除
    st.warning("⚠️ 刪除抽查將同時刪除所有相關照片，此操作無法復原！")
    
    if st.button("確認刪除"):
        response = delete_inspection(inspection_id)
        if "error" not in response:
            st.toast("抽查刪除成功", icon="✅")
            st.cache_data.clear()
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"刪除失敗: {response['error']}")


# 顯示抽查列表
display_inspections(project_filter if project_filter != "全部專案" else None)

# 按鈕列
col1, col2, col3= st.columns(3)

# with col3:
#     if st.button("📝新增抽查", use_container_width=True):
#         st.toast("請點選側邊攔新增抽查表", icon="ℹ️")
        # add_inspection_ui()

with col1:
    if st.button("✏️編輯抽查", use_container_width=True):
        update_inspection_ui()

# with col3:
#     if st.button("📄產生報告", use_container_width=True):
#         generate_report_ui()

with col2:
    if st.button("🗑️刪除抽查", use_container_width=True):
        delete_inspection_ui()

with col3:
    if st.button("📝列印報告", use_container_width=True):
        generate_report_ui()

# 新增抽查對話框