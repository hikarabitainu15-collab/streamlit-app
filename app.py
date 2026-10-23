import streamlit as st
import streamlit.components.v1 as components

# # lang属性を日本語に変更するスクリプト
# 画面上部に謎のスペースができてしまう
# components.html("""
#     <script>
#         window.top.document.documentElement.lang = "ja";
#     </script>
# """)

if 'page_layout' not in st.session_state:
    st.session_state.page_layout = "centered"

with st.container(horizontal=True, horizontal_alignment="right"):
    if st.session_state.page_layout == "centered":
        if st.button("ページをワイドにする", help="ウィンドウ幅によってはレイアウトが崩れる可能性があります", type="tertiary"):
            st.session_state.page_layout = "wide"
            st.rerun()
    elif st.session_state.page_layout == "wide":
        if st.button("ページを中央揃えにする", help="標準のレイアウトです", type="tertiary"):
            st.session_state.page_layout = "centered"
            st.rerun()

#ページ設定
st.set_page_config(
    page_title="sw2.5 charasheet app",
    page_icon="⚔",
    layout=st.session_state.page_layout,
    initial_sidebar_state="auto",
    menu_items={
        #'Get Help': 'https://www.extremelycoolapp.com/help',
        #'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "## SNEくんが情けないために生まれた素晴らしいサイト"
    }
)

sheet_list_page = st.Page(
    "pages/sheet_list.py",
    title="シート一覧",
    default=True
)

sheet_page = st.Page(
    "pages/sheet.py",
    title="シート編集",
)

about_page = st.Page(
    "pages/about.py",
    title="このアプリについて"
)

pg = st.navigation(
    [
        sheet_list_page,
        sheet_page,
        about_page
    ],
    position="hidden"
)

st.session_state.pages = {
    "sheet_list": sheet_list_page,
    "sheet": sheet_page,
    "about": about_page
}

pg.run()