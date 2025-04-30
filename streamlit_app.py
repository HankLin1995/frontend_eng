import streamlit as st
# from auth import check_ad_credentials, get_user_info_one, parse_dn, white_list
import time

VERSION="1.0.0"

st.set_page_config(page_title=f"施工抽查系統-V{VERSION}",layout="wide")

# 建築巡檢系統頁面
project_page = st.Page("views/projects.py", title="專案管理", icon=":material/domain:")
inspection_page = st.Page("views/inspections.py", title="抽查管理", icon=":material/search:")
photo_page = st.Page("views/photos.py", title="照片管理", icon=":material/image:")

pg=st.navigation(
    {
        "施工抽查": [project_page, inspection_page, photo_page]
    }
)

pg.run()