import copy
import re
import streamlit as st
import numpy as np
import pandas as pd
import json

# セッション初期設定
if 'page_layout' not in st.session_state:
    st.session_state.page_layout = "centered"
if 'file_upload_flag' not in st.session_state:
    st.session_state.file_upload_flag = False
if 'race_mode' not in st.session_state:
    st.session_state.race_mode = "normal"
if 'born_mode' not in st.session_state:
    st.session_state.born_mode = "normal"
if 'lv_list' not in st.session_state:
    st.session_state.lv_list = [0]
if 'skill_count' not in st.session_state:
    st.session_state.skill_count = 1
if 'growth_list' not in st.session_state:
    st.session_state.growth_list = [0] * 6
if 'life_stats_list' not in st.session_state:
    st.session_state.life_stats_list = [
        [0,0,0,0],
        [0,0,0,0],
        [0,0,0,0],
        [0,0,0,0]
    ]
if 'hp_buf' not in st.session_state:
    st.session_state.vital_buf = [0] * 4
    st.session_state.mental_buf = [0] * 4
    st.session_state.hp_buf = [0] * 4
    st.session_state.mp_buf = [0] * 4
    st.session_state.accuracy_buf = [0] * 2
    st.session_state.avoidance_buf = [0] * 2
if 'use_exp' not in st.session_state:
    st.session_state.exp_all = 0
    st.session_state.use_exp = 0
if 'first_skill' not in st.session_state:
    st.session_state.first_skill = []
if 'ability_mode' not in st.session_state:
    st.session_state.ability_mode = []
    for i in range(18):
        st.session_state.ability_mode.append(" ")
if 'weapon_list_num' not in st.session_state:
    st.session_state.weapon_list_num = 1
if 'equipment_part_list' not in st.session_state:
    st.session_state.equipment_part_list = ["頭", "顔", "耳", "首", "背中", "右手", "左手", "腰", "足", "他"]
    st.session_state.equipment_list_num = 10
    st.session_state.equipment_buf = [0] * 15
if 'item_list_num' not in st.session_state:
    st.session_state.item_list_num = 5
    st.session_state.money = 0
if 'language_list_num' not in st.session_state:
    st.session_state.language_list_num = 3
if 'honor_list_num' not in st.session_state:
    st.session_state.honor_list_num = 3
if 'history_list_num' not in st.session_state:
    st.session_state.history_list_num = 3
    st.session_state.exp = 0
    st.session_state.pinzoro = 0
    st.session_state.honor = 0

#関数
def on_upload_file():
    st.session_state.file_upload_flag = True
def update_born():
    born_name = st.session_state.born_selectbox
    if ((born_name != " ") and (born_name != "自由記入")):
        st.session_state[f"stats_技"] = borns[born_list.index(born_name)-1]["stats"][0]
        st.session_state[f"stats_体"] = borns[born_list.index(born_name)-1]["stats"][1]
        st.session_state[f"stats_心"] = borns[born_list.index(born_name)-1]["stats"][2]
        if 'or' not in borns[born_list.index(born_name)-1]["skills"]:
            for name in borns[born_list.index(born_name)-1]["skills"]:
                st.session_state[f"skill_lv_{skills_name_list.index(name)}"] = 1
    elif 'load_data' in locals():
        st.session_state[f"stats_技"] = load_data["stats_list"][0][0]
        st.session_state[f"stats_体"] = load_data["stats_list"][2][0]
        st.session_state[f"stats_心"] = load_data["stats_list"][4][0]
    else:
        st.session_state[f"stats_技"] = st.session_state[f"stats_体"] = st.session_state[f"stats_心"] = 0
def update_lv():
    count = []
    for i in range(st.session_state.skill_count):
        key = f"skill_lv_{i}"
        if key in st.session_state:
            count.append(st.session_state[key])
    st.session_state.lv_list = count
    st.session_state.use_exp = 0
    for i in range(len(skill_data["skill"])):
        st.session_state.use_exp += exp_table_data["exp_table"][skill_data["skill"][i]["exp_table"]][st.session_state.lv_list[i]]
def update_life_stats_list():
    st.session_state.life_stats_list[0][1] = sum(st.session_state.vital_buf)
    st.session_state.life_stats_list[1][1] = sum(st.session_state.mental_buf)
    st.session_state.life_stats_list[2][1] = sum(st.session_state.hp_buf)
    st.session_state.life_stats_list[3][1] = sum(st.session_state.mp_buf)
def update_ability_buf():
    if "頑強" in st.session_state.ability_mode:
        st.session_state.hp_buf[1] = 15
        update_life_stats_list()
    elif "頑強" not in st.session_state.ability_mode:
        st.session_state.hp_buf[1] = 0
        update_life_stats_list()
    if "超頑強" in st.session_state.ability_mode:
        st.session_state.hp_buf[2] = 15
        update_life_stats_list()
    elif "超頑強" not in st.session_state.ability_mode:
        st.session_state.hp_buf[2] = 0
        update_life_stats_list()
    if "キャパシティ" in st.session_state.ability_mode:
        st.session_state.mp_buf[1] = 15
        update_life_stats_list()
    elif "キャパシティ" not in st.session_state.ability_mode:
        st.session_state.mp_buf[1] = 0
        update_life_stats_list()
    if "抵抗強化I" in st.session_state.ability_mode:
        st.session_state.vital_buf[1] = 1
        st.session_state.mental_buf[1] = 1
        update_life_stats_list()
    elif "抵抗強化II" in st.session_state.ability_mode:
        st.session_state.vital_buf[1] = 2
        st.session_state.mental_buf[1] = 2
        update_life_stats_list()
    elif (("抵抗強化I" not in st.session_state.ability_mode) and ("抵抗強化II" not in st.session_state.ability_mode)):
        st.session_state.vital_buf[1] = 0
        st.session_state.mental_buf[1] = 0
        update_life_stats_list()
    if "命中強化I" in st.session_state.ability_mode:
        st.session_state.accuracy_buf[0] = 1
    elif "命中強化II" in st.session_state.ability_mode:
        st.session_state.accuracy_buf[0] = 2
    elif (("命中強化I" not in st.session_state.ability_mode) and ("命中強化II" in st.session_state.ability_mode)):
        st.session_state.accuracy_buf[0] = 0
    if "回避行動I" in st.session_state.ability_mode:
        st.session_state.avoidance_buf[0] = 1
    elif "回避行動II" in st.session_state.ability_mode:
        st.session_state.avoidance_buf[0] = 2
    elif (("回避行動I" not in st.session_state.ability_mode) and ("回避行動II" not in st.session_state.ability_mode)):
        st.session_state.avoidance_buf[0] = 0
def update_ability_mode(abi_num):
    st.session_state.ability_mode[abi_num] = st.session_state[f"ability_selectbox_{abi_num}"]
    update_ability_buf()    
def update_weapon_list_num(num):
    st.session_state.weapon_list_num = max(st.session_state.weapon_list_num + num, 1)
def update_equipment_buf():
    equipment_buf_list = []
    st.session_state.equipment_buf = [0] * 15
    for part in st.session_state.equipment_part_list:
        i = 0
        while(f"equipment_{part}_{i}_4" in st.session_state):
            if st.session_state[f"equipment_{part}_{i}_4"] != "":
                equipment_buf_list.append(st.session_state[f"equipment_{part}_{i}_4"])
            i += 1
    for data in equipment_buf_list:
        flag_str = data[-1]
        match flag_str:
            case "A":
                try:
                    buf_num = int(data.rstrip("A"))
                    st.session_state.equipment_buf[0] += buf_num
                except:
                    st.empty()
            case "B":
                try:
                    buf_num = int(data.rstrip("B"))
                    st.session_state.equipment_buf[1] += buf_num
                except:
                    st.empty()
            case "C":
                try:
                    buf_num = int(data.rstrip("C"))
                    st.session_state.equipment_buf[2] += buf_num
                except:
                    st.empty()
            case "D":
                try:
                    buf_num = int(data.rstrip("D"))
                    st.session_state.equipment_buf[3] += buf_num
                except:
                    st.empty()
            case "E":
                try:
                    buf_num = int(data.rstrip("E"))
                    st.session_state.equipment_buf[4] += buf_num
                except:
                    st.empty()
            case "F":
                try:
                    buf_num = int(data.rstrip("F"))
                    st.session_state.equipment_buf[5] += buf_num
                except:
                    st.empty()
            case "G":
                try:
                    buf_num = int(data.rstrip("G"))
                    st.session_state.equipment_buf[6] += buf_num
                except:
                    st.empty()
            case "H":
                try:
                    buf_num = int(data.rstrip("H"))
                    st.session_state.equipment_buf[7] += buf_num
                except:
                    st.empty()
            case "I":
                try:
                    buf_num = int(data.rstrip("I"))
                    st.session_state.equipment_buf[8] += buf_num
                except:
                    st.empty()
            case "J":
                try:
                    buf_num = int(data.rstrip("J"))
                    st.session_state.equipment_buf[9] += buf_num
                except:
                    st.empty()
            case "K":
                try:
                    buf_num = int(data.rstrip("K"))
                    st.session_state.equipment_buf[10] += buf_num
                except:
                    st.empty()
            case "L":
                try:
                    buf_num = int(data.rstrip("L"))
                    st.session_state.equipment_buf[11] += buf_num
                except:
                    st.empty()
            case "M":
                try:
                    buf_num = int(data.rstrip("M"))
                    st.session_state.equipment_buf[12] += buf_num
                except:
                    st.empty()
            case "N":
                try:
                    buf_num = int(data.rstrip("N"))
                    st.session_state.equipment_buf[13] += buf_num
                except:
                    st.empty()
            case "O":
                try:
                    buf_num = int(data.rstrip("O"))
                    st.session_state.equipment_buf[14] += buf_num
                except:
                    st.empty()
def update_equipment_exclusive_buf():
    equipment_buf_list = []
    for part in st.session_state.equipment_part_list:
        i = 0
        while(f"{part}{i}専用" in st.session_state):
            equipment_buf_list.append(st.session_state[f"{part}{i}専用"])
            i += 1
    if(("HP" in equipment_buf_list) and (st.session_state.hp_buf[0] != 2)):
        st.session_state.hp_buf[0] = 2
        update_life_stats_list()
    elif(("HP" not in equipment_buf_list) and (st.session_state.hp_buf[0] != 0)):
        st.session_state.hp_buf[0] = 0
        update_life_stats_list()
    if(("MP" in equipment_buf_list) and (st.session_state.mp_buf[0] != 2)):
        st.session_state.mp_buf[0] = 2
        update_life_stats_list()
    elif(("MP" not in equipment_buf_list) and (st.session_state.mp_buf[0] != 0)):
        st.session_state.mp_buf[0] = 0
        update_life_stats_list()
def update_item_list_num(num):
    st.session_state.item_list_num = max(st.session_state.item_list_num + num, 1)
def update_language_list_num(num):
    st.session_state.language_list_num = max(st.session_state.language_list_num + num, 0)
def update_honor_list_num(num):
    st.session_state.honor_list_num = max(st.session_state.honor_list_num + num, 3)
def update_history_list_num(num):
    st.session_state.history_list_num = max(st.session_state.history_list_num + num, 1)
    if num == -1:
        update_history()
def update_history():
    st.session_state.exp = 0
    st.session_state.exp_all = 0
    st.session_state.pinzoro = 0
    st.session_state.money = 0
    st.session_state.honor = 0
    st.session_state.growth_list = [0] * 6
    for i in range(st.session_state.history_list_num):
        key_exp = f"history_{i}_1"
        key_pinzoro = f"history_{i}_2"
        key_money = f"history_{i}_3"
        key_honor = f"history_{i}_4"
        key_growth = f"history_{i}_5"
        key_fool = f"history_{i}_7"
        st.session_state.exp += st.session_state[key_exp] if key_exp in st.session_state else 0
        st.session_state.exp_all += (st.session_state[key_pinzoro]*10 if st.session_state[key_fool] else st.session_state[key_pinzoro]*50) + (st.session_state[key_exp] if key_exp in st.session_state else 0)
        st.session_state.pinzoro += st.session_state[key_pinzoro] if key_pinzoro in st.session_state else 0
        st.session_state.money += st.session_state[key_money] if key_money in st.session_state else 0
        st.session_state.honor += st.session_state[key_honor] if key_honor in st.session_state else 0
        if st.session_state[key_growth] != "":
            try:
                st.session_state.growth_list[0] += int(re.search(r'器\d+', st.session_state[key_growth]).group().lstrip("器")) if "器" in st.session_state[key_growth] else 0
                st.session_state.growth_list[1] += int(re.search(r'敏\d+', st.session_state[key_growth]).group().lstrip("敏")) if "敏" in st.session_state[key_growth] else 0
                st.session_state.growth_list[2] += int(re.search(r'筋\d+', st.session_state[key_growth]).group().lstrip("筋")) if "筋" in st.session_state[key_growth] else 0
                st.session_state.growth_list[3] += int(re.search(r'生\d+', st.session_state[key_growth]).group().lstrip("生")) if "生" in st.session_state[key_growth] else 0
                st.session_state.growth_list[4] += int(re.search(r'知\d+', st.session_state[key_growth]).group().lstrip("知")) if "知" in st.session_state[key_growth] else 0
                st.session_state.growth_list[5] += int(re.search(r'精\d+', st.session_state[key_growth]).group().lstrip("精")) if "精" in st.session_state[key_growth] else 0
            except:
                st.error("成長欄の入力規則が間違っています")

#外部データ読み込み
# 種族情報ファイルを読み込む
@st.cache_data
def load_race_json():
    with open("race.json", "r", encoding="utf-8") as f:
        return json.load(f)
race_data = load_race_json()
races = race_data["race"]
race_list = [" "] + [race["name"] for race in races] + ["自由記入"]

# 技能情報ファイルを読み込む
@st.cache_data
def load_skills_json():
    with open("skills.json", "r", encoding="utf-8") as f:
        return json.load(f)
skill_data = load_skills_json()
#各技能のレベル格納配列を追加
for i in range(len(skill_data["skill"])):
    skill_data["skill"][i]["lv"] = 0
skills_name_list = [item["name"] for item in skill_data["skill"]]
warrior_name_list = [item["name"] for item in skill_data["skill"] if item["type"]==0]
magic_name_list = [item["name"] for item in skill_data["skill"] if item["type"]==1]
other_name_list = [item["name"] for item in skill_data["skill"] if item["type"]==2]
other2_name_list = [item["name"] for item in skill_data["skill"] if item["type"]==3]
st.session_state.skill_count = len(skills_name_list)

# 経験値テーブル情報ファイルを読み込む
@st.cache_data
def load_exp_table_json():
    with open("exp_table.json", "r", encoding="utf-8") as f:
        return json.load(f)
exp_table_data = load_exp_table_json()

# 戦闘特技情報ファイルを読み込む
@st.cache_data
def load_ability_json():
    with open("ability.json", "r", encoding="utf-8") as f:
        return json.load(f)
ability_data = load_ability_json()
ability_passive_list = [item for item in ability_data["passive"]]
ability_active_list = [item for item in ability_data["active"]]
ability_main_active_list = [item for item in ability_data["main_active"]]
ability_all_list = ability_passive_list + ability_active_list + ability_main_active_list
ability_all_name_list = [item["name"] for item in ability_all_list]

#言語情報ファイルを読み込む
@st.cache_data
def load_language_json():
    with open("language.json", "r", encoding="utf-8") as f:
        return json.load(f)
language_data = load_language_json()
language_name_list = [" "] + [item["name"] for item in language_data["language"]] + ["地方語", "自由記入"]

