import streamlit as st
import json
import time
import hashlib

from functions import get_connection

@st.dialog("パスワード入力")
def pass_input(id, password):
    with st.form("input_edit_pass"):
        textbox = st.empty()
        input_password = textbox.text_input("パスワードを入力してください", type="password", key="input_password_text")
        with st.container(horizontal_alignment="right"):
            if st.form_submit_button("完了", key="password_ok"):
                hash_input_password = hashlib.sha256(input_password.encode('utf-8')).hexdigest()
                if hash_input_password == password:
                    st.session_state.edit_id = id
                    st.session_state.edit_mode = True
                    st.session_state.file_upload_flag = True
                    st.switch_page(st.session_state.pages["sheet"])
                else:
                    textbox.error("パスワードが違います。  \nもう一度入力してください。")
                    st.write(hash_input_password)
                    st.write(password)

@st.dialog("削除確認")
def data_delete(id, password):
    with st.form("data_delete_check"):
        textbox = st.empty()
        textbox.warning("データを削除します。  \nパスワードを入力してください。")
        input_password = st.text_input("パスワードを入力してください", type="password", label_visibility="collapsed", key="input_delete_password_text")
        with st.container(horizontal=True, horizontal_alignment="right"):
            if st.form_submit_button("削除", type="primary", key="func_delete_button"):
                hash_input_password = hashlib.sha256(input_password.encode('utf-8')).hexdigest()
                if hash_input_password == password:
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute("DELETE FROM sheet_data WHERE id = ?", (id,))
                    conn.commit()
                    conn.close()
                    textbox.success("削除しました。")
                    time.sleep(3)
                    st.rerun()
                else:
                    textbox.error("パスワードが違います。  \nもう一度入力してください。")
                    st.write(hash_input_password)
                    st.write(password)

            elif st.form_submit_button("キャンセル", key="func_cancel_button"):
                st.rerun()

st.title("シート一覧")

with st.container(gap="xxsmall"):
    col_list_pc, col_list_pl, col_list_lv, col_list_date, col_list_create = st.columns([2,1,1,1,1])
    with col_list_pc:
        st.write("PC名")
    with col_list_pl:
        st.write("PL名")
    with col_list_lv:
        st.write("レベル")
    with col_list_date:
        st.write("更新日時")
    with col_list_create:
        with st.container(horizontal_alignment="right"):
            if st.button("新規作成", type="primary"):
                st.session_state.edit_mode = False
                st.switch_page(st.session_state.pages["sheet"])
    st.divider()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM sheet_data")
    raw_data = c.fetchall()
    conn.close()
    for id, pc, pl, lv, date, password, binary_data in raw_data:
        if id == 0:
            continue
        col_list_pc, col_list_pl, col_list_lv, col_list_date, col_list_delete = st.columns([2,1,1,1,1])
        with col_list_pc:
            #st.write(f"#### {pc}")
            if st.button(f"{pc}", key=f"pc_name_{id}", type="tertiary"):
                st.session_state.input_password_text = ""
                pass_input(id, password)
        with col_list_pl:
            st.write(f"{pl}")
        with col_list_lv:
            st.write(f"{lv}")
        with col_list_date:
            st.write(f"{date}")
        # with col_list_edit:
        #     if st.button("編集", key=f"edit_{id}"):
        #         st.session_state.input_password_text = ""
        #         pass_input(id, password)
        with col_list_delete:
            with st.container(horizontal_alignment="center"):
                if st.button("削除", type="tertiary", key=f"delete_{id}"):
                    data_delete(id, password)


with st.expander("デバッグ用DB生データ", expanded=False):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM sheet_data")
    raw_data = c.fetchall()
    conn.close()

    df = []
    for id, pc, pl, lv, date, password, binary_data in raw_data:
        json_obj = json.loads(binary_data.decode("utf-8"))
        df.append({"id": id, "PC名": pc, "PL名": pl, "Lv":lv, "更新日時": date, "pass": password, "data": json_obj})

    st.write(df)
