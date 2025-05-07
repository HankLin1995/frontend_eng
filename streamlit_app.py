import streamlit as st
# from auth import check_ad_credentials, get_user_info_one, parse_dn, white_list
import time

def login_info():
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📝 使用說明")
        st.markdown("""
        1. **登入 Google 帳號**  
        2. **建立專案**  
        3. **新增抽查表**  
            - 上傳 PDF  
            - 填寫基本資料  
            - 上傳多張照片  
        4. **查看清單並列印報告**
                """)

    with col2:
        st.markdown("### ⚠️ 注意事項")
        st.warning("""
        - 系統目前部署在個人主機  
        - 每個專案 **限制 100 MB**  
        - 請將照片**壓縮後再上傳**  
        - 如需部署在其他主機，歡迎聯繫我們！
                """)

        st.divider()

        st.markdown("### 📬 聯絡資訊")

        col3,col4 = st.columns(2)

        with col3:
            st.image("https://www.hanksvba.com/images/LINE_QRCODE.PNG", width=150, caption="LINE官方帳號")

        with col4:

            st.link_button("🌎 Hank's blog", "https://www.hanksvba.com/",type="secondary")

VERSION="2.0.0"

st.set_page_config(page_title=f"施工抽查系統-V{VERSION}",layout="wide")

st.logo("lOGO.JPG")

if not st.user.is_logged_in:
    login_info()
    if st.sidebar.button("Google 登入",type="primary"):
        st.login()
else:
    # if st.sidebar.button(f"{st.user.name}登出",type="secondary"):
    #     st.logout()
    # st.sidebar.markdown("---")

    # 建築巡檢系統頁面
    project_page = st.Page("views/projects.py", title="專案管理", icon=":material/domain:")
    inspection_page = st.Page("views/inspections.py", title="抽查表清單", icon=":material/list:")
    photo_page = st.Page("views/photos.py", title="照片圖廊", icon=":material/image:")
    inspection_add_page = st.Page("views/inspections_add.py", title="新增抽查表", icon=":material/create:")
    inspection_edit_page= st.Page("views/inspections_edit.py", title="編輯抽查表", icon=":material/edit_document:")

    pg=st.navigation(
        {
            "設定": [project_page],
            "異動": [inspection_add_page,inspection_edit_page],
            "總覽": [inspection_page,photo_page]
        }
    )

    pg.run()
    if st.sidebar.button(f"👋 {st.user.name}登出",type="secondary"):
        st.logout()