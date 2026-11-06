import streamlit as st

st.title("このサイトについて")

st.write("なにか書く")

st.write("確認されているバグ")

if st.button("戻る", key="about_back"):
    st.switch_page(st.session_state.pages["sheet_list"])
