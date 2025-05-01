import streamlit as st
# from auth import check_ad_credentials, get_user_info_one, parse_dn, white_list
import time

VERSION="1.0.0"

st.set_page_config(page_title=f"施工抽查系統-V{VERSION}",layout="wide")

# 建築巡檢系統頁面
project_page = st.Page("views/projects.py", title="專案管理", icon=":material/domain:")
inspection_page = st.Page("views/inspections.py", title="抽查表清單", icon=":material/search:")
photo_page = st.Page("views/photos.py", title="照片圖廊", icon=":material/image:")
inspection_add_page = st.Page("views/inspections_add.py", title="新增抽查表", icon=":material/search:")

pg=st.navigation(
    {
        "基本設定": [project_page],
        "施工抽查": [inspection_add_page,inspection_page, photo_page]
    }
)

pg.run()