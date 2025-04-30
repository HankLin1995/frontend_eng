import streamlit as st
# from auth import check_ad_credentials, get_user_info_one, parse_dn, white_list
import time

VERSION="1.4.3"

st.set_page_config(page_title=f"建築巡檢系統-V{VERSION}",layout="wide")

# 建築巡檢系統頁面
project_page = st.Page("pages/projects.py", title="專案管理", icon=":material/domain:")
inspection_page = st.Page("pages/inspections.py", title="巡檢管理", icon=":material/search:")
photo_page = st.Page("pages/photos.py", title="照片管理", icon=":material/image:")

pg=st.navigation(
    {
        "建築巡檢系統": [project_page, inspection_page, photo_page]
    }
)

pg.run()