#技能リスト情報ファイルを読み込む
@st.cache_data
def load_skills_list_json(skill):
    with open("skills_list.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return data[skill]
hiou_list = load_skills_list_json("秘奥")
rengi_list = load_skills_list_json("練技")
juka_list = load_skills_list_json("呪歌")
kigei_list = load_skills_list_json("騎芸")
hujutu_list = load_skills_list_json("賦術")
souiki_list = load_skills_list_json("相域")
kohou_list = load_skills_list_json("鼓咆・陣率")
souki_list = load_skills_list_json("操気")
masou_list = load_skills_list_json("魔装")
sendou_list = load_skills_list_json("占瞳")
juin_list = load_skills_list_json("呪印")
kikaku_list = load_skills_list_json("貴格")

#神情報ファイルを読み込む
@st.cache_data
def load_gods_json():
    with open("gods.json", "r", encoding="utf-8") as f:
        return json.load(f)
gods_data = load_gods_json()

#アップロードされたデータを読み込む
@st.cache_data
def load_uploaded_json(json_file):
    return json.load(json_file)

#横幅設定
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

#アップロードデータを読み込んでページに反映する
uploaded_file = st.sidebar.file_uploader("json読み込み", type="json", accept_multiple_files=False, on_change=on_upload_file)
if uploaded_file is not None:
    load_data = load_uploaded_json(uploaded_file)
    if st.session_state.file_upload_flag:
        st.session_state.pc_name = load_data["pc_name"]
        st.session_state.pl_name = load_data["pl_name"]
        st.session_state.age = load_data["age"]
        st.session_state.gender = load_data["gender"]
        st.session_state.race_selectbox = load_data["race"][0]
        st.session_state.born_selectbox = load_data["born"][0]
        first_stats_list = copy.deepcopy(load_data["born"][2])
        st.session_state[f"stats_技"] = load_data["stats_list"][0][0]
        st.session_state[f"stats_体"] = load_data["stats_list"][2][0]
        st.session_state[f"stats_心"] = load_data["stats_list"][4][0]
        for i in range(6):
            for j in range(6):
                st.session_state[f"stats_{i}_{j}"] = load_data["stats_list"][i][j]
        for i in range(4):
            st.session_state[f"stats_buf_{i}"] = load_data["stats_buf"][i]
        for name in [names for names in load_data["lv_list"]]:
            st.session_state[f"skill_lv_{skills_name_list.index(name)}"] = load_data["lv_list"][name]
        update_lv()
        st.session_state.faith = load_data["faith"]
        st.session_state.ability_mode = load_data["ability"]
        update_ability_buf()
        st.session_state.weapon_list_num = len(load_data["weapon_list"])
        for i in range(len(load_data["weapon_list"])):
            for j in range(12):
                st.session_state[f"weapon_{i}_{j}"] = load_data["weapon_list"][i][j]
        for i in range(3):
            for j in range(7):
                st.session_state[f"armor_{i}_{j}"] = load_data["armor_list"][i][j]
        st.session_state.armor_0_3 = load_data["armor_list"][0][3]
        st.session_state.armor_1_3 = load_data["armor_list"][1][3]
        for part in st.session_state.equipment_part_list:
            for i in range(len(load_data["equipment_list"][part])):
                for j in range(6):
                    st.session_state[f"equipment_{part}_{i}_{j}"] = load_data["equipment_list"][part][i][j]
        update_equipment_buf()
        st.session_state.item_list_num = len(load_data["item_list"])
        for i in range(len(load_data["item_list"])):
            for j in range(5):
                st.session_state[f"item_{i}_{j}"] = load_data["item_list"][i][j]
        st.session_state.move_power_buf = load_data["other_stats_list"][0]
        st.session_state.gunti_check = load_data["other_stats_list"][1]
        st.session_state.mamotiki_skill = load_data["other_stats_list"][2]
        st.session_state.mamotiki_buf = load_data["other_stats_list"][3]
        st.session_state.sensei_skill = load_data["other_stats_list"][4]
        st.session_state.sensei_buf = load_data["other_stats_list"][5]
        language_num = 0
        if load_data["language_list"] == 2:
            for i in range(len(load_data["language_list"][language_num])):
                st.session_state[f"first_language_selectbox_{i}"] = load_data["language_list"][language_num][i][0]
                st.session_state[f"first_language_free_{i}"] = load_data["language_list"][language_num][i][1]
                st.session_state[f"first_language_exist_talk_{i}"] = load_data["language_list"][language_num][i][2]
                st.session_state[f"first_language_exist_read_{i}"] = load_data["language_list"][language_num][i][3]
            language_num = 1
        st.session_state.language_list_num = len(load_data["language_list"][language_num])
        for i in range(len(load_data["language_list"][language_num])):
            st.session_state[f"language_selectbox_{i}"] = load_data["language_list"][language_num][i][0]
            st.session_state[f"language_free_{i}"] = load_data["language_list"][language_num][i][1]
            st.session_state[f"language_exist_talk_{i}"] = load_data["language_list"][language_num][i][2]
            st.session_state[f"language_exist_read_{i}"] = load_data["language_list"][language_num][i][3]
        if '全魔法' in load_data["maryoku_list"]:
            for name in load_data["maryoku_list"]:
                if name == '全魔法':
                    for i in range(3):
                        st.session_state[f"all_maryoku_{i}"] = load_data["maryoku_list"]["全魔法"][i]
                elif name == 'フェアリーテイマー契約':
                    for i in range(6):
                        st.session_state[f"fairy_contract_{i}"] = load_data["maryoku_list"]["フェアリーテイマー契約"][i]
                elif name == 'ビブリオマンサー魔法':
                    for i in range(2):
                        for j in range(len(load_data["maryoku_list"]["ビブリオマンサー魔法"][i])):
                            st.session_state[f"hiou_magic_{i}_{j}"] = load_data["maryoku_list"]["ビブリオマンサー魔法"][i][j]
                else:
                    for i in range(5):
                        st.session_state[f"maryoku_{name}_{i}"] = load_data["maryoku_list"][name][i]
        for skill in load_data["other_skill_list"]:
            for i in range(len(load_data["other_skill_list"][skill])):
                st.session_state[f"{skill}_{i}"] = load_data["other_skill_list"][skill][i]
        for i in range(3):
            st.session_state[f"honor_rank_{i}"] = load_data["honor_list"][0][i]
        for i in range(len(load_data["honor_list"][1])):
            for j in range(3):
                st.session_state[f"honor_{i}_{j}"] = load_data["honor_list"][1][i][j]
        st.session_state.history_list_num = len(load_data["history"])
        for i in range(len(load_data["history"])):
            for j in range(8):
                st.session_state[f"history_{i}_{j}"] = load_data["history"][i][j]
        update_history()
        st.session_state.memo_area = load_data["memo"]

        st.session_state.file_upload_flag = False

#能力値配列
stats_name_list = [
    ["A","B","C","D","E","F"],
    ["器用度","敏捷度","筋力","生命力","知力","精神力"]
]
#冒険者レベル
main_lv = max(st.session_state.lv_list)
#魔法使い系技能レベル合計/最大値/2番目の値
magic_lv_sum = 0
magic_lv_max = 0
magic_lv_second_max = 0
magic_lv_list = [0]
# if len(st.session_state.lv_list) >= len(magic_name_list):
#     for i in range(len(skills_name_list)):
#         if skill_data["skill"][i]["name"] in magic_name_list:
#             magic_lv_sum += (st.session_state.lv_list[i])
#             magic_lv_max = max(magic_lv_max, st.session_state.lv_list[i])
if len(st.session_state.lv_list) >= len(magic_name_list):
    magic_lv_list = [st.session_state.lv_list[skills_name_list.index(data["name"])] for data in skill_data["skill"] if data["name"] in magic_name_list]
    magic_lv_sum = sum(magic_lv_list)
    magic_lv_max = max(magic_lv_list)
    magic_lv_second_max = sorted(magic_lv_list, reverse=True)[1]

#その他系技能格納用辞書
other_skill_dict = {}

st.title("sw2.5 キャラシ作成")

#キャラクター情報
with st.expander("キャラクター情報"):
    #PC名、PL名
    col1_name_pc, col2_name_pl = st.columns([3,1])
    with col1_name_pc:
        name_pc = st.text_input("キャラクター名", key="pc_name")
    with col2_name_pl:
        name_pl = st.text_input("プレイヤー名", key="pl_name")

    #種族、年齢、性別
    col1_race, col2_age, col3_gender = st.columns([3,1,1])
    with col1_race:
        # race_container = st.container()
        # with race_container:
        if st.session_state.race_mode == "normal":
            #通常モード
            race__ = st.selectbox("種族", options=race_list, key="race_selectbox")
            if race__ == "自由記入":
                st.session_state.race_mode = "custom"
                st.session_state.born_selectbox = " "
                update_born()
                st.rerun()
            race = race__
        else:
            #自由記入モード
            col1_race_input, col2_race_free = st.columns([1,2])
            with col1_race_input:
                race__ = st.selectbox("種族", options=race_list, key="race_selectbox")
                if race__ != "自由記入":
                    st.session_state.race_mode = "normal"
                    st.rerun()
            with col2_race_free:
                race = st.text_input("", value=load_data["race"][1] if uploaded_file is not None else "", placeholder="ここに入力")
    with col2_age:
        age = st.text_input("年齢", key="age")
    with col3_gender:
        gender = st.text_input("性別", key="gender")

    #種族特徴、生まれ
    col1_feature, col2_born = st.columns([2,1])
    if race__ == " ":
        born_dice = [[1,1,1,1,1,1],[18,18,18,18,18,18]]
        with col1_feature:
            feature = st.text_input("種族特徴", value="", disabled=True)
        with col2_born:
            born__ = " "
            born = st.text_input("生まれ", disabled=True)
    elif race__ == "自由記入":
        born_dice = [[1,1,1,1,1,1],[18,18,18,18,18,18]]
        with col1_feature:
            feature = st.text_input("種族特徴", value=load_data["race"][2] if uploaded_file is not None else "[]")
        with col2_born:
            born__ = "自由記入"
            born = st.text_input("生まれ", value=load_data["born"][1] if uploaded_file is not None else "")
    else:
        feature = race_data["race"][(race_list.index(race)-1)]["feature"]
        borns = race_data["race"][(race_list.index(race)-1)]["born"]
        born_list = [" "] + [born["job"] for born in borns] + ["自由記入"]
        born_dice = [
            race_data["race"][(race_list.index(race)-1)]["born_dice"]["born_dice_min"],
            race_data["race"][(race_list.index(race)-1)]["born_dice"]["born_dice_max"]
        ]
        with col1_feature:
            st.text_input("種族特徴", value=feature)
        with col2_born:
            # born_container = st.container()
            # with born_container:
            if st.session_state.born_mode == "normal":
                #通常モード
                born__ = st.selectbox("生まれ", born_list, key="born_selectbox", on_change=update_born)
                if born__ == "自由記入":
                    st.session_state.born_mode = "custom"
                    st.rerun()
                born = born__
            else:
                #自由記入モード
                col1_born_input, col2_born_free = st.columns([1,1])
                with col1_born_input:
                    born__ = st.selectbox("生まれ",born_list, key="born_selectbox", on_change=update_born)
                    if born__ != "自由記入":
                        st.session_state.born_mode = "normal"
                        st.rerun()
                with col2_born_free:
                    born = st.text_input("", placeholder="ここに入力", value=load_data["born"][1] if uploaded_file is not None else "")

    #生まれによる初期能力値、初期技能
    if 'first_stats_list' in locals():
        st.empty()
    elif born__ == " ":
        first_stats_list = [0,0,0]
        st.session_state.first_skill = [""]
    elif born__ == "自由記入":
        first_stats_list = [0,0,0]
        st.session_state.first_skill = ["なし"]
    else:
        first_stats_list = borns[born_list.index(born__)-1]["stats"]
        st.session_state.first_skill = borns[born_list.index(born__)-1]["skills"]
    if 'stats_list' not in locals():
        stats_list = [
            [0,born_dice[0][0],0,0,0,0,0],
            [0,born_dice[0][1],0,0,0,0,0],
            [0,born_dice[0][2],0,0,0,0,0],
            [0,born_dice[0][3],0,0,0,0,0],
            [0,born_dice[0][4],0,0,0,0,0],
            [0,born_dice[0][5],0,0,0,0,0],
        ]

#能力値タブ
with st.expander("能力値"):
    col1_stats, col2_stats = st.columns([1,6])
    with col1_stats:
        st.markdown("")
        st.markdown("")
        st.markdown("")
        stats_list[0][0] = st.number_input("技", value=first_stats_list[0], step=1, key=f"stats_技")
        stats_list[1][0] = stats_list[0][0]
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        stats_list[2][0] = st.number_input("体", value=first_stats_list[1], step=1, key=f"stats_体")
        stats_list[3][0] = stats_list[2][0]
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        stats_list[4][0] = st.number_input("心", value=first_stats_list[2], step=1, key=f"stats_心")
        stats_list[5][0] = stats_list[4][0]
    with col2_stats:
        for i in range(6):
            col_stats_1, col_stats_2, col_stats_3, col_stats_4, col_stats_5, col_stats_6, col_stats_7, col_stats_8, col_stats_9, col_stats_10, col_stats_11, col_stats_12 = st.columns([1,4,1,4,1,4,1,4,1,4,1,5])
            with col_stats_1:
                st.write("")
                st.write("")
                st.write(r"\+")
            with col_stats_2:
                stats_list[i][1] = st.number_input(stats_name_list[0][i], step=1, min_value=born_dice[0][0], max_value=born_dice[1][0], key=f"stats_{i}_1")
            with col_stats_3:
                st.write("")
                st.write("")
                st.write(r"\+")
            with col_stats_4:
                stats_list[i][2] = st.number_input(f"成長{stats_name_list[0][i]}", value=st.session_state.growth_list[i], disabled=True)
            with col_stats_5:
                st.write("")
                st.write("")
                st.write(r"\=")
            with col_stats_6:
                stats_list[i][3] = st.number_input(stats_name_list[1][i], value=(stats_list[i][0]+stats_list[i][1]+stats_list[i][2]), disabled=True)
            with col_stats_7:
                st.write("")
                st.write("")
                st.write(r"\+")
            with col_stats_8:
                stats_list[i][4] = st.number_input(f"補正{stats_name_list[0][i]}", step=1, key=f"stats_{i}_4")
            with col_stats_9:
                st.write("")
                st.write("")
                st.write(r"\+")
            with col_stats_10:
                stats_list[i][5] = st.number_input(f"補正{stats_name_list[0][i]}", value=st.session_state.equipment_buf[i], step=1, label_visibility="hidden", disabled=True)
            with col_stats_11:
                st.write("")
                st.write("")
                st.write(r"\=")
            with col_stats_12:
                stats_list[i][6] = st.number_input(f"{stats_name_list[1][i]}B", value=int((stats_list[i][3]+stats_list[i][4]+stats_list[i][5])/6), disabled=True)
    st.divider()
    
    col1_vital_mental, col_vmhp_sub, col2_hp_mp= st.columns([20,1,20])
    #生命抵抗力、精神抵抗力
    with col1_vital_mental:
        st.write("生命抵抗力")
        col1_vital_1, col1_vital_2, col1_vital_3, col1_vital_4, col1_vital_5, col1_vital_6, col1_vital_7 = st.columns([5,1,5,1,5,1,5])
        with col1_vital_1:
            st.session_state.life_stats_list[0][0] = st.number_input("冒険者レベル+生命力B", value=(main_lv+stats_list[3][5]), disabled=True, label_visibility="collapsed")
        with col1_vital_2:
            st.write("")
            st.write(r"\+")
        with col1_vital_3:
            st.number_input("生命抵抗補正_1", value=(st.session_state.life_stats_list[0][1]+st.session_state.equipment_buf[6]), disabled=True ,label_visibility="collapsed")
        with col1_vital_4:
            st.write("")
            st.write(r"\+")
        with col1_vital_5:
            st.session_state.life_stats_list[0][2] = st.number_input("生命抵抗補正_2", value=0, step=1, label_visibility="collapsed", key="stats_buf_0")
        with col1_vital_6:
            st.write("")
            st.write(r"\=")
        with col1_vital_7:
            st.session_state.life_stats_list[0][3] = st.number_input("生命抵抗力", value=(st.session_state.life_stats_list[0][0]+st.session_state.life_stats_list[0][1]+st.session_state.life_stats_list[0][2]+st.session_state.equipment_buf[6]), disabled=True, label_visibility="collapsed")
        st.write("精神抵抗力")
        col1_mental_1, col1_mental_2, col1_mental_3, col1_mental_4, col1_mental_5, col1_mental_6, col1_mental_7 = st.columns([5,1,5,1,5,1,5])
        with col1_mental_1:
            st.session_state.life_stats_list[1][0] = st.number_input("冒険者レベル+精神力B", value=(main_lv+stats_list[5][5]), disabled=True, label_visibility="collapsed")
        with col1_mental_2:
            st.write("")
            st.write(r"\+")
        with col1_mental_3:
            st.number_input("精神抵抗補正_1", value=(st.session_state.life_stats_list[1][1]+st.session_state.equipment_buf[7]), disabled=True, label_visibility="collapsed")
        with col1_mental_4:
            st.write("")
            st.write(r"\+")
        with col1_mental_5:
            st.session_state.life_stats_list[1][2] = st.number_input("精神抵抗補正_2", value=0, step=1, label_visibility="collapsed", key="stats_buf_1")
        with col1_mental_6:
            st.write("")
            st.write(r"\=")
        with col1_mental_7:
            st.session_state.life_stats_list[1][3] = st.number_input("精神抵抗力", value=(st.session_state.life_stats_list[1][0]+st.session_state.life_stats_list[1][1]+st.session_state.life_stats_list[1][2]+st.session_state.equipment_buf[7]), disabled=True, label_visibility="collapsed")
    #HP、MP
    with col2_hp_mp:
        st.write("HP")
        col2_hp_1, col2_hp_2, col2_hp_3, col2_hp_4, col2_hp_5, col2_hp_6, col2_hp_7 = st.columns([5,1,5,1,5,1,5])
        with col2_hp_1:
            st.session_state.life_stats_list[2][0] = st.number_input("冒険者レベル*3+生命力", value=(main_lv*3+stats_list[3][3]+stats_list[3][4]+stats_list[3][5]), disabled=True, label_visibility="collapsed")
        with col2_hp_2:
            st.write("")
            st.write(r"\+")
        with col2_hp_3:
            st.number_input("HP補正_1", value=(st.session_state.life_stats_list[2][1]+st.session_state.equipment_buf[8]), disabled=True, label_visibility="collapsed")
        with col2_hp_4:
            st.write("")
            st.write(r"\+")
        with col2_hp_5:
            st.session_state.life_stats_list[2][2] = st.number_input("HP補正_2", value=0, step=1, label_visibility="collapsed", key="stats_buf_2")
        with col2_hp_6:
            st.write("")
            st.write(r"\=")
        with col2_hp_7:
            st.number_input("HP", value=(st.session_state.life_stats_list[2][0]+st.session_state.life_stats_list[2][1]+st.session_state.life_stats_list[2][2]+st.session_state.equipment_buf[8]), disabled=True, label_visibility="collapsed")###################
        st.write("MP")
        col2_mp_1, col2_mp_2, col2_mp_3, col2_mp_4, col2_mp_5, col2_mp_6, col2_mp_7 = st.columns([5,1,5,1,5,1,5])
        with col2_mp_1:
            st.session_state.life_stats_list[3][0] = st.number_input("魔法使い系技能レベル*3+精神力", value=(magic_lv_sum*3+stats_list[5][3]+stats_list[5][4]+stats_list[5][5]), disabled=True, label_visibility="collapsed")
        with col2_mp_2:
            st.write("")
            st.write(r"\+")
        with col2_mp_3:
            st.number_input("MP補正_1", value=(st.session_state.life_stats_list[3][1]+st.session_state.equipment_buf[9]), disabled=True, label_visibility="collapsed")
        with col2_mp_4:
            st.write("")
            st.write(r"\+")
        with col2_mp_5:
            st.session_state.life_stats_list[3][2] = st.number_input("MP補正_2", value=0, step=1, label_visibility="collapsed", key="stats_buf_3")
        with col2_mp_6:
            st.write("")
            st.write(r"\=")
        with col2_mp_7:
            st.number_input("MP", value=(st.session_state.life_stats_list[3][0]+st.session_state.life_stats_list[3][1]+st.session_state.life_stats_list[3][2]+st.session_state.equipment_buf[9]), disabled=True, label_visibility="collapsed")

#技能タブ
with st.expander("技能"):
    col1_exp, col2_lv_magilv = st.columns([1,2])
    with col1_exp:
        st.write("経験点")
        st.table({"残り":(st.session_state.exp_all - st.session_state.use_exp), "累計":st.session_state.exp_all})
    with col2_lv_magilv:
        col2_1_lv, col2_2_magilv = st.columns([1,1])
        with col2_1_lv:
            st.write("冒険者レベル")
            st.text_input("冒険者レベル", value=main_lv, disabled=True, label_visibility="collapsed")
        with col2_2_magilv:
            st.write("魔法使い系技能レベル")
            st.text_input("魔法使い系技能レベル", value=magic_lv_sum, disabled=True, label_visibility="collapsed")
        first_skill_txt = "初期習得技能: "
        for name in st.session_state.first_skill:
            first_skill_txt += name + ","
        st.write(first_skill_txt.rstrip(","))
    st.divider()
    
    col1_warrior, col2_magic, col3_other = st.columns([1,1,1])
    with col1_warrior:
        st.write("##### 戦士系技能")
        for name in warrior_name_list:
            col1_warrior_1, col1_warrior_2 = st.columns([3,1])
            with col1_warrior_1:
                st.write(name)
            with col1_warrior_2:
                skill_data["skill"][skills_name_list.index(name)]["lv"] = st.number_input(name, min_value=0, max_value=17, step=1, label_visibility="collapsed", key=f"skill_lv_{skills_name_list.index(name)}", on_change=update_lv)
    with col2_magic:
        st.write("##### 魔法使い系技能")
        for name in magic_name_list:
            col1_magic_1, col1_magic_2 = st.columns([3,1])
            with col1_magic_1:
                st.write(name)
                if name == "プリースト":
                    st.selectbox("神選択", options=([" "]+[data["name"] for data in gods_data["god"]]), label_visibility="collapsed", key="faith")
            with col1_magic_2:
                skill_data["skill"][skills_name_list.index(name)]["lv"] = st.number_input(name, value=0, min_value=0, max_value=17, step=1, label_visibility="collapsed", key=f"skill_lv_{skills_name_list.index(name)}", on_change=update_lv)
    with col3_other:
        st.write("##### その他系技能")
        for name in other_name_list:
            col1_other_1, col1_other_2 = st.columns([3,1])
            with col1_other_1:
                st.write(name)
            with col1_other_2:
                skill_data["skill"][skills_name_list.index(name)]["lv"] = st.number_input(name, value=0, min_value=0, max_value=17, step=1, label_visibility="collapsed", key=f"skill_lv_{skills_name_list.index(name)}", on_change=update_lv)
    with col1_warrior:
        st.write("##### その他系技能2")
        for name in other2_name_list:
            col1_warrior_1, col1_warrior_2 = st.columns([3,1])
            with col1_warrior_1:
                st.write(name)
            with col1_warrior_2:
                skill_data["skill"][skills_name_list.index(name)]["lv"] = st.number_input(name, value=0, min_value=0, max_value=17, step=1, label_visibility="collapsed", key=f"skill_lv_{skills_name_list.index(name)}", on_change=update_lv)

#戦闘特技タブ
with st.expander("戦闘特技"):
    col_ability_1, col_ability_2, col_ability_3 = st.columns([1,4,6])
    #自動習得戦闘特技
    if (skill_data["skill"][skills_name_list.index("ファイター")]["lv"] >= 15) or (skill_data["skill"][skills_name_list.index("グラップラー")]["lv"] >= 15) or (skill_data["skill"][skills_name_list.index("バトルダンサー")]["lv"] >= 15):
        auto_ability_name = "バトルマスター"
        with col_ability_1:
            st.text_input("自", value="自", key=f"abi_lv_{auto_ability_name}", disabled=True, label_visibility="collapsed")
        with col_ability_2:
            st.text_input(f"戦闘特技_{auto_ability_name}", value=auto_ability_name, label_visibility="collapsed", key=f"ability_{auto_ability_name}")
        with col_ability_3:
            st.text_input(f"説明_{auto_ability_name}", value="複数宣言=2回", label_visibility="collapsed")
    if len(st.session_state.lv_list) >= len(magic_name_list):
        for i in range(len(skills_name_list)):
            if((skill_data["skill"][i]["name"] in magic_name_list) and (st.session_state.lv_list[i] >= 11)):
                auto_ability_name = "ルーンマスター"
                with col_ability_1:
                    st.text_input("自", value="自", key=f"abi_lv_{auto_ability_name}", disabled=True, label_visibility="collapsed")
                with col_ability_2:
                    st.text_input(f"戦闘特技_{auto_ability_name}", value=auto_ability_name, label_visibility="collapsed", key=f"ability_{auto_ability_name}")
                with col_ability_3:
                    st.text_input(f"説明_{auto_ability_name}", value="複数宣言=2回、一方は使用:魔法使い系技能に限る", label_visibility="collapsed")
                break
    if skill_data["skill"][skills_name_list.index("ファイター")]["lv"] >= 7:
        auto_ability_name = "タフネス"
        if st.session_state.hp_buf[3] != 15:
            st.session_state.hp_buf[3] = 15
            update_life_stats_list()
            st.rerun()
        with col_ability_1:
            st.text_input("自", value="自", key=f"abi_lv_{auto_ability_name}", disabled=True, label_visibility="collapsed")
        with col_ability_2:
            st.text_input(f"戦闘特技_{auto_ability_name}", value=auto_ability_name, label_visibility="collapsed", key=f"ability_{auto_ability_name}")
        with col_ability_3:
            st.text_input(f"説明_{auto_ability_name}", value="最大HP+15", label_visibility="collapsed")
    elif st.session_state.hp_buf[3] != 0:
        st.session_state.hp_buf[3] = 0
        update_life_stats_list()
        st.rerun()
    if skill_data["skill"][skills_name_list.index("グラップラー")]["lv"] >= 1:
        auto_ability_name = "追加攻撃"
        with col_ability_1:
            st.text_input("自", value="自", key=f"abi_lv_{auto_ability_name}", disabled=True, label_visibility="collapsed")
        with col_ability_2:
            st.text_input(f"戦闘特技_{auto_ability_name}", value=auto_ability_name, label_visibility="collapsed", key=f"ability_{auto_ability_name}")
        with col_ability_3:
            st.text_input(f"説明_{auto_ability_name}", value="1H格闘武器で追加攻撃を行う", label_visibility="collapsed")
    if skill_data["skill"][skills_name_list.index("グラップラー")]["lv"] >= 7:
        auto_ability_name = "カウンター"
        with col_ability_1:
            st.text_input("自", value="自", key=f"abi_lv_{auto_ability_name}", disabled=True, label_visibility="collapsed")
        with col_ability_2:
            st.text_input(f"戦闘特技_{auto_ability_name}", value=auto_ability_name, label_visibility="collapsed", key=f"ability_{auto_ability_name}")
        with col_ability_3:
            st.text_input(f"説明_{auto_ability_name}", value="近接攻撃に対して命中でカウンターを試みられる", label_visibility="collapsed")
    if skill_data["skill"][skills_name_list.index("バトルダンサー")]["lv"] >= 7:
        auto_ability_name = "舞い流し"
        with col_ability_1:
            st.text_input("自", value="自", key=f"abi_lv_{auto_ability_name}", disabled=True, label_visibility="collapsed")
        with col_ability_2:
            st.text_input(f"戦闘特技_{auto_ability_name}", value=auto_ability_name, label_visibility="collapsed", key=f"ability_{auto_ability_name}")
        with col_ability_3:
            st.text_input(f"説明_{auto_ability_name}", value="対象:1体の形状:射撃や貫通、突破の抵抗を回避で代用できる", label_visibility="collapsed")
    if skill_data["skill"][skills_name_list.index("スカウト")]["lv"] >= 5:
        auto_ability_name_list = [["トレジャーハンター", "掠め取り", "クルードテイク"], ["戦利品決定+1", "1H武器でクリティカルした時、クリティカルしない代わりに戦利品決定を行う" ,"戦利品決定の2dを1d×2にする"]]
        with col_ability_1:
            st.text_input("自", value="自", key=f"abi_lv_{auto_ability_name_list[0][0]}", disabled=True, label_visibility="collapsed")
        with col_ability_2:
            st.session_state.ability_mode[2] = st.selectbox(f"戦闘特技_{auto_ability_name_list[0][0]}", options=auto_ability_name_list[0], index=auto_ability_name_list[0].index(st.session_state.ability_mode[2] if st.session_state.get("ability_mode", [0,1," "])[2] != " " else "トレジャーハンター"), label_visibility="collapsed", key=f"ability_{auto_ability_name_list[0][0]}")
        with col_ability_3:
            st.text_input(f"説明_{auto_ability_name_list[0][0]}", value=auto_ability_name_list[1][auto_ability_name_list[0].index(st.session_state.get(f"ability_{auto_ability_name_list[0][0]}", "トレジャーハンター"))], label_visibility="collapsed")
    if skill_data["skill"][skills_name_list.index("スカウト")]["lv"] >= 7:
        auto_ability_name = "ファストアクション"
        with col_ability_1:
            st.text_input("自", value="自", key=f"abi_lv_{auto_ability_name}", disabled=True, label_visibility="collapsed")
        with col_ability_2:
            st.text_input(f"戦闘特技_{auto_ability_name}", value=auto_ability_name, label_visibility="collapsed", key=f"ability_{auto_ability_name}")
        with col_ability_3:
            st.text_input(f"説明_{auto_ability_name}", value="先制判定成功時、1ラウンド目の主動作+1回", label_visibility="collapsed")
    if skill_data["skill"][skills_name_list.index("スカウト")]["lv"] >= 9:
        auto_ability_name = "影走り"
        with col_ability_1:
            st.text_input("自", value="自", key=f"abi_lv_{auto_ability_name}", disabled=True, label_visibility="collapsed")
        with col_ability_2:
            st.text_input(f"戦闘特技_{auto_ability_name}", value=auto_ability_name, label_visibility="collapsed", key=f"ability_{auto_ability_name}")
        with col_ability_3:
            st.text_input(f"説明_{auto_ability_name}", value="移動妨害を受けずに移動できる", label_visibility="collapsed")
    if skill_data["skill"][skills_name_list.index("スカウト")]["lv"] >= 12:
        auto_ability_name = "トレジャーマスター"
        with col_ability_1:
            st.text_input("自", value="自", key=f"abi_lv_{auto_ability_name}", disabled=True, label_visibility="collapsed")
        with col_ability_2:
            st.text_input(f"戦闘特技_{auto_ability_name}", value=auto_ability_name, label_visibility="collapsed", key=f"ability_{auto_ability_name}")
        with col_ability_3:
            st.text_input(f"説明_{auto_ability_name}", value="戦利品決定+1", label_visibility="collapsed")
    if skill_data["skill"][skills_name_list.index("スカウト")]["lv"] >= 15:
        auto_ability_name = "匠の技"
        with col_ability_1:
            st.text_input("自", value="自", key=f"abi_lv_{auto_ability_name}", disabled=True, label_visibility="collapsed")
        with col_ability_2:
            st.text_input(f"戦闘特技_{auto_ability_name}", value=auto_ability_name, label_visibility="collapsed", key=f"ability_{auto_ability_name}")
        with col_ability_3:
            st.text_input(f"説明_{auto_ability_name}", value="スカウト技能による判定をいつでも1回振りなおせる", label_visibility="collapsed")
    if skill_data["skill"][skills_name_list.index("レンジャー")]["lv"] >= 5:
        auto_ability_name_list = [["サバイバビリティ", "掠め取り", "クルードテイク"], ["1日1回自然環境で抵抗力判定を自動成功にできる", "1H武器でクリティカルした時、クリティカルしない代わりに戦利品決定を行う" ,"戦利品決定の2dを1d×2にする"]]
        with col_ability_1:
            st.text_input("自", value="自", key=f"abi_lv_{auto_ability_name_list[0][0]}", disabled=True, label_visibility="collapsed")
        with col_ability_2:
            st.session_state.ability_mode[4] = st.selectbox(f"戦闘特技_{auto_ability_name_list[0][0]}", options=auto_ability_name_list[0], index=auto_ability_name_list[0].index(st.session_state.ability_mode[4] if st.session_state.get("ability_mode", [0,1,2,3," "])[4] != " " else "サバイバビリティ"), label_visibility="collapsed", key=f"ability_{auto_ability_name_list[0][0]}")
        with col_ability_3:
            st.text_input(f"説明_{auto_ability_name_list[0][0]}", value=auto_ability_name_list[1][auto_ability_name_list[0].index(st.session_state.get(f"ability_{auto_ability_name_list[0][0]}", "トレジャーハンター"))], label_visibility="collapsed")
    if skill_data["skill"][skills_name_list.index("レンジャー")]["lv"] >= 7:
        auto_ability_name = "不屈"
        with col_ability_1:
            st.text_input("自", value="自", key=f"abi_lv_{auto_ability_name}", disabled=True, label_visibility="collapsed")
        with col_ability_2:
            st.text_input(f"戦闘特技_{auto_ability_name}", value=auto_ability_name, label_visibility="collapsed", key=f"ability_{auto_ability_name}")
        with col_ability_3:
            st.text_input(f"説明_{auto_ability_name}", value="生死判定に成功で気絶しない", label_visibility="collapsed")
    if skill_data["skill"][skills_name_list.index("レンジャー")]["lv"] >= 9:
        auto_ability_name = "ポーションマスター"
        with col_ability_1:
            st.text_input("自", value="自", key=f"abi_lv_{auto_ability_name}", disabled=True, label_visibility="collapsed")
        with col_ability_2:
            st.text_input(f"戦闘特技_{auto_ability_name}", value=auto_ability_name, label_visibility="collapsed", key=f"ability_{auto_ability_name}")
        with col_ability_3:
            st.text_input(f"説明_{auto_ability_name}", value="1ラウンドに1回補助動作でポーションを使用できる", label_visibility="collapsed")
    if skill_data["skill"][skills_name_list.index("レンジャー")]["lv"] >= 12:
        auto_ability_name = "縮地"
        with col_ability_1:
            st.text_input("自", value="自", key=f"abi_lv_{auto_ability_name}", disabled=True, label_visibility="collapsed")
        with col_ability_2:
            st.text_input(f"戦闘特技_{auto_ability_name}", value=auto_ability_name, label_visibility="collapsed", key=f"ability_{auto_ability_name}")
        with col_ability_3:
            st.text_input(f"説明_{auto_ability_name}", value="全力移動をしても通常移動と同様の行動ができる", label_visibility="collapsed")
    if skill_data["skill"][skills_name_list.index("レンジャー")]["lv"] >= 15:
        auto_ability_name = "ランアンドガン"
        with col_ability_1:
            st.text_input("自", value="自", key=f"abi_lv_{auto_ability_name}", disabled=True, label_visibility="collapsed")
        with col_ability_2:
            st.text_input(f"戦闘特技_{auto_ability_name}", value=auto_ability_name, label_visibility="collapsed", key=f"ability_{auto_ability_name}")
        with col_ability_3:
            st.text_input(f"説明_{auto_ability_name}", value="通常移動をしても制限移動と同様の行動ができる", label_visibility="collapsed")
    if skill_data["skill"][skills_name_list.index("セージ")]["lv"] >= 5:
        auto_ability_name_list = [["鋭い目", "掠め取り", "クルードテイク"], ["戦利品決定+1", "1H武器でクリティカルした時、クリティカルしない代わりに戦利品決定を行う" ,"戦利品決定の2dを1d×2にする"]]
        with col_ability_1:
            st.text_input("自", value="自", key=f"abi_lv_{auto_ability_name_list[0][0]}", disabled=True, label_visibility="collapsed")
        with col_ability_2:
            st.session_state.ability_mode[6] = st.selectbox(f"戦闘特技_{auto_ability_name_list[0][0]}", options=auto_ability_name_list[0], index=auto_ability_name_list[0].index(st.session_state.ability_mode[6] if st.session_state.get("ability_mode", [0,1,2,3,4,5," "])[6] != " " else "鋭い目"), label_visibility="collapsed", key=f"ability_{auto_ability_name_list[0][0]}")
        with col_ability_3:
            st.text_input(f"説明_{auto_ability_name_list[0][0]}", value=auto_ability_name_list[1][auto_ability_name_list[0].index(st.session_state.get(f"ability_{auto_ability_name_list[0][0]}", "トレジャーハンター"))], label_visibility="collapsed")
    if skill_data["skill"][skills_name_list.index("セージ")]["lv"] >= 7:
        auto_ability_name = "弱点看破"
        with col_ability_1:
            st.text_input("自", value="自", key=f"abi_lv_{auto_ability_name}", disabled=True, label_visibility="collapsed")
        with col_ability_2:
            st.text_input(f"戦闘特技_{auto_ability_name}", value=auto_ability_name, label_visibility="collapsed", key=f"ability_{auto_ability_name}")
        with col_ability_3:
            st.text_input(f"説明_{auto_ability_name}", value="自身で見抜いた弱点を2倍で適用する", label_visibility="collapsed")
    if skill_data["skill"][skills_name_list.index("セージ")]["lv"] >= 9:
        auto_ability_name = "マナセーブ"
        with col_ability_1:
            st.text_input("自", value="自", key=f"abi_lv_{auto_ability_name}", disabled=True, label_visibility="collapsed")
        with col_ability_2:
            st.text_input(f"戦闘特技_{auto_ability_name}", value=auto_ability_name, label_visibility="collapsed", key=f"ability_{auto_ability_name}")
        with col_ability_3:
            st.text_input(f"説明_{auto_ability_name}", value="あらゆるMP消費-1", label_visibility="collapsed")
    if skill_data["skill"][skills_name_list.index("セージ")]["lv"] >= 12:
        auto_ability_name = "マナ耐性"
        with col_ability_1:
            st.text_input("自", value="自", key=f"abi_lv_{auto_ability_name}", disabled=True, label_visibility="collapsed")
        with col_ability_2:
            st.text_input(f"戦闘特技_{auto_ability_name}", value=auto_ability_name, label_visibility="collapsed", key=f"ability_{auto_ability_name}")
        with col_ability_3:
            st.text_input(f"説明_{auto_ability_name}", value="受ける魔法ダメージ-5", label_visibility="collapsed")
    if skill_data["skill"][skills_name_list.index("セージ")]["lv"] >= 15:
        auto_ability_name = "賢人の知恵"
        with col_ability_1:
            st.text_input("自", value="自", key=f"abi_lv_{auto_ability_name}", disabled=True, label_visibility="collapsed")
        with col_ability_2:
            st.text_input(f"戦闘特技_{auto_ability_name}", value=auto_ability_name, label_visibility="collapsed", key=f"ability_{auto_ability_name}")
        with col_ability_3:
            st.text_input(f"説明_{auto_ability_name}", value="セージ技能による判定をいつでも1回振りなおせる", label_visibility="collapsed")
    #バトルダンサー用追加戦闘特技
    if skill_data["skill"][skills_name_list.index("バトルダンサー")]["lv"] >= 1:
        with col_ability_1:
            st.text_input("舞", value="舞", key=f"abi_lv舞", disabled=True, label_visibility="collapsed")
        with col_ability_2:
            #battledancer_ability_list = [" " , "囮攻撃I", "切り返しI", "牽制攻撃I", "全力攻撃I", "挑発攻撃I", "必殺攻撃I", "魔力撃", "自由記入"]
            battledancer_ability_list = (
                [" "]
                + [data["name"] for data in ability_active_list if ((data["replace_lv"][1]<=main_lv) and data["flag"] == "B")]
            )
            if st.session_state.ability_mode[0] != "自由記入":
                try:
                    st.selectbox("戦闘特技_舞", options=battledancer_ability_list, index=battledancer_ability_list.index(st.session_state.ability_mode[0]), label_visibility="collapsed", key=f"ability_selectbox_0", on_change=update_ability_mode, args=(0,))
                except:
                    st.selectbox("戦闘特技_舞", options=battledancer_ability_list, index=0, label_visibility="collapsed", key=f"ability_selectbox_0", on_change=update_ability_mode, args=(0,))
                    update_ability_mode(0)
                if st.session_state.ability_mode[0] == "自由記入":
                    st.rerun()
                abi = st.session_state.ability_mode[0]
            else:
                col1_abi_input, col2_abi_free = st.columns([1,1])
                with col1_abi_input:
                    st.selectbox("戦闘特技_舞", battledancer_ability_list, index=battledancer_ability_list.index(st.session_state.ability_mode[0]), label_visibility="collapsed", key=f"ability_selectbox_0", on_change=update_ability_mode, args=(0,))
                    if st.session_state.ability_mode[0] != "自由記入":
                        st.rerun()
                with col2_abi_free:
                    abi = st.text_input("", placeholder="ここに入力", label_visibility="collapsed", key=f"free_text_0")
        with col_ability_3:
            abi__ = st.session_state.ability_mode[0]
            if abi__ == " ":
                st.text_input("説明_舞", label_visibility="collapsed")
            elif abi__ == "自由記入":
                st.text_input("説明_舞", label_visibility="collapsed")
            else:
                st.text_input("説明_舞", value=ability_all_list[ability_all_name_list.index(abi)]["explanation"], label_visibility="collapsed")
    else:
        st.session_state.ability_mode[0] = " "
    #1～15用戦闘特技
    for abi_lv in range(1, 16, 2):
        if abi_lv <= main_lv:
            with col_ability_1:
                st.number_input(abi_lv, value=abi_lv, key=f"abi_lv{abi_lv}", disabled=True, label_visibility="collapsed")
            with col_ability_2:
                # current_ability_list = (
                #     [" ", "---常時特技---"]
                #     + [data["name"] for data in ability_passive_list if ((data["required_lv"]<=abi_lv) and (data["replace_lv"]<=main_lv))]
                #     + ["---宣言特技---"]
                #     + [data["name"] for data in ability_active_list if ((data["required_lv"]<=abi_lv) and (data["replace_lv"]<=main_lv))]
                #     + ["---主動作型特技---"]
                #     + [data["name"] for data in ability_main_active_list if ((data["required_lv"]<=abi_lv) and (data["replace_lv"]<=main_lv))]
                #     + ["自由記入"]
                # )
                current_ability_list = [" ", "---常時特技---"]
                for i, list_name in enumerate([ability_passive_list, ability_active_list, ability_main_active_list]):
                    for data in list_name:
                        required_lv = replace_lv = 0
                        for j in range(len(data["required_lv"][0])):
                            required_lv = max(required_lv, main_lv if data["required_lv"][0][j] == "冒険者" else magic_lv_max if data["required_lv"][0][j] == "魔法使い" else skill_data["skill"][skills_name_list.index(data["required_lv"][0][j])]["lv"])
                            replace_lv  = max(replace_lv, main_lv if data["replace_lv"][0][j] == "冒険者" else magic_lv_max if data["required_lv"][0][j] == "魔法使い" else skill_data["skill"][skills_name_list.index(data["replace_lv"][0][j])]["lv"])
                        if((data["required_lv"][1] <= abi_lv ) and #習得可能レベル <= 戦闘特技枠のレベル かつ
                           (data["required_lv"][1] <= required_lv) and #習得可能レベル <= 要求技能のレベル かつ
                           (data["replace_lv"][1] <= replace_lv) and #置き換えレベル <= 要求技能のレベル かつ
                           (
                               ((data["flag"] != "M") and (set(data["required_skill"]).issubset(set(st.session_state.ability_mode[:abi_lv])))) or #フラグM(魔力強化)でない かつ 前提特技をすべて習得している または
                               ((data["flag"] == "R") and (bool(set(data["required_skill"]) & set(st.session_state.ability_mode[:abi_lv])))) or #フラグR かつ 前提が複数あるうち一つ以上習得している または
                               ((data["flag"] == "M") and ((data["required_lv"][1] <= magic_lv_second_max) and (data["replace_lv"][1] <= magic_lv_second_max))) #魔力強化用分岐
                            )
                        ):
                            current_ability_list.append(data["name"])
                    if i == 0:
                        current_ability_list.append("---宣言特技---")
                    elif i == 1:
                        current_ability_list.append("---主動作型特技---")
                    elif i == 2:
                        current_ability_list.append("自由記入")
                if st.session_state.ability_mode[abi_lv] != "自由記入":
                    try:
                        st.selectbox(f"戦闘特技{abi_lv}", options=current_ability_list, index=current_ability_list.index(st.session_state.ability_mode[abi_lv]), label_visibility="collapsed", key=f"ability_selectbox_{abi_lv}", on_change=update_ability_mode, args=(abi_lv,))
                    except:
                        st.selectbox(f"戦闘特技{abi_lv}", options=current_ability_list, index=0, label_visibility="collapsed", key=f"ability_selectbox_{abi_lv}", on_change=update_ability_mode, args=(abi_lv,))
                        update_ability_mode(abi_lv)
                    if st.session_state.ability_mode[abi_lv] == "自由記入":
                        st.rerun()
                    abi = st.session_state.ability_mode[abi_lv]
                else:
                    col1_abi_input, col2_abi_free = st.columns([1,1])
                    with col1_abi_input:
                        st.selectbox(f"戦闘特技{abi_lv}", options=current_ability_list, index=current_ability_list.index(st.session_state.ability_mode[abi_lv]), label_visibility="collapsed", key=f"ability_selectbox_{abi_lv}", on_change=update_ability_mode, args=(abi_lv,))
                        if st.session_state.ability_mode[abi_lv] != "自由記入":
                            st.rerun()
                    with col2_abi_free:
                        abi = st.text_input("", placeholder="ここに入力", label_visibility="collapsed", key=f"free_text_{abi_lv}")
            with col_ability_3:
                abi__ = st.session_state.ability_mode[abi_lv]
                if abi__ == " ":
                    st.text_input(f"説明{abi_lv}", label_visibility="collapsed")
                elif (abi__ == "---常時特技---") or (abi__ == "---宣言特技---") or (abi__ == "---主動作型特技---"):
                    st.error("選んじゃだめよ")
                elif abi__ == "自由記入":
                    st.text_input(f"説明{abi_lv}", label_visibility="collapsed")
                else:
                    st.text_input(f"説明{abi_lv}", value=ability_all_list[ability_all_name_list.index(abi)]["explanation"], label_visibility="collapsed")
        else:
            st.session_state.ability_mode[abi_lv] = " "
    #16,17用戦闘特技
    if main_lv >= 16:
        abi_lv = 16
        with col_ability_1:
            st.number_input(abi_lv, value=abi_lv, key=f"abi_lv{abi_lv}", disabled=True, label_visibility="collapsed")
        with col_ability_2:          
            current_ability_list = [" ", "---常時特技---"]
            for i, list_name in enumerate([ability_passive_list, ability_active_list, ability_main_active_list]):
                for data in list_name:
                    required_lv = replace_lv = 0
                    for j in range(len(data["required_lv"][0])):
                        required_lv = max(required_lv, main_lv if data["required_lv"][0][j] == "冒険者" else magic_lv_max if data["required_lv"][0][j] == "魔法使い" else skill_data["skill"][skills_name_list.index(data["required_lv"][0][j])]["lv"])
                        replace_lv  = max(replace_lv, main_lv if data["replace_lv"][0][j] == "冒険者" else magic_lv_max if data["required_lv"][0][j] == "魔法使い" else skill_data["skill"][skills_name_list.index(data["replace_lv"][0][j])]["lv"])
                    if((data["required_lv"][1] <= abi_lv ) and #習得可能レベル <= 戦闘特技枠のレベル かつ
                        (data["required_lv"][1] <= required_lv) and #習得可能レベル <= 要求技能のレベル かつ
                        (data["replace_lv"][1] <= replace_lv) and #置き換えレベル <= 要求技能のレベル かつ
                        (
                            ((data["flag"] != "M") and (set(data["required_skill"]).issubset(set(st.session_state.ability_mode[:abi_lv])))) or #フラグM(魔力強化)でない かつ 前提特技をすべて習得している または
                            ((data["flag"] == "R") and (bool(set(data["required_skill"]) & set(st.session_state.ability_mode[:abi_lv])))) or #フラグR かつ 前提が複数あるうち一つ以上習得している または
                            ((data["flag"] == "M") and ((data["required_lv"][1] <= magic_lv_second_max) and (data["replace_lv"][1] <= magic_lv_second_max))) #魔力強化用分岐
                        )
                    ):
                        current_ability_list.append(data["name"])
            if st.session_state.ability_mode[abi_lv] != "自由記入":
                st.selectbox(f"戦闘特技{abi_lv}", options=current_ability_list, index=current_ability_list.index(st.session_state.ability_mode[abi_lv]), label_visibility="collapsed", key=f"ability_selectbox_{abi_lv}", on_change=update_ability_mode, args=(abi_lv,))
                if st.session_state.ability_mode[abi_lv] == "自由記入":
                    st.rerun()
                abi = st.session_state.ability_mode[abi_lv]
            else:
                col1_abi_input, col2_abi_free = st.columns([1,1])
                with col1_abi_input:
                    st.selectbox(f"戦闘特技{abi_lv}", options=current_ability_list, index=current_ability_list.index(st.session_state.ability_mode[abi_lv]), label_visibility="collapsed", key=f"ability_selectbox_{abi_lv}", on_change=update_ability_mode, args=(abi_lv,))
                    if st.session_state.ability_mode[abi_lv] != "自由記入":
                        st.rerun()
                with col2_abi_free:
                    abi = st.text_input("", placeholder="ここに入力", label_visibility="collapsed", key=f"free_text_{abi_lv}")
        with col_ability_3:
            abi__ = st.session_state.ability_mode[abi_lv]
            if abi__ == " ":
                st.text_input(f"説明{abi_lv}", label_visibility="collapsed")
            elif (abi__ == "---常時特技---") or (abi__ == "---宣言特技---") or (abi__ == "---主動作型特技---"):
                st.error("選んじゃだめよ")
            elif abi__ == "自由記入":
                st.text_input(f"説明{abi_lv}", label_visibility="collapsed")
            else:
                st.text_input(f"説明{abi_lv}", value=ability_all_list[ability_all_name_list.index(abi)]["explanation"], label_visibility="collapsed")
    else:
        st.session_state.ability_mode[16] = " "
    if main_lv >= 17:
        abi_lv = 17
        with col_ability_1:
            st.number_input(abi_lv, value=abi_lv, key=f"abi_lv{abi_lv}", disabled=True, label_visibility="collapsed")
        with col_ability_2:
            current_ability_list = [" ", "---常時特技---"]
            for i, list_name in enumerate([ability_passive_list, ability_active_list, ability_main_active_list]):
                for data in list_name:
                    required_lv = replace_lv = 0
                    for j in range(len(data["required_lv"][0])):
                        required_lv = max(required_lv, main_lv if data["required_lv"][0][j] == "冒険者" else magic_lv_max if data["required_lv"][0][j] == "魔法使い" else skill_data["skill"][skills_name_list.index(data["required_lv"][0][j])]["lv"])
                        replace_lv  = max(replace_lv, main_lv if data["replace_lv"][0][j] == "冒険者" else magic_lv_max if data["required_lv"][0][j] == "魔法使い" else skill_data["skill"][skills_name_list.index(data["replace_lv"][0][j])]["lv"])
                    if((data["required_lv"][1] <= abi_lv ) and #習得可能レベル <= 戦闘特技枠のレベル かつ
                        (data["required_lv"][1] <= required_lv) and #習得可能レベル <= 要求技能のレベル かつ
                        (data["replace_lv"][1] <= replace_lv) and #置き換えレベル <= 要求技能のレベル かつ
                        (
                            ((data["flag"] != "M") and (set(data["required_skill"]).issubset(set(st.session_state.ability_mode[:abi_lv])))) or #フラグM(魔力強化)でない かつ 前提特技をすべて習得している または
                            ((data["flag"] == "R") and (bool(set(data["required_skill"]) & set(st.session_state.ability_mode[:abi_lv])))) or #フラグR かつ 前提が複数あるうち一つ以上習得している または
                            ((data["flag"] == "M") and ((data["required_lv"][1] <= magic_lv_second_max) and (data["replace_lv"][1] <= magic_lv_second_max))) #魔力強化用分岐
                        )
                    ):
                        current_ability_list.append(data["name"])
            if st.session_state.ability_mode[abi_lv] != "自由記入":
                st.selectbox(f"戦闘特技{abi_lv}", options=current_ability_list, index=current_ability_list.index(st.session_state.ability_mode[abi_lv]), label_visibility="collapsed", key=f"ability_selectbox_{abi_lv}", on_change=update_ability_mode, args=(abi_lv,))
                if st.session_state.ability_mode[abi_lv] == "自由記入":
                    st.rerun()
                abi = st.session_state.ability_mode[abi_lv]
            else:
                col1_abi_input, col2_abi_free = st.columns([1,1])
                with col1_abi_input:
                    st.selectbox(f"戦闘特技{abi_lv}", options=current_ability_list, index=current_ability_list.index(st.session_state.ability_mode[abi_lv]), label_visibility="collapsed", key=f"ability_selectbox_{abi_lv}", on_change=update_ability_mode, args=(abi_lv,))
                    if st.session_state.ability_mode[abi_lv] != "自由記入":
                        st.rerun()
                with col2_abi_free:
                    abi = st.text_input("", placeholder="ここに入力", label_visibility="collapsed", key=f"free_text_{abi_lv}")
        with col_ability_3:
            abi__ = st.session_state.ability_mode[abi_lv]
            if abi__ == " ":
                st.text_input(f"説明{abi_lv}", label_visibility="collapsed")
            elif (abi__ == "---常時特技---") or (abi__ == "---宣言特技---") or (abi__ == "---主動作型特技---"):
                st.error("選んじゃだめよ")
            elif abi__ == "自由記入":
                st.text_input(f"説明{abi_lv}", label_visibility="collapsed")
            else:
                st.text_input(f"説明{abi_lv}", value=ability_all_list[ability_all_name_list.index(abi)]["explanation"], label_visibility="collapsed")
    else:
        st.session_state.ability_mode[17] = " "
        update_ability_buf()
    st.info("※戦闘特技の置き換えは手動で行ってください")

#武器
with st.expander("武器"):
    col_weapon_name, col_weapon_strength, col_weapon_exclusive, col_weapon_accuracy, col_weapon_power, col_weapon_critical_value, col_weapon_add_damage, col_weapon_skill = st.columns([2.4, 0.6, 0.5, 1.2, 0.7, 0.7, 1.2, 1])
    with col_weapon_name:
        st.write("武器")
    with col_weapon_strength:
        st.write('<p style="font-size:14px">必筋</p>', unsafe_allow_html=True)
    with col_weapon_exclusive:
        st.write('<p style="font-size:12px">専用</p>', unsafe_allow_html=True)
    with col_weapon_accuracy:
        st.write("命中")
    with col_weapon_power:
        st.write("威力")
    with col_weapon_critical_value:
        st.write("C値")
    with col_weapon_add_damage:
        st.write("追加D")
    with col_weapon_skill:
        st.write('<p style="font-size:14px">使用技能</p>', unsafe_allow_html=True)
    weapon_list = []
    for i in range(st.session_state.weapon_list_num):
        weapon_list_buffer = []
        col_weapon_name, col_weapon_strength, col_weapon_exclusive, col_weapon_accuracy, col_weapon_power, col_weapon_critical_value, col_weapon_add_damage, col_weapon_skill = st.columns([2.4, 0.7, 0.4, 1.2, 0.7, 0.7, 1.2, 1])
        col_weapon_cost, col_weapon_usage, col_weapon_text, col_weapon_category = st.columns([2,1.6,6,2])
        with col_weapon_name:
            weapon_list_buffer.append(st.text_input(f"武器{i}名称", placeholder="名称", label_visibility="collapsed", key=f"weapon_{i}_0"))
        with col_weapon_cost:
            weapon_list_buffer.append(st.number_input(f"武器{i}価格", step=1, label_visibility="collapsed", placeholder="価格", help="価格", key=f"weapon_{i}_1"))
        with col_weapon_usage:
            weapon_list_buffer.append(st.selectbox(f"武器{i}用法", ["", "1H", "1H両" , "2H", "1H騎", "1H拳", "2H拳", "1H#", "2H#", "1H投", "2H投", "3H"], placeholder="用法", label_visibility="collapsed", key=f"weapon_{i}_2"))
        with col_weapon_strength:
            weapon_list_buffer.append(st.number_input(f"武器{i}必筋", step=1, label_visibility="collapsed", key=f"weapon_{i}_3"))
        with col_weapon_exclusive:
            weapon_list_buffer.append(st.checkbox(f"武器{i}専用", label_visibility="collapsed", key=f"weapon_{i}_4"))
        with col_weapon_skill:
            weapon_list_buffer.append(st.selectbox(f"武器{i}使用技能", [" ", "戦", "拳" ,"舞", "軽", "射", "魔", "練", "狩", "操"], label_visibility="collapsed", key=f"weapon_{i}_5"))
        with col_weapon_power:
            weapon_list_buffer.append(st.number_input(f"武器{i}威力", step=1, min_value=0 , max_value=100 ,label_visibility="collapsed", key=f"weapon_{i}_6"))
        with col_weapon_critical_value:
            weapon_list_buffer.append(st.number_input(f"武器{i}C値", step=1, label_visibility="collapsed", key=f"weapon_{i}_7"))
        with col_weapon_text:
            weapon_list_buffer.append(st.text_input(f"武器{i}備考", placeholder="備考", label_visibility="collapsed", key=f"weapon_{i}_8"))
        with col_weapon_category:
            weapon_list_buffer.append(st.selectbox(f"武器{i}カテゴリ", ["", "ソード", "アックス", "スピア", "メイス", "スタッフ", "フレイル", "ウォーハンマー", "格闘", "投擲", "ボウ", "クロスボウ", "ガン", "魔導書", "魔器", "その他"], label_visibility="collapsed", placeholder="カテゴリ", key=f"weapon_{i}_9"))
        with col_weapon_add_damage:
            col_weapon_add_damage_1, col_weapon_add_damage_2 = st.columns([2,1.4])
            with col_weapon_add_damage_1:
                weapon_list_buffer.append(st.number_input(f"武器{i}追加D", step=1, label_visibility="collapsed", key=f"weapon_{i}_10"))
            with col_weapon_add_damage_2:
                match weapon_list_buffer[5]:
                    case "戦":
                        skill_lv_damage = skill_data["skill"][skills_name_list.index("ファイター")]["lv"] + stats_list[2][5]       
                    case "拳":
                        skill_lv_damage = skill_data["skill"][skills_name_list.index("グラップラー")]["lv"] + stats_list[2][5]
                    case "舞":
                        skill_lv_damage = skill_data["skill"][skills_name_list.index("バトルダンサー")]["lv"] + stats_list[2][5]
                    case "軽":
                        skill_lv_damage = skill_data["skill"][skills_name_list.index("フェンサー")]["lv"] + stats_list[2][5]
                    case "射":
                        skill_lv_damage = skill_data["skill"][skills_name_list.index("シューター")]["lv"] + stats_list[2][5]
                    case "魔":
                        skill_lv_damage = skill_data["skill"][skills_name_list.index("デーモンルーラー")]["lv"] + stats_list[2][5]
                    case "練":
                        skill_lv_damage = skill_data["skill"][skills_name_list.index("エンハンサー")]["lv"] + stats_list[2][5]
                    case "狩":
                        skill_lv_damage = skill_data["skill"][skills_name_list.index("ダークハンター")]["lv"] + stats_list[5][5]
                    case "操":
                        skill_lv_damage = skill_data["skill"][skills_name_list.index("フィジカルマスター")]["lv"] + stats_list[2][5]
                    case _:
                        skill_lv_damage = 0
                weapon_mastery_damage = 0
                if f"武器習熟A/{weapon_list_buffer[9]}" in st.session_state.ability_mode:
                    weapon_mastery_damage += 1
                    if f"武器習熟S/{weapon_list_buffer[9]}" in st.session_state.ability_mode:
                        weapon_mastery_damage += 2
                if ((weapon_list_buffer[9] == "魔器") and ("魔器習熟A" in st.session_state.ability_mode)):
                    weapon_mastery_damage += 1
                    if "魔器習熟S" in st.session_state.ability_mode:
                        weapon_mastery_damage += 1
                        if "魔器の達人" in st.session_state.ability_mode:
                            weapon_mastery_damage += 1
                st.write(f"={(skill_lv_damage + weapon_mastery_damage + weapon_list_buffer[10])}")
        with col_weapon_accuracy:
            col_weapon_accuracy_1, col_weapon_accuracy_2 = st.columns([2,1.4])
            with col_weapon_accuracy_1: 
                weapon_list_buffer.append(st.number_input(f"武器{i}命中", step=1, label_visibility="collapsed", key=f"weapon_{i}_11"))
            with col_weapon_accuracy_2:
                match weapon_list_buffer[5]:
                    case "戦":
                        accuracy = skill_data["skill"][skills_name_list.index("ファイター")]["lv"] + int((stats_list[0][3]+stats_list[0][4]+stats_list[0][5]+(2 if weapon_list_buffer[4] else 0))/6)        
                    case "拳":
                        accuracy = skill_data["skill"][skills_name_list.index("グラップラー")]["lv"] + int((stats_list[0][3]+stats_list[0][4]+stats_list[0][5]+(2 if weapon_list_buffer[4] else 0))/6)        
                    case "舞":
                        accuracy = skill_data["skill"][skills_name_list.index("バトルダンサー")]["lv"] + int((stats_list[0][3]+stats_list[0][4]+stats_list[0][5]+(2 if weapon_list_buffer[4] else 0))/6)        
                    case "軽":
                        accuracy = skill_data["skill"][skills_name_list.index("フェンサー")]["lv"] + int((stats_list[0][3]+stats_list[0][4]+stats_list[0][5]+(2 if weapon_list_buffer[4] else 0))/6)        
                    case "射":
                        accuracy = skill_data["skill"][skills_name_list.index("シューター")]["lv"] + int((stats_list[0][3]+stats_list[0][4]+stats_list[0][5]+(2 if weapon_list_buffer[4] else 0))/6)        
                    case "魔":
                        accuracy = skill_data["skill"][skills_name_list.index("デーモンルーラー")]["lv"] + int((stats_list[0][3]+stats_list[0][4]+stats_list[0][5]+(2 if weapon_list_buffer[4] else 0))/6)
                    case "練":
                        accuracy = skill_data["skill"][skills_name_list.index("エンハンサー")]["lv"] + int((stats_list[0][3]+stats_list[0][4]+stats_list[0][5]+(2 if weapon_list_buffer[4] else 0))/6)
                    case "狩":
                        accuracy = skill_data["skill"][skills_name_list.index("ダークハンター")]["lv"] + int((stats_list[5][3]+stats_list[5][4]+stats_list[5][5])/6)
                    case "操":
                        accuracy = skill_data["skill"][skills_name_list.index("フィジカルマスター")]["lv"] + int((stats_list[0][3]+stats_list[0][4]+stats_list[0][5]+(2 if weapon_list_buffer[4] else 0))/6)
                    case _:
                        accuracy = 0
                if weapon_list_buffer[9] == "投擲":
                    if "スローイングI" in st.session_state.ability_mode:
                        accuracy += 1
                    elif "スローイングII" in st.session_state.ability_mode:
                        accuracy += 2
                st.write(f"={(accuracy + weapon_list_buffer[6] + st.session_state.accuracy_buf[0])}")
        weapon_list.append(weapon_list_buffer)
    with st.container(horizontal_alignment="left", horizontal=True):
        st.button("増加", on_click=update_weapon_list_num, args=(1,), key="wepon_list_add")
        st.button("減少", on_click=update_weapon_list_num, args=(-1,), key="wepon_list_sub")

#防具
with st.expander("防具"):
    col_armor_name, col_armor_exclusive, col_armor_strength, col_armor_avoidance, col_armor_protection, col_armor_other = st.columns([2.9,0.75,1,1,1,6.6])
    with col_armor_name:
        st.write("防具")
    with col_armor_exclusive:
        st.write('<p style="font-size:12px">専用</p>', unsafe_allow_html=True)
    with col_armor_strength:
        st.write("必筋")
    with col_armor_avoidance:
        st.write("回避")
    with col_armor_protection:
        st.write("防護")
    with col_armor_other:
        col_armor_cost, col_armor_other2 = st.columns([1.6,5])
        with col_armor_cost:
            st.write("価格")
        with col_armor_other2:
            st.write("備考")
    armor_list = [[],[],[],[]]
    col_armor_name, col_armor_exclusive, col_armor_strength, col_armor_avoidance, col_armor_protection, col_armor_other = st.columns([3,0.6,1,1,1,6.6])
    with col_armor_name:
        armor_list[0].append(st.text_input("鎧名称", placeholder="鎧", label_visibility="collapsed", key="armor_0_0"))
        armor_list[1].append(st.text_input("盾名称", placeholder="盾", label_visibility="collapsed", key="armor_1_0"))
        armor_list[2].append(st.text_input("その他名称", placeholder="その他", label_visibility="collapsed", key="armor_2_0"))
    with col_armor_exclusive:
        st.write("")
        armor_list[0].append(st.checkbox("鎧専用", label_visibility="collapsed", key="armor_0_1"))
        st.write("")
        armor_list[1].append(st.checkbox("盾専用", label_visibility="collapsed", key="armor_1_1"))
        st.write("")
        armor_list[2].append(st.checkbox("その他専用", label_visibility="collapsed", key="armor_2_1"))
    with col_armor_strength:
        armor_list[0].append(st.number_input("鎧必筋", step=1, label_visibility="collapsed", key="armor_0_2"))
        armor_list[1].append(st.number_input("盾必筋", step=1, label_visibility="collapsed", key="armor_1_2"))
        armor_list[2].append(st.number_input("その他必筋", step=1, label_visibility="collapsed", key="armor_2_2"))
    with col_armor_avoidance:
        armor_list[0].append(st.number_input("鎧回避", step=1, label_visibility="collapsed", key="armor_0_3"))
        armor_list[1].append(st.number_input("盾回避", step=1, label_visibility="collapsed", key="armor_1_3"))
        armor_list[2].append(st.number_input("その他回避", step=1, label_visibility="collapsed", key="armor_2_3"))
    with col_armor_protection:
        armor_list[0].append(st.number_input("鎧防護", step=1, label_visibility="collapsed", key="armor_0_4"))
        armor_list[1].append(st.number_input("盾防護", step=1, label_visibility="collapsed", key="armor_1_4"))
        armor_list[2].append(st.number_input("その他防護", step=1, label_visibility="collapsed", key="armor_2_4"))
    with col_armor_other:
        col_armor_cost, col_armor_other2 = st.columns([1.6,5])
        with col_armor_cost:
            armor_list[0].append(st.number_input("鎧価格", step=1, label_visibility="collapsed", key="armor_0_5"))
            armor_list[1].append(st.number_input("盾価格", step=1, label_visibility="collapsed", key="armor_1_5"))
            armor_list[2].append(st.number_input("その他価格", step=1, label_visibility="collapsed", key="armor_2_5"))
        with col_armor_other2:
            armor_list[0].append(st.text_input("鎧備考", label_visibility="collapsed", key="armor_0_6"))
            armor_list[1].append(st.text_input("盾備考", label_visibility="collapsed", key="armor_1_6"))
            armor_list[2].append(st.text_input("その他備考", label_visibility="collapsed", key="armor_2_6"))
        col_armor_mastery, col_armor_skill = st.columns([1,1])
        with col_armor_mastery:
            armor_list[3].append(st.selectbox("防具習熟", ["", "金属鎧", "非金属鎧"], label_visibility="collapsed", placeholder="防具習熟", key="armor_3_0"))
        with col_armor_skill:
            armor_list[3].append(st.selectbox("防具使用技能", ["", "戦", "拳" ,"舞", "軽", "射", "魔", "操"], label_visibility="collapsed", placeholder="使用技能", key="armor_3_1"))
            armor_list[3].append(0)
            armor_list[3].append(0)
            armor_list[3].append(0)
            armor_list[3].append(0)
    with col_armor_strength:
        st.write("計")
    with col_armor_avoidance:
        match armor_list[3][1]:
            case "戦":
                avoidance = skill_data["skill"][skills_name_list.index("ファイター")]["lv"] + int((stats_list[1][3]+stats_list[1][4]+stats_list[1][5]+(2 if armor_list[1][1] else 0))/6)        
            case "拳":
                avoidance = skill_data["skill"][skills_name_list.index("グラップラー")]["lv"] + int((stats_list[1][3]+stats_list[1][4]+stats_list[1][5]+(2 if armor_list[1][1] else 0))/6)        
            case "舞":
                avoidance = skill_data["skill"][skills_name_list.index("バトルダンサー")]["lv"] + int((stats_list[1][3]+stats_list[1][4]+stats_list[1][5]+(2 if armor_list[1][1] else 0))/6)        
            case "軽":
                avoidance = skill_data["skill"][skills_name_list.index("フェンサー")]["lv"] + int((stats_list[1][3]+stats_list[1][4]+stats_list[1][5]+(2 if armor_list[1][1] else 0))/6)        
            case "射":
                avoidance = skill_data["skill"][skills_name_list.index("シューター")]["lv"] + int((stats_list[1][3]+stats_list[1][4]+stats_list[1][5]+(2 if armor_list[1][1] else 0))/6)        
            case "魔":
                avoidance = skill_data["skill"][skills_name_list.index("デーモンルーラー")]["lv"] + int((stats_list[1][3]+stats_list[1][4]+stats_list[1][5]+(2 if armor_list[1][1] else 0))/6)
            case "操":
                avoidance = skill_data["skill"][skills_name_list.index("フィジカルマスター")]["lv"] + int((stats_list[1][3]+stats_list[1][4]+stats_list[1][5]+(2 if armor_list[1][1] else 0))/6)
            case _:
                avoidance = 0
        st.write(f"={(avoidance + armor_list[0][3] + armor_list[1][3] + armor_list[2][3] + st.session_state.equipment_buf[10] + sum(st.session_state.avoidance_buf))}")
    with col_armor_protection:
        armor_mastery_protection = 0
        if f"防具習熟A/{armor_list[3][0]}" in st.session_state.ability_mode:
            armor_mastery_protection += 1
            if f"防具習熟S/{armor_list[3][0]}" in st.session_state.ability_mode:
                armor_mastery_protection += 2
        if (f"防具習熟A/盾" in st.session_state.ability_mode) and (armor_list[1][2] > 0):
            armor_mastery_protection += 1
            if f"防具習熟S/盾" in st.session_state.ability_mode:
                armor_mastery_protection += 2
        if "魔器習熟A" in st.session_state.ability_mode:
            armor_mastery_protection += 1 if armor_list[0][2] > 0 else 0
            armor_mastery_protection += 1 if armor_list[1][2] > 0 else 0
            if "魔器習熟S" in st.session_state.ability_mode:
                armor_mastery_protection += 1 if armor_list[0][2] > 0 else 0
                armor_mastery_protection += 1 if armor_list[1][2] > 0 else 0
                if "魔器の達人" in st.session_state.ability_mode:
                    armor_mastery_protection += 1 if armor_list[0][2] > 0 else 0
                    armor_mastery_protection += 1 if armor_list[1][2] > 0 else 0
                
        st.write(f"={armor_mastery_protection + armor_list[0][4] + armor_list[1][4] + armor_list[2][4] + st.session_state.equipment_buf[11]}")

#装飾品
with st.expander("装飾品"):
    col_equipment_part, col_equipment_name, col_equipment_exclusive, col_equipment_cost, col_equipment_other, col_equipment_buf, col_equipment_add = st.columns([0.7,2,1.1,1,3,1,0.4])
    with col_equipment_part:
        st.write()
    with col_equipment_name:
        st.write("名称")
    with col_equipment_exclusive:
        st.write("専用")
    with col_equipment_cost:
        st.write("価格")
    with col_equipment_other:
        st.write("備考")
    with col_equipment_buf:
        st.write("効果")
    with col_equipment_add:
        st.write("")
    equipment_list = []
    for part in st.session_state.equipment_part_list:
        equipment_list_buffer_1 = []
        equipment_add_check = True
        i = 0
        while(equipment_add_check):
            equipment_list_buffer_2 = []
            col_equipment_part2, col_equipment_name2, col_equipment_exclusive2, col_equipment_cost2, col_equipment_other2, col_equipment_buf2, col_equipment_add2 = st.columns([0.7,2,1.1,1,3,1,0.4])
            with col_equipment_part2:
                if(i == 0):
                    st.write(f"{part}")
                else:
                    st.write("┗")
            with col_equipment_name2:
                equipment_list_buffer_2.append(st.text_input(f"{part}{i}名称", label_visibility="collapsed", key=f"equipment_{part}_{i}_0"))
            with col_equipment_exclusive2:
                equipment_list_buffer_2.append(st.selectbox(f"{part}{i}専用", [" ", "HP", "MP"], label_visibility="collapsed", on_change=update_equipment_exclusive_buf, key=f"equipment_{part}_{i}_1"))
            with col_equipment_cost2:
                equipment_list_buffer_2.append(st.number_input(f"{part}{i}価格", step=1, label_visibility="collapsed", key=f"equipment_{part}_{i}_2"))
            with col_equipment_other2:
                equipment_list_buffer_2.append(st.text_input(f"{part}{i}備考", label_visibility="collapsed", key=f"equipment_{part}_{i}_3"))
            with col_equipment_buf2:
                equipment_list_buffer_2.append(st.text_input(f"{part}{i}効果", label_visibility="collapsed", on_change=update_equipment_buf, key=f"equipment_{part}_{i}_4"))
            with col_equipment_add2:
                equipment_list_buffer_2.append(st.checkbox(f"{part}{i}増減" ,label_visibility="collapsed", key=f"equipment_{part}_{i}_5"))
                equipment_add_check = equipment_list_buffer_2[5]
            equipment_list_buffer_1.append(equipment_list_buffer_2)
            i += 1
        equipment_list.append(equipment_list_buffer_1)
    with st.expander("", icon="ℹ️", type="step"):
        st.info("""
            ※右のチェックボックスにチェックを入れると欄が増えます。\n
            ※効果欄に(数値)(既定の文字)とすると自動計算します。例)器用を1増やす→1A\n
            　器用～精神:A～F, 生命抵抗力:G, 精神抵抗力:H, HP:I, MP:J,\n
            　回避力:K, 防護点:L, 魔力:M, 魔物知識:N, 移動力:O
            """)

#所持品・所持金
with st.expander("所持品・所持金"):
    col_item_name, col_item_cost, col_item_get, col_item_lost, col_item_other = st.columns([3,1,1,1,5])
    with col_item_name:
        st.write("名称")
    with col_item_cost:
        st.write("単価")
    with col_item_get:
        st.write("所持数")
    with col_item_lost:
        st.write("消費数")
    with col_item_other:
        st.write("効果・備考など")
    item_list = []
    for i in range(st.session_state.item_list_num):
        item_list_buffer = []
        with col_item_name:
            item_list_buffer.append(st.text_input(f"所持品{i}名称", label_visibility="collapsed", key=f"item_{i}_0"))
        with col_item_cost:
            item_list_buffer.append(st.number_input(f"所持品{i}単価", step=1, label_visibility="collapsed", key=f"item_{i}_1"))
        with col_item_get:
            item_list_buffer.append(st.number_input(f"所持品{i}所持数", step=1, label_visibility="collapsed", key=f"item_{i}_2"))
        with col_item_lost:
            item_list_buffer.append(st.number_input(f"所持品{i}消費数", step=1, label_visibility="collapsed", key=f"item_{i}_3"))
        with col_item_other:
            item_list_buffer.append(st.text_input(f"所持品{i}備考", label_visibility="collapsed", key=f"item_{i}_4"))
        item_list.append(item_list_buffer)
    with st.container(horizontal_alignment="left", horizontal=True):
        st.button("増加", on_click=update_item_list_num, args=(1,), key="item_list_add")
        st.button("減少", on_click=update_item_list_num, args=(-1,), key="item_list_sub")
        st.write("")
        payment = 0
        for data in weapon_list:
            payment += data[1]
        for data in armor_list:
            payment += data[5]
        for i in range(len(st.session_state.equipment_part_list)):
            for data in equipment_list[i]:
                payment += data[2]
        for data in item_list:
            payment += data[1] * (data[2] + data[3])
        st.write(f"##### 所持金:{(st.session_state.money - payment)}")

#その他ステータス
with st.expander("その他ステータス"):
    col_other_stats_1, col_other_stats_2 = st.columns([1,1])
    with col_other_stats_1:
        col_move_1, col_move_2, col_move_3, col_move_4, col_move_5 = st.columns([4,1,4,1,4])
        with col_move_1:
            move_power_1 = st.number_input("移動力", value=(stats_list[1][3]+stats_list[1][4]+stats_list[1][5]+(2 if armor_list[0][1] else 0)+st.session_state.equipment_buf[14]), step=1, disabled=True)
        with col_move_2:
            st.write("######")
            st.write(r"\+")
        with col_move_3:
            move_power_2 = st.number_input("移_補", value=0, step=1, label_visibility="hidden", key="move_power_buf")
        with col_move_4:
            st.write("######")
            st.write(r"\=")
        with col_move_5:
            move_power_3 = st.number_input("移_結", value=(move_power_1 + move_power_2), step=1, disabled=True, label_visibility="hidden")
    with col_other_stats_2:
        col_move_6, col_move_7 = st.columns([4,10])
        with col_move_6:
            st.number_input("全力移動", value=(move_power_3 * 3), step=1, disabled=True)
        with col_move_7:
            st.write("######")
            gunti = st.checkbox("【軍師の知略】を用いる", key="gunti_check")
    with col_other_stats_1:
        col_mamotiki_1, col_mamotiki_2, col_mamotiki_3, col_mamotiki_4, col_mamotiki_5, col_mamotiki_6 = st.columns([4,3,1,3,1,3])
        mamotiki_skill_list = {"賢":"セージ", "騎":"ライダー", "狩":"ダークハンター"}
        with col_mamotiki_1:
            mamotiki_0 = skill_data["skill"][skills_name_list.index(mamotiki_skill_list[st.selectbox("魔物知識", options=mamotiki_skill_list, key="mamotiki_skill")])]["lv"]
            mamotiki_0 = (mamotiki_0 + stats_list[4][5] + st.session_state.equipment_buf[13]) if mamotiki_0 != 0 else 0
        with col_mamotiki_2:
            mamotiki_1 = st.number_input("魔知", value=(mamotiki_0), step=1, disabled=True, label_visibility="hidden")
        with col_mamotiki_3:
            st.write("######")
            st.write(r"\+")
        with col_mamotiki_4:
            mamotiki_2 = st.number_input("魔知_補", value=0, step=1, label_visibility="hidden", key="mamotiki_buf")
        with col_mamotiki_5:
            st.write("######")
            st.write(r"\=")
        with col_mamotiki_6:
            st.number_input("魔知_結", value=(mamotiki_1 + mamotiki_2), step=1, disabled=True, label_visibility="hidden")
    with col_other_stats_2:
        col_sensei_1, col_sensei_2, col_sensei_3, col_sensei_4, col_sensei_5, col_sensei_6 = st.columns([4,3,1,3,1,3])
        sensei_skill_list = {"斥":"スカウト", "軍":"ウォーリーダー"}
        with col_sensei_1:
            sensei_0 = skill_data["skill"][skills_name_list.index(sensei_skill_list[st.selectbox("先制力", options=sensei_skill_list, key="sensei_skill")])]["lv"]
            if sensei_0 != 0:
                if (gunti and (st.session_state["先制技能"] == "軍")):
                    sensei_0 = sensei_0 + stats_list[4][5] +1
                else:
                    sensei_0 = sensei_0 + stats_list[1][5]
        with col_sensei_2:
            sensei_1 = st.number_input("先制", value=(sensei_0), step=1, disabled=True, label_visibility="hidden")
        with col_sensei_3:
            st.write("######")
            st.write(r"\+")
        with col_sensei_4:
            sensei_2 = st.number_input("先制_補", value=0, step=1, label_visibility="hidden", key="sensei_buf")
        with col_sensei_5:
            st.write("######")
            st.write(r"\=")
        with col_sensei_6:
            st.number_input("先制_結", value=(sensei_1 + sensei_2), step=1, disabled=True, label_visibility="hidden")

#言語
with st.expander("言語"):
    all_language_list = []
    col_language_name, col_language_talk, col_language_read = st.columns([6,1,1])
    with col_language_name:
        st.write("言語")
    with col_language_talk:
        st.write("会話")
    with col_language_read:
        st.write("読文")
    if ((race__ == " ") or (race__ == "自由記入")):
        st.empty()
    #初期習得言語
    else:
        first_language_list = []
        first_language = race_data["race"][(race_list.index(race)-1)]["language"]
        for i in range(len(first_language)):
            first_language_list_buffer = []
            col_language_name_2, col_language_talk_2, col_language_read_2 = st.columns([6,1,1])
            with col_language_name_2:
                if (first_language[i][0] != "地方語") and (first_language[i][0] != "自由記入"):
                    first_language_list_buffer.append(st.selectbox(f"言語{i}", options=language_name_list, index=language_name_list.index(first_language[i][0]), label_visibility="collapsed", disabled=True, key=f"first_language_selectbox_{i}"))
                    if (first_language_list_buffer[0] == "地方語") or (first_language_list_buffer[0] == "自由記入"):
                        st.rerun()
                    first_language_list_buffer.append("")
                else:
                    col2_language_name_1, col2_language_name_2 = st.columns([1,3])
                    with col2_language_name_1:
                        first_language_list_buffer.append(st.selectbox(f"言語{i}", options=language_name_list, index=language_name_list.index(first_language[i][0]), label_visibility="collapsed", disabled=True, key=f"first_language_selectbox_{i}"))
                        if (first_language_list_buffer[0] != "地方語") and (first_language_list_buffer[0] != "自由記入"):
                            st.rerun()
                    with col2_language_name_2:
                        first_language_list_buffer.append(st.text_input("", placeholder="ここに入力", label_visibility="collapsed", key=f"first_language_free_{i}"))
            with col_language_talk_2:
                if (first_language_list_buffer[0] != " ") and (first_language_list_buffer[0] != "地方語") and (first_language_list_buffer[0] != "自由記入"):
                    language_exist = not language_data["language"][language_name_list.index(first_language_list_buffer[0])-1]["exist"][0]
                else:
                    language_exist = False
                first_language_list_buffer.append(st.checkbox(f"初期会話{i}", value=first_language[i][1], label_visibility="collapsed", disabled=language_exist, key=f"first_language_exist_talk_{i}"))
            with col_language_read_2:
                if (first_language_list_buffer[0] != " ") and (first_language_list_buffer[0] != "地方語") and (first_language_list_buffer[0] != "自由記入"):
                    language_exist = not language_data["language"][language_name_list.index(first_language_list_buffer[0])-1]["exist"][1]
                else:
                    language_exist = False
                first_language_list_buffer.append(st.checkbox(f"初期読文{i}", value=first_language[i][2], label_visibility="collapsed", disabled=language_exist, key=f"first_language_exist_read_{i}"))
            first_language_list.append(first_language_list_buffer)
        all_language_list.append(first_language_list)
    #自動習得言語
        #実装予定？
    #任意習得言語
    language_list = []
    for i in range(st.session_state.language_list_num):
        language_list_buffer = []
        col_language_name_2, col_language_talk_2, col_language_read_2 = st.columns([6,1,1])
        with col_language_name_2:
            if (st.session_state.get(f"language_selectbox_{i}", " ") != "地方語") and (st.session_state.get(f"language_selectbox_{i}", " ") != "自由記入"):
                language_list_buffer.append(st.selectbox(f"言語{i}", options=language_name_list, index=language_name_list.index(st.session_state.get(f"language_selectbox_{i}", " ")), label_visibility="collapsed", key=f"language_selectbox_{i}"))
                if (language_list_buffer[0] == "地方語") or (language_list_buffer[0] == "自由記入"):
                    st.rerun()
                language_list_buffer.append("")
            else:
                col2_language_name_1, col2_language_name_2 = st.columns([1,3])
                with col2_language_name_1:
                    language_list_buffer.append(st.selectbox(f"言語{i}", options=language_name_list, index=language_name_list.index(st.session_state[f"language_selectbox_{i}"]), label_visibility="collapsed", key=f"language_selectbox_{i}"))
                    if (language_list_buffer[0] != "地方語") and (language_list_buffer[0] != "自由記入"):
                        st.rerun()
                with col2_language_name_2:
                    language_list_buffer.append(st.text_input("", placeholder="ここに入力", label_visibility="collapsed", key=f"language_free_{i}"))
        with col_language_talk_2:
            if (language_list_buffer[0] != " ") and (language_list_buffer[0] != "地方語") and (language_list_buffer[0] != "自由記入"):
                language_exist = not language_data["language"][language_name_list.index(language_list_buffer[0])-1]["exist"][0]
            else:
                language_exist = False
            language_list_buffer.append(st.checkbox(f"会話{i}", label_visibility="collapsed", disabled=language_exist, key=f"language_exist_talk_{i}"))
        with col_language_read_2:
            if (language_list_buffer[0] != " ") and (language_list_buffer[0] != "地方語") and (language_list_buffer[0] != "自由記入"):
                language_exist = not language_data["language"][language_name_list.index(language_list_buffer[0])-1]["exist"][1]
            else:
                language_exist = False
            language_list_buffer.append(st.checkbox(f"読文{i}", label_visibility="collapsed", disabled=language_exist, key=f"language_exist_read_{i}"))
        language_list.append(language_list_buffer)
    all_language_list.append(language_list)
    with st.container(horizontal_alignment="left", horizontal=True):
        st.button("増加", on_click=update_language_list_num, args=(1,), key="language_list_add")
        st.button("減少", on_click=update_language_list_num, args=(-1,), key="language_list_sub")

#魔力
maryoku_dict = {}
if magic_lv_sum > 0:
    with st.expander("魔力"):
        col_maryoku_name, col_maryoku_exclusive, col_maryoku_buf, col_maryoku_kousi, col_maryoku_damage = st.columns([1.5,0.4,1,1,1])
        with col_maryoku_name:
            st.write("魔法")
        with col_maryoku_exclusive:
            st.write("専用")
        with col_maryoku_buf:
            st.write("魔力補正")
        with col_maryoku_kousi:
            st.write("行使補正")
        with col_maryoku_damage:
            st.write("ダメージ補正")
        maryoku_list_all = [0] * 3
        col_maryoku_name_1, col_maryoku_exclusive_1, col_maryoku_buf_1, col_maryoku_kousi_1, col_maryoku_damage_1 = st.columns([1.5,0.4,1,1,1])
        with col_maryoku_name_1:
            st.text_input("全魔法", value="全魔法", label_visibility="collapsed", disabled=True)
        with col_maryoku_buf_1:
            col_maryoku_buf_2, col_maryoku_buf_3 = st.columns([2,1])
            with col_maryoku_buf_2:
                maryoku_list_all[0] = st.number_input("全魔法_魔力補正", value=(st.session_state.equipment_buf[12]), step=1, label_visibility="collapsed", key="all_maryoku_0")
                maryoku_list_all[0] += 1 if "魔力強化I" in st.session_state.ability_mode else 2 if "魔力強化II" in st.session_state.ability_mode else 0
        with col_maryoku_kousi_1:
            col_maryoku_kousi_2, col_maryoku_kousi_3 = st.columns([2,1])
            with col_maryoku_kousi_2:
                maryoku_list_all[1] = st.number_input("全魔法_行使補正", step=1, label_visibility="collapsed", key="all_maryoku_1")
        with col_maryoku_damage_1:
            col_maryoku_damage_2, col_maryoku_damage_3 = st.columns([2,1])
            with col_maryoku_damage_2:
                maryoku_list_all[2] = st.number_input("全魔法_ダメージ補正", step=1, label_visibility="collapsed", key="all_maryoku_2")
        maryoku_dict["全魔法"] = maryoku_list_all
        for name in magic_name_list:
            if skill_data["skill"][skills_name_list.index(name)]["lv"] > 0:
                maryoku_list = [0] * 5
                col_maryoku_name_1, col_maryoku_exclusive_1, col_maryoku_buf_1, col_maryoku_kousi_1, col_maryoku_damage_1 = st.columns([1.5,0.4,1,1,1])
                with col_maryoku_name_1:
                    st.text_input(name, value=name, label_visibility="collapsed", disabled=True)
                with col_maryoku_exclusive_1:
                    maryoku_list[0] = st.checkbox(f"{name}_専用", label_visibility="collapsed", key=f"maryoku_{name}_0")
                with col_maryoku_buf_1:
                    col_maryoku_buf_2, col_maryoku_buf_3 = st.columns([2,1])
                    with col_maryoku_buf_2:
                        maryoku_list[1] = st.number_input(f"{name}_魔力補正", step=1, label_visibility="collapsed", key=f"maryoku_{name}_1")
                    with col_maryoku_buf_3:
                        maryoku_list[2] = skill_data["skill"][skills_name_list.index(name)]["lv"] + stats_list[4][5] + maryoku_list[1] + maryoku_list_all[0]
                        st.write(f"={maryoku_list[2]}")
                with col_maryoku_kousi_1:
                    col_maryoku_kousi_2, col_maryoku_kousi_3 = st.columns([2,1])
                    with col_maryoku_kousi_2:
                        maryoku_list[3] = st.number_input(f"{name}_行使補正", step=1, label_visibility="collapsed", key=f"maryoku_{name}_3")
                    with col_maryoku_kousi_3:
                        st.write(f"={(skill_data["skill"][skills_name_list.index(name)]["lv"] + int((stats_list[4][3]+stats_list[4][4]+(2 if maryoku_list[0] else 0))/6) + maryoku_list[1] + maryoku_list[3] + maryoku_list_all[1])}")
                with col_maryoku_damage_1:
                    col_maryoku_damage_2, col_maryoku_damage_3 = st.columns([2,1])
                    with col_maryoku_damage_2:
                        maryoku_list[4] = st.number_input(f"{name}_ダメージ補正", step=1, label_visibility="collapsed", key=f"maryoku_{name}_4")
                    with col_maryoku_damage_3:
                        st.write(f"={(maryoku_list[2] + maryoku_list[4] + maryoku_list_all[2])}")
                maryoku_dict[name] = maryoku_list
                #ウィザード魔力
                if ((name == "コンジャラー") and (skill_data["skill"][skills_name_list.index("ソーサラー")]["lv"] > 0) and (skill_data["skill"][skills_name_list.index("コンジャラー")]["lv"] > 0)):
                    maryoku_list = [0] * 5
                    max_maryoku = max(skill_data["skill"][skills_name_list.index("ソーサラー")]["lv"], skill_data["skill"][skills_name_list.index("コンジャラー")]["lv"])
                    col_maryoku_name_1, col_maryoku_exclusive_1, col_maryoku_buf_1, col_maryoku_kousi_1, col_maryoku_damage_1 = st.columns([1.5,0.4,1,1,1])
                    with col_maryoku_name_1:
                        st.text_input("ウィザード", value="ウィザード", label_visibility="collapsed", disabled=True)
                    with col_maryoku_exclusive_1:
                        maryoku_list[0] = st.checkbox(f"ウィザード_専用", label_visibility="collapsed", key="maryoku_ウィザード_0")
                    with col_maryoku_buf_1:
                        col_maryoku_buf_2, col_maryoku_buf_3 = st.columns([2,1])
                        with col_maryoku_buf_2:
                            maryoku_list[1] = st.number_input(f"ウィザード_魔力補正", step=1, label_visibility="collapsed", key="maryoku_ウィザード_1")
                        with col_maryoku_buf_3:
                            maryoku_list[2] = max_maryoku + stats_list[4][5] + maryoku_list[1] + maryoku_list_all[0]
                            st.write(f"={maryoku_list[2]}")
                    with col_maryoku_kousi_1:
                        col_maryoku_kousi_2, col_maryoku_kousi_3 = st.columns([2,1])
                        with col_maryoku_kousi_2:
                            maryoku_list[3] = st.number_input(f"ウィザード_行使補正", step=1, label_visibility="collapsed", key="maryoku_ウィザード_3")
                        with col_maryoku_kousi_3:
                            st.write(f"={(max_maryoku + int((stats_list[4][3]+stats_list[4][4]+(2 if maryoku_list[0] else 0))/6) + maryoku_list[1] + maryoku_list[3] + maryoku_list_all[1])}")
                    with col_maryoku_damage_1:
                        col_maryoku_damage_2, col_maryoku_damage_3 = st.columns([2,1])
                        with col_maryoku_damage_2:
                            maryoku_list[4] = st.number_input(f"ウィザード_ダメージ補正", step=1, label_visibility="collapsed", key="maryoku_ウィザード_4")
                        with col_maryoku_damage_3:
                            st.write(f"={(maryoku_list[2] + maryoku_list[4] + maryoku_list_all[2])}")
                    maryoku_dict["ウィザード"] = maryoku_list
                #フェアテ契約
                if name == "フェアリーテイマー":
                    fairy_contract_list = [0] * 6
                    col_fairy_rank, col_fairy_stone, col_fairy_water, col_fairy_fire, col_fairy_wind, col_fairy_light, col_fairy_dark = st.columns([1.5,1,1,1,1,1,1])
                    with col_fairy_stone:
                        fairy_contract_list[0] = st.checkbox("土", key="fairy_contract_0")
                    with col_fairy_water:
                        fairy_contract_list[1] = st.checkbox("水・氷", key="fairy_contract_1")
                    with col_fairy_fire:
                        fairy_contract_list[2] = st.checkbox("炎", key="fairy_contract_2")
                    with col_fairy_wind:
                        fairy_contract_list[3] = st.checkbox("風", key="fairy_contract_3")
                    with col_fairy_light:
                        fairy_contract_list[4] = st.checkbox("光", key="fairy_contract_4")
                    with col_fairy_dark:
                        fairy_contract_list[5] = st.checkbox("闇", key="fairy_contract_5")
                    with col_fairy_rank:
                        fairy_rank = "不正"
                        fairy_contact = 0
                        for contact in fairy_contract_list:
                            fairy_contact += 1 if contact else 0
                        if sum(fairy_contract_list) == 4:
                            fairy_rank = skill_data["skill"][skills_name_list.index("フェアリーテイマー")]["lv"]
                        elif sum(fairy_contract_list) == 3:
                            fairy_rank = "3属性契約の処理を書く"
                        elif sum(fairy_contract_list) == 6:
                            fairy_rank = "6属性契約の処理を書く"
                        st.write(f"ランク：{fairy_rank}")
                    maryoku_dict["フェアリーテイマー契約"] = fairy_contract_list
                #ビブリオ処理
                if name == "ビブリオマンサー":
                    hiou_magic_list = []
                    with st.expander("準備行使枠", type="compact"):
                        hiou_magic_list_buffer = []
                        for i in range(skill_data["skill"][skills_name_list.index("ビブリオマンサー")]["lv"]):
                            i = i + 1
                            col_hiou_lv, col_hiou_name, col_hiou_mp, col_hiou_other = st.columns([1,4,1,5])
                            with col_hiou_lv:
                                st.number_input(f"秘奥lv_{i}", value=i, label_visibility="collapsed", disabled=True)
                            with col_hiou_name:
                                hiou_list_now = [" "] + [data["name"] for data in hiou_list if data["required_lv"]<=i]
                                hiou = st.selectbox(f"秘奥_{i}", options=hiou_list_now, label_visibility="collapsed", key=f"hiou_magic_0_{(i-1)}")
                                hiou_magic_list_buffer.append(hiou)
                            with col_hiou_mp:
                                st.number_input(f"秘奥MP_{i}", value=(hiou_list[hiou_list_now.index(hiou)-1]["mp"] if hiou != " " else 0), label_visibility="collapsed", disabled=True)
                            with col_hiou_other:
                                st.text_input(f"秘奥効果_{i}", value=(hiou_list[hiou_list_now.index(hiou)-1]["explanation"] if hiou != " " else ""), label_visibility="collapsed")
                    hiou_magic_list.append(hiou_magic_list_buffer)
                    with st.expander("応急行使枠", type="compact"):
                        hiou_magic_list_buffer = []
                        for i in range(int((skill_data["skill"][skills_name_list.index("ビブリオマンサー")]["lv"] + 2)/3)):
                            col_hiou_lv, col_hiou_name, col_hiou_mp, col_hiou_other = st.columns([1,4,1,5])
                            with col_hiou_lv:
                                st.text_input(f"応急_秘奥lv_{i}", value="応", label_visibility="collapsed", disabled=True)
                            with col_hiou_name:
                                hiou_list_now = [" "] + [data["name"] for data in hiou_list if data["required_lv"] <= skill_data["skill"][skills_name_list.index("ビブリオマンサー")]["lv"]]
                                hiou = st.selectbox(f"応急_秘奥_{i}", options=hiou_list_now, label_visibility="collapsed", key=f"hiou_magic_1_{i}")
                                hiou_magic_list_buffer.append(hiou)
                            with col_hiou_mp:
                                st.number_input(f"応急_秘奥MP_{i}", value=(hiou_list[hiou_list_now.index(hiou)-1]["mp"] if hiou != " " else 0), label_visibility="collapsed", disabled=True)
                            with col_hiou_other:
                                st.text_input(f"応急_秘奥効果_{i}", value=(hiou_list[hiou_list_now.index(hiou)-1]["explanation"] if hiou != " " else ""), label_visibility="collapsed")
                    hiou_magic_list.append(hiou_magic_list_buffer)
                    maryoku_dict["ビブリオマンサー魔法"] = hiou_magic_list

#練技
if skill_data["skill"][skills_name_list.index("エンハンサー")]["lv"] > 0:
    rengi_list_buffer = []
    with st.expander("練技"):
        for i in range(skill_data["skill"][skills_name_list.index("エンハンサー")]["lv"]):
            i = i + 1
            col_rengi_lv, col_rengi_name, col_rengi_other = st.columns([1,4,6])
            with col_rengi_lv:
                st.number_input(f"練技lv_{i}", value=i, label_visibility="collapsed", disabled=True)
            with col_rengi_name:
                rengi_list_now = [" "] + [data["name"] for data in rengi_list if data["required_lv"]<=i]
                rengi = st.selectbox(f"練技_{i}", options=rengi_list_now, label_visibility="collapsed", key=f"enhancer_{(i-1)}")
                rengi_list_buffer.append(rengi)
            with col_rengi_other:
                st.text_input(f"練技効果_{i}", value=(rengi_list[[data["name"] for data in rengi_list].index(rengi)]["explanation"] if rengi != " " else ""), label_visibility="collapsed")
    other_skill_dict["enhancer"] = rengi_list_buffer

#呪歌
if skill_data["skill"][skills_name_list.index("バード")]["lv"] > 0:
    juka_list_buffer = []
    with st.expander("呪歌"):
        col_juka_lv_0, col_juka_name_0, col_juka_need_0, col_juka_create_0, col_juka_advanced_0, col_juka_other_0 = st.columns([1,3,1.2,1.2,1.2,3.4])
        with col_juka_lv_0:
            st.empty()
        with col_juka_name_0:
            st.write("名称")
        with col_juka_need_0:
            st.write("必要")
        with col_juka_create_0:
            st.write("生成")
        with col_juka_advanced_0:
            st.write("追加")
        with col_juka_other_0:
            st.write("効果")
        if "呪歌追加I" in st.session_state.ability_mode:
            add_juka = 1
        elif "呪歌追加II" in st.session_state.ability_mode:
            add_juka = 2
        elif "呪歌追加III" in st.session_state.ability_mode:
            add_juka = 3
        else:
            add_juka = 0
        for i in range(add_juka):
            i = i + 1
            col_juka_lv_1, col_juka_name_1, col_juka_need_1, col_juka_create_1, col_juka_advanced_1, col_juka_other_1 = st.columns([1,3,1.2,1.2,1.2,3.4])
            with col_juka_lv_1:
                st.text_input(f"追加呪歌_lv_{i}", value="追", label_visibility="collapsed", disabled=True)
            with col_juka_name_1:
                juka_list_now = [" "] + [data["name"] for data in juka_list if data["required_lv"] <= skill_data["skill"][skills_name_list.index("バード")]["lv"]]
                juka = st.selectbox(f"追加呪歌_{i}", options=juka_list_now, label_visibility="collapsed", key=f"add_bard_{(i-1)}")
                juka_list_buffer.append(juka)
            with col_juka_need_1:
                st.text_input(f"追加呪歌必要_{i}", value=(juka_list[[data["name"] for data in juka_list].index(juka)]["gakuso"][0] if juka != " " else ""), label_visibility="collapsed")
            with col_juka_create_1:
                st.text_input(f"追加呪歌生成_{i}", value=(juka_list[[data["name"] for data in juka_list].index(juka)]["gakuso"][1] if juka != " " else ""), label_visibility="collapsed")
            with col_juka_advanced_1:
                st.text_input(f"追加呪歌追加_{i}", value=(juka_list[[data["name"] for data in juka_list].index(juka)]["gakuso"][2] if juka != " " else ""), label_visibility="collapsed")
            with col_juka_other_1:
                st.text_input(f"追加呪歌効果_{i}", value=(juka_list[[data["name"] for data in juka_list].index(juka)]["explanation"] if juka != " " else ""), label_visibility="collapsed")
        other_skill_dict["add_bard"] = juka_list_buffer
        juka_list_buffer = []
        for i in range(skill_data["skill"][skills_name_list.index("バード")]["lv"]):
            i = i + 1
            col_juka_lv_1, col_juka_name_1, col_juka_need_1, col_juka_create_1, col_juka_advanced_1, col_juka_other_1 = st.columns([1,3,1.2,1.2,1.2,3.4])
            with col_juka_lv_1:
                st.number_input(f"呪歌_lv_{i}", value=i, label_visibility="collapsed", disabled=True)
            with col_juka_name_1:
                juka_list_now = [" "] + [data["name"] for data in juka_list if data["required_lv"]<=i]
                juka = st.selectbox(f"呪歌_{i}", options=juka_list_now, label_visibility="collapsed", key=f"bard_{(i-1)}")
                juka_list_buffer.append(juka)
            with col_juka_need_1:
                st.text_input(f"呪歌必要_{i}", value=(juka_list[[data["name"] for data in juka_list].index(juka)]["gakuso"][0] if juka != " " else ""), label_visibility="collapsed")
            with col_juka_create_1:
                st.text_input(f"呪歌生成_{i}", value=(juka_list[[data["name"] for data in juka_list].index(juka)]["gakuso"][1] if juka != " " else ""), label_visibility="collapsed")
            with col_juka_advanced_1:
                st.text_input(f"呪歌追加_{i}", value=(juka_list[[data["name"] for data in juka_list].index(juka)]["gakuso"][2] if juka != " " else ""), label_visibility="collapsed")
            with col_juka_other_1:
                st.text_input(f"呪歌効果_{i}", value=(juka_list[[data["name"] for data in juka_list].index(juka)]["explanation"] if juka != " " else ""), label_visibility="collapsed")
    other_skill_dict["bard"] = juka_list_buffer

#騎芸
if skill_data["skill"][skills_name_list.index("ライダー")]["lv"] > 0:
    kigei_list_buffer = []
    with st.expander("騎芸"):
        for i in range(skill_data["skill"][skills_name_list.index("ライダー")]["lv"]):
            i = i + 1
            col_kigei_lv_0, col_kigei_name_0, col_kigei_other_0 = st.columns([1,4,6])
            with col_kigei_lv_0:
                st.number_input(f"騎芸lv_{i}", value=i, label_visibility="collapsed", disabled=True)
            with col_kigei_name_0:
                kigei_list_now = [" "] + [data["name"] for data in kigei_list if data["required_lv"]<=i]
                kigei = st.selectbox(f"騎芸_{i}", options=kigei_list_now, label_visibility="collapsed", key=f"rider_{(i-1)}")
                kigei_list_buffer.append(kigei)
            with col_kigei_other_0:
                st.text_input(f"騎芸効果_{i}", value=(kigei_list[[data["name"] for data in kigei_list].index(kigei)]["explanation"] if kigei != " " else ""), label_visibility="collapsed")
    other_skill_dict["rider"] = kigei_list_buffer

#賦術
if skill_data["skill"][skills_name_list.index("アルケミスト")]["lv"] > 0:
    hujutu_list_buffer = []
    with st.expander("賦術"):
        col_hujutu_lv_0, col_hujutu_name_0, col_hujutu_need_0, col_hujutu_other_0, col_hujutu_BASSS_0 = st.columns([1,3,1,4,2])
        with col_hujutu_lv_0:
            st.empty()
        with col_hujutu_name_0:
            st.write("名称")
        with col_hujutu_need_0:
            st.write("消費")
        with col_hujutu_other_0:
            st.write("効果")
        with col_hujutu_BASSS_0:
            st.write("ランク効果")
        # with col_hujutu_length_0:
        #     st.write("射程/形状")
        for i in range(skill_data["skill"][skills_name_list.index("アルケミスト")]["lv"]):
            i = i + 1
            col_hujutu_lv_1, col_hujutu_name_1, col_hujutu_need_1, col_hujutu_other_1, col_hujutu_BASSS_1 = st.columns([1,3,1,4,2])
            with col_hujutu_lv_1:
                st.number_input(f"賦術_lv_{i}", value=i, label_visibility="collapsed", disabled=True)
            with col_hujutu_name_1:
                hujutu_list_now = [" "] + [data["name"] for data in hujutu_list if data["required_lv"]<=i]
                hujutu = st.selectbox(f"賦術_{i}", options=hujutu_list_now, label_visibility="collapsed", key=f"alchemist_{(i-1)}")
                hujutu_list_buffer.append(hujutu)
            with col_hujutu_need_1:
                st.text_input(f"賦術必要_{i}", value=(hujutu_list[[data["name"] for data in hujutu_list].index(hujutu)]["color"] if hujutu != " " else ""), label_visibility="collapsed")
            with col_hujutu_other_1:
                st.text_input(f"賦術効果_{i}", value=(hujutu_list[[data["name"] for data in hujutu_list].index(hujutu)]["explanation"] if hujutu != " " else ""), label_visibility="collapsed")
            with col_hujutu_BASSS_1:
                st.text_input(f"賦術カード効果_{i}", value=(hujutu_list[[data["name"] for data in hujutu_list].index(hujutu)]["rank"] if hujutu != " " else ""), label_visibility="collapsed")
            # with col_hujutu_length_1:
            #     st.text_input(f"賦術射程形状_{i}", value=(hujutu_list[hujutu_list_now.index(hujutu)-1]["length"] if hujutu != " " else ""), label_visibility="collapsed")
    other_skill_dict["alchemist"] = hujutu_list_buffer

#相域
if skill_data["skill"][skills_name_list.index("ジオマンサー")]["lv"] > 0:
    souiki_list_buffer = []
    with st.expander("相域"):
        for i in range(skill_data["skill"][skills_name_list.index("ジオマンサー")]["lv"]):
            i = i + 1
            col_souiki_lv, col_souiki_name, col_souiki_need, col_souiki_other = st.columns([1,3.5,1.5,5])
            with col_souiki_lv:
                st.number_input(f"相域lv_{i}", value=i, label_visibility="collapsed", disabled=True)
            with col_souiki_name:
                souiki_list_now = [" "] + [data["name"] for data in souiki_list if data["required_lv"]<=i]
                souiki = st.selectbox(f"相域_{i}", options=souiki_list_now, label_visibility="collapsed", key=f"geomancer_{(i-1)}")
                souiki_list_buffer.append(souiki)
            with col_souiki_need:
                st.text_input(f"相域必要_{i}", value=(souiki_list[[data["name"] for data in souiki_list].index(souiki)]["meimyaku"] if souiki != " " else ""), label_visibility="collapsed")
            with col_souiki_other:
                st.text_input(f"相域効果_{i}", value=(souiki_list[[data["name"] for data in souiki_list].index(souiki)]["explanation"] if souiki != " " else ""), label_visibility="collapsed")
    other_skill_dict["geomancer"] = souiki_list_buffer

#鼓咆・陣率
if skill_data["skill"][skills_name_list.index("ウォーリーダー")]["lv"] > 0:
    kohou_list_buffer = []
    with st.expander("鼓咆・陣率"):
        if "鼓咆陣率追加I" in st.session_state.ability_mode:
            add_kohou = 1
        elif "鼓咆陣率追加II" in st.session_state.ability_mode:
            add_kohou = 2
        elif "鼓咆陣率追加II" in st.session_state.ability_mode:
            add_kohou = 3
        else:
            add_kohou = 0
        for i in range(add_kohou):
            i = i + 1
            col_kohou_lv, col_kohou_name, col_kohou_jinki, col_kohou_other = st.columns([1,4,1,5])
            with col_kohou_lv:
                st.text_input(f"追加鼓咆lv_{i}", value="追", label_visibility="collapsed", disabled=True)
            with col_kohou_name:
                kohou_list_now = [" "] + [data["name"] for data in kohou_list if data["required_lv"] <= skill_data["skill"][skills_name_list.index("ウォーリーダー")]["lv"]]
                kohou = st.selectbox(f"追加鼓咆_{i}", options=kohou_list_now, label_visibility="collapsed", key=f"add_war_leader_{(i-1)}")
                kohou_list_buffer.append(kohou)
            with col_kohou_jinki:
                st.text_input(f"追加鼓咆陣気_{i}", value=(kohou_list[[data["name"] for data in kohou_list].index(kohou)]["jinki"] if kohou != " " else ""), label_visibility="collapsed")
            with col_kohou_other:
                st.text_input(f"追加鼓咆効果_{i}", value=(kohou_list[[data["name"] for data in kohou_list].index(kohou)]["explanation"] if kohou != " " else ""), label_visibility="collapsed")
        other_skill_dict["add_war_leader"] = kohou_list_buffer
        kohou_list_buffer = []
        for i in range(skill_data["skill"][skills_name_list.index("ウォーリーダー")]["lv"]):
            i = i + 1
            col_kohou_lv, col_kohou_name, col_kohou_jinki, col_kohou_other = st.columns([1,4,1,5])
            with col_kohou_lv:
                st.number_input(f"鼓咆lv_{i}", value=i, label_visibility="collapsed", disabled=True)
            with col_kohou_name:
                kohou_list_now = [" "] + [data["name"] for data in kohou_list if data["required_lv"]<=i]
                kohou = st.selectbox(f"鼓咆_{i}", options=kohou_list_now, label_visibility="collapsed", key=f"war_leader_{(i-1)}")
                kohou_list_buffer.append(kohou)
            with col_kohou_jinki:
                st.text_input(f"鼓咆陣気_{i}", value=(kohou_list[[data["name"] for data in kohou_list].index(kohou)]["jinki"] if kohou != " " else ""), label_visibility="collapsed")
            with col_kohou_other:
                st.text_input(f"鼓咆効果_{i}", value=(kohou_list[[data["name"] for data in kohou_list].index(kohou)]["explanation"] if kohou != " " else ""), label_visibility="collapsed")
    other_skill_dict["war_leader"] = kohou_list_buffer

#操気
if skill_data["skill"][skills_name_list.index("ダークハンター")]["lv"] > 0:
    souki_list_buffer = []
    with st.expander("操気"):
        for i in range(skill_data["skill"][skills_name_list.index("ダークハンター")]["lv"]):
            i = i + 1
            col_souki_lv, col_souki_name, col_souki_hp, col_souki_other = st.columns([1,4,1,5])
            with col_souki_lv:
                st.number_input(f"操気lv_{i}", value=i, label_visibility="collapsed", disabled=True)
            with col_souki_name:
                souki_list_now = [" "] + [data["name"] for data in souki_list if data["required_lv"]<=i]
                souki = st.selectbox(f"操気_{i}", options=souki_list_now, label_visibility="collapsed", key=f"dark_hunter_{(i-1)}")
                souki_list_buffer.append(souki)
            with col_souki_hp:
                st.text_input(f"操気HP_{i}", value=(souki_list[[data["name"] for data in souki_list].index(souki)]["hp"] if souki != " " else ""), label_visibility="collapsed")
            with col_souki_other:
                st.text_input(f"操気効果_{i}", value=(souki_list[[data["name"] for data in souki_list].index(souki)]["explanation"] if souki != " " else ""), label_visibility="collapsed")
    other_skill_dict["dark_hunter"] = souki_list_buffer

#魔装
if skill_data["skill"][skills_name_list.index("フィジカルマスター")]["lv"] > 0:
    masou_list_buffer = []
    with st.expander("魔装"):
        for i in range(skill_data["skill"][skills_name_list.index("フィジカルマスター")]["lv"]):
            i = i + 1
            col_masou_lv, col_masou_name, col_masou_other = st.columns([1,4,6])
            with col_masou_lv:
                st.number_input(f"魔装lv_{i}", value=i, label_visibility="collapsed", disabled=True)
            with col_masou_name:
                masou_list_now = [" "] + [data["name"] for data in masou_list if data["required_lv"]<=i]
                masou = st.selectbox(f"魔装_{i}", options=masou_list_now, label_visibility="collapsed", key=f"physical_master_{(i-1)}")
                masou_list_buffer.append(masou)
            with col_masou_other:
                st.text_input(f"魔装効果_{i}", value=(masou_list[[data["name"] for data in masou_list].index(masou)]["explanation"] if masou != " " else ""), label_visibility="collapsed")
    other_skill_dict["physical_master"] = masou_list_buffer

#占瞳
if skill_data["skill"][skills_name_list.index("ミスティック")]["lv"] > 0:
    sendou_list_buffer = []
    with st.expander("占瞳"):
        for i in range(skill_data["skill"][skills_name_list.index("ミスティック")]["lv"]):
            i = i + 1
            col_sendou_lv, col_sendou_name, col_sendou_other = st.columns([1,4,6])
            with col_sendou_lv:
                st.number_input(f"占瞳lv_{i}", value=i, label_visibility="collapsed", disabled=True)
            with col_sendou_name:
                sendou_list_now = [" "] + [data["name"] for data in sendou_list if data["required_lv"]<=i]
                sendou = st.selectbox(f"占瞳_{i}", options=sendou_list_now, label_visibility="collapsed", key=f"mystic_{(i-1)}")
                sendou_list_buffer.append(sendou)
            with col_sendou_other:
                st.text_input(f"占瞳説明_{i}", value=(sendou_list[[data["name"] for data in sendou_list].index(sendou)]["explanation"] if sendou != " " else ""), label_visibility="collapsed")
            col_sendou_lv, col_sendou_effect = st.columns([1,10])
            with col_sendou_effect:
                st.text_input(f"占瞳効果_{i}", value=(sendou_list[[data["name"] for data in sendou_list].index(sendou)]["effect"] if sendou != " " else ""), label_visibility="collapsed")
    other_skill_dict["mystic"] = sendou_list_buffer

#呪印
if skill_data["skill"][skills_name_list.index("アーティザン")]["lv"] > 0:
    juin_list_buffer = []
    with st.expander("呪印"):
        for i in range(skill_data["skill"][skills_name_list.index("アーティザン")]["lv"]):
            i = i + 1
            col_juin_lv, col_juin_name, col_juin_hp, col_juin_other = st.columns([1,3,2,5])
            with col_juin_lv:
                st.number_input(f"呪印lv_{i}", value=i, label_visibility="collapsed", disabled=True)
            with col_juin_name:
                juin_list_now = [" "] + [data["name"] for data in juin_list if data["required_lv"]<=i]
                juin = st.selectbox(f"呪印_{i}", options=juin_list_now, label_visibility="collapsed", key=f"artisan_{(i-1)}")
                juin_list_buffer.append(juin)
            with col_juin_hp:
                st.text_input(f"呪印対象_{i}", value=(juin_list[[data["name"] for data in juin_list].index(juin)]["target"] if juin != " " else ""), label_visibility="collapsed")
            with col_juin_other:
                st.text_input(f"呪印効果_{i}", value=(juin_list[[data["name"] for data in juin_list].index(juin)]["explanation"] if juin != " " else ""), label_visibility="collapsed")
    other_skill_dict["artisan"] = juin_list_buffer

#貴格
if skill_data["skill"][skills_name_list.index("アリストクラシー")]["lv"] > 0:
    kikaku_list_buffer = []
    with st.expander("貴格"):
        for i in range(skill_data["skill"][skills_name_list.index("アリストクラシー")]["lv"]):
            i = i + 1
            col_kikaku_lv, col_kikaku_name, col_kikaku_other = st.columns([1,4,6])
            with col_kikaku_lv:
                st.number_input(f"貴格lv_{i}", value=i, label_visibility="collapsed", disabled=True)
            with col_kikaku_name:
                kikaku_list_now = [" "] + [data["name"] for data in kikaku_list if data["required_lv"]<=i]
                kikaku = st.selectbox(f"貴格_{i}", options=kikaku_list_now, label_visibility="collapsed", key=f"aristocracy_{(i-1)}")
                kikaku_list_buffer.append(kikaku)
            with col_kikaku_other:
                st.text_input(f"貴格効果_{i}", value=(kikaku_list[[data["name"] for data in kikaku_list].index(kikaku)]["explanation"] if kikaku != " " else ""), label_visibility="collapsed")
    other_skill_dict["aristocracy"] = kikaku_list_buffer

#名誉点
with st.expander("名誉点"):
    honor_list = [["", 0, ""],[]]
    col_honor_name, col_honor_point, col_honor_other = st.columns([2.5,1,5])
    with col_honor_name:
        st.write("名誉アイテム")
    with col_honor_point:
        st.write("点数")
    with col_honor_other:
        st.write("メモ")
    with col_honor_name:
        honor_list[0][0] = st.text_input("冒険者ランク", placeholder="冒険者ランク", label_visibility="collapsed", key="honor_rank_0")
    with col_honor_point:
        honor_list[0][1] = rank_honor_point = int(st.number_input("冒険者ランク点数", step=1, label_visibility="collapsed", key="honor_rank_1") / 10)
    with col_honor_other:
        honor_list[0][2] = st.text_input("冒険者ランクメモ", placeholder="この点数の10分の1以下の点数消費は自動返還されます", label_visibility="collapsed", key="honor_rank_2")    
    honor_point_used = 0
    for i in range(st.session_state.honor_list_num):
        honor_list_buffer = []
        with col_honor_name:
            honor_list_buffer.append(st.text_input(f"名誉アイテム{i}", label_visibility="collapsed", key=f"honor_{i}_0"))
        with col_honor_point:
            honor_point = st.number_input(f"名誉点数{i}", step=1, label_visibility="collapsed", key=f"honor_{i}_1")
            honor_list_buffer.append(honor_point)
            honor_point_used += honor_point if honor_point > rank_honor_point else 0
        with col_honor_other:
            honor_list_buffer.append(st.text_input(f"名誉メモ{i}", label_visibility="collapsed", key=f"honor_{i}_2"))
        honor_list[1].append(honor_list_buffer)
    with st.container(horizontal_alignment="left", horizontal=True):
        st.button("増加", on_click=update_honor_list_num, args=(1,), key="honor_list_add")
        st.button("減少", on_click=update_honor_list_num, args=(-1,), key="honor_list_sub")
        st.write(f"##### 消費名誉点:{honor_point_used}")
        st.write(f"##### 所持名誉点:{(st.session_state.honor - honor_point_used)}")

#セッション履歴
with st.expander("セッション履歴"):
    col_history_date0, col_history_exp0, col_history_pinzoro0, col_history_money0, col_history_honor0, col_history_growth0, col_history_other0, col_history_fool0 = st.columns([1,1.2,0.8,1.2,0.9,1.5,2.5,0.3])
    with col_history_date0:
        st.write("日付")
    with col_history_exp0:
        st.write("経験点")
    with col_history_pinzoro0:
        st.write("1ゾロ")
    with col_history_money0:
        st.write("報酬")
    with col_history_honor0:
        st.write("名誉点")
    with col_history_growth0:
        st.write("成長")
    with col_history_other0:
        st.write("備考")
    history_list = []
    for i in range(st.session_state.history_list_num):
        history_list_buffer = []
        col_history_date1, col_history_exp1, col_history_pinzoro1, col_history_money1, col_history_honor1, col_history_growth1, col_history_other1, col_history_fool1 = st.columns([1,1.2,0.8,1.2,0.9,1.5,2.5,0.3])
        with col_history_date1:
            history_list_buffer.append(st.text_input(f"セッション履歴{i}日付", label_visibility="collapsed", key=f"history_{i}_0"))
        with col_history_exp1:
            history_list_buffer.append(st.number_input(f"セッション履歴{i}経験点", step=1, label_visibility="collapsed", on_change=update_history, key=f"history_{i}_1"))
        with col_history_pinzoro1:
            history_list_buffer.append(st.number_input(f"セッション履歴{i}ピンゾロ", step=1, label_visibility="collapsed", on_change=update_history, key=f"history_{i}_2"))
        with col_history_money1:
            history_list_buffer.append(st.number_input(f"セッション履歴{i}報酬", step=1, label_visibility="collapsed", on_change=update_history, key=f"history_{i}_3"))
        with col_history_honor1:
            history_list_buffer.append(st.number_input(f"セッション履歴{i}名誉点", step=1, label_visibility="collapsed", on_change=update_history, key=f"history_{i}_4"))
        with col_history_growth1:
            history_list_buffer.append(st.text_input(f"セッション履歴{i}成長", label_visibility="collapsed", on_change=update_history, key=f"history_{i}_5"))
        with col_history_other1:
            history_list_buffer.append(st.text_input(f"セッション履歴{i}備考", label_visibility="collapsed", key=f"history_{i}_6"))
        with col_history_fool1:
            history_list_buffer.append(st.checkbox(f"セッション履歴{i}学ばない", label_visibility="collapsed", on_change=update_history, key=f"history_{i}_7"))
        history_list.append(history_list_buffer)
    col_history_button, col_history_info = st.columns([1,8])
    with col_history_button:
        st.button("増加", on_click=update_history_list_num, args=(1,), key="history_list_add")
        st.button("減少", on_click=update_history_list_num, args=(-1,), key="history_list_sub")
    with col_history_info:
        st.info("""
            ※右のチェックボックスにチェックを入れると"学ばない"を適用します。\n
            ※成長欄の入力規則:(能力値の頭文字)(数値)で複数可　例) 器1敏2知34
            """)
    st.divider()
    #update_history()
    col_history_date2, col_history_exp2, col_history_pinzoro2, col_history_money2, col_history_honor2, col_history_growth2, col_history_other2, col_history_fool2 = st.columns([1,1.2,0.8,1.2,0.9,1.2,1.8,1.3])
    with col_history_date2:
        st.write(f"##### 合計")
    with col_history_exp2:
        st.text_input(f"セッション履歴経験点合計", value=st.session_state.exp, label_visibility="collapsed", disabled=True)
    with col_history_pinzoro2:
        st.text_input(f"セッション履歴ピンゾロ合計", value=st.session_state.pinzoro, label_visibility="collapsed", disabled=True)
    with col_history_money2:
        st.text_input(f"セッション履歴報酬合計", value=st.session_state.money, label_visibility="collapsed", disabled=True)
    with col_history_honor2:
        st.text_input(f"セッション履歴名誉点合計", value=st.session_state.honor, label_visibility="collapsed", disabled=True)
    with col_history_growth2:
        st.text_input(f"セッション履歴成長合計", value=sum(st.session_state.growth_list), label_visibility="collapsed", disabled=True)
    col_history_date3, col_history_exp3, col_history_other3 = st.columns([1.7,1.3,6.4])
    with col_history_other2:
        st.write("##### 総経験点")
    with col_history_fool2:
        st.text_input(f"セッション履歴総経験点", value=st.session_state.exp_all, label_visibility="collapsed", disabled=True)

#その他
with st.expander("その他メモ"):
    st.text_area("その他メモ", label_visibility="collapsed", key="memo_area")

save_data = {
    "pc_name":name_pc,
    "pl_name":name_pl,
    "race":[race__, race, feature],
    "age":age,
    "gender":gender,
    "born":[born__, born, [stats_list[0][0], stats_list[2][0], stats_list[4][0]]],
    "stats_list":stats_list,
    "stats_buf":[st.session_state.life_stats_list[0][2], st.session_state.life_stats_list[1][2], st.session_state.life_stats_list[2][2], st.session_state.life_stats_list[3][2]],
    "lv_list":dict(zip(skills_name_list, st.session_state.lv_list)),
    "faith":st.session_state.faith,
    "ability":st.session_state.ability_mode,
    "weapon_list":weapon_list,
    "armor_list":armor_list,
    "equipment_list":dict(zip(st.session_state.equipment_part_list, equipment_list)),
    "item_list":item_list,
    "other_stats_list":[st.session_state.move_power_buf, st.session_state.gunti_check, st.session_state.mamotiki_skill, st.session_state.mamotiki_buf, st.session_state.sensei_skill, st.session_state.sensei_buf],
    "language_list":all_language_list,
    "maryoku_list":maryoku_dict,
    "other_skill_list":other_skill_dict,
    "honor_list":honor_list,
    "history":history_list,
    "memo":st.session_state.memo_area
}

json_save = json.dumps(save_data, ensure_ascii=False, indent=4)
st.sidebar.download_button("保存", data=json_save, file_name="save_data.json", mime="application/json")

if st.sidebar.button("キャッシュのクリア"):
    st.cache_data.clear()
    st.rerun()

omake = st.text_input("(デバッグ用)変数名を入力")
if omake in locals():
    locals()[omake]
elif omake == "":
    st.empty()
else:
    st.write(f'変数:"{omake}"は存在しません')
    
omake2 = st.text_input("(デバッグ用)グローバル変数名を入力")
if omake2 == "":
    st.empty()
elif omake2 in st.session_state:
    st.session_state[omake2]
else:
    st.write(f'グローバル変数:"{omake2}"は存在しません')

# with st.expander("ゴミ", expanded=True):
#     st.number_input("testta", step=1, key="vital_buf_1", on_change=update_life_stats_list)
#     st.number_input("testa", step=1, key="hp_buf_1", on_change=update_life_stats_list)