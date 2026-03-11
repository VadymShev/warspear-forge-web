import streamlit as st
import random
import os
import base64

# --- НАЛАШТУВАННЯ СТОРІНКИ ---
st.set_page_config(page_title="Warspear Forge", page_icon="⚔️", layout="centered")

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

def play_sound(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>"""
            st.components.v1.html(md, height=0)

# --- СТИЛІЗАЦІЯ (УЛЬТРА-КОМПАКТ) ---
st.markdown(f"""
    <style>
    .block-container {{ 
        padding-top: 1rem !important; 
        padding-bottom: 0rem !important;
        padding-left: 0.5rem !important; 
        padding-right: 0.5rem !important; 
    }}
    
    .stApp {{ background-color: #f8f9fa; }}

    /*Forge-контейнер*/
    .forge-container {{ 
        display: flex; 
        flex-direction: row; 
        align-items: center; 
        justify-content: center; 
        gap: 8px; 
        margin-bottom: 0px; 
    }}
    
    .weapon-box img {{ width: 85px !important; height: auto; }}
    
    .stars-box {{ 
        display: flex; 
        flex-direction: row; 
        flex-wrap: wrap; 
        width: 110px; 
        gap: 2px; 
    }}
    
    .star-img-fixed {{ width: 20px !important; height: 20px !important; }}

    /* Кнопки в один ряд */
    div[data-testid="stHorizontalBlock"] {{
        gap: 5px !important;
    }}

    .stButton>button {{ 
        width: 100%; 
        height: 3em; 
        font-size: 13px !important; 
        padding: 0px !important;
    }}
    
    /* Окремий стиль для головної кнопки */
    .main-btn button {{
        background-color: #0d6efd !important;
        color: white !important;
    }}

    /* Компактна історія */
    .history-box {{ 
        background: white; 
        padding: 4px; 
        border-radius: 6px; 
        border: 1px solid #dee2e6; 
        max-height: 80px; 
        overflow-y: auto; 
        font-size: 11px; 
        margin-top: 5px;
    }}

    [data-testid="stMetricValue"] {{ font-size: 15px !important; }}
    [data-testid="stMetricLabel"] {{ font-size: 10px !important; }}
    
    /* Зменшення полів вводу */
    .stNumberInput input {{
        padding: 2px 5px !important;
        font-size: 12px !important;
    }}
    
    hr {{ margin: 0.3rem 0 !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- ЛОГІКА ТА СТАН ---
if 'level' not in st.session_state:
    st.session_state.update({
        'level': 0, 'gold_spent': 0, 'signs_spent': 0, 
        'spheres_spent': 0, 'att': 0, 'last_sound': None,
        'history': []
    })

CHANCES = {0: 100.0, 1: 60.0, 2: 40.0, 3: 25.0, 4: 15.0, 5: 10.0, 6: 7.0, 7: 4.0, 8: 0.75, 9: 0.25}
WEAPON_IMAGES = {
    "Посох": "staff.png", "Меч": "sword.png", "Дворучний меч": "greatsword.png",
    "Сокира": "axe.png", "Дворучна сокира": "greataxe.png", "Булава": "mace.png",
    "Дворучна булава": "maul.png", "Спис": "spear.png", "Кинджал": "dagger.png",
    "Лук": "bow.png", "Арбалет": "crossbow.png"
}

def add_to_history(text):
    st.session_state.history.insert(0, text)
    if len(st.session_state.history) > 10: st.session_state.history.pop()

def sharpen(use_signs):
    if st.session_state.level >= 10: return
    st.session_state.att += 1
    st.session_state.gold_spent += int(650 + (st.session_state.level * 104))
    st.session_state.spheres_spent += 1
    if use_signs: st.session_state.signs_spent += 1
    
    chance = CHANCES.get(st.session_state.level, 0.25)
    old_lvl = st.session_state.level
    roll = random.uniform(0, 100)
    
    if roll <= chance:
        st.session_state.level += 1
        st.session_state.last_sound = "success"
        add_to_history(f"✅ +{old_lvl}➡️+{st.session_state.level}")
    else:
        if use_signs or st.session_state.level <= 3:
            st.session_state.last_sound = None
            add_to_history(f"💨 Невдача +{old_lvl}")
        else:
            fail_type = random.choice(["stay", "down", "reset"])
            if fail_type == "stay":
                add_to_history(f"💨 Невдача +{old_lvl}")
            elif fail_type == "down":
                st.session_state.level -= 1
                st.session_state.last_sound = "fail"
                add_to_history(f"📉 Пониж. +{old_lvl}➡️+{st.session_state.level}")
            elif fail_type == "reset":
                st.session_state.level = 0
                st.session_state.last_sound = "fail"
                add_to_history(f"❌ КРАХ +{old_lvl}➡️0")

# --- ЗВУК ---
if st.session_state.last_sound:
    play_sound(f"{st.session_state.last_sound}.mp3")
    st.session_state.last_sound = None

# --- ІНТЕРФЕЙС ---
weapon_name = st.selectbox("Предмет:", list(WEAPON_IMAGES.keys()), label_visibility="collapsed")
img_file = WEAPON_IMAGES.get(weapon_name)
star_64 = get_image_base64("star.png")
sign_64 = get_image_base64("sign.png")
sphere_64 = get_image_base64("sphere.png")
weapon_64 = get_image_base64(img_file)

# Forge Block (Зброя + Зірки)
star_html = "".join([f'<img src="data:image/png;base64,{star_64}" class="star-img-fixed">' for _ in range(st.session_state.level)]) if star_64 else "⭐" * st.session_state.level
weapon_tag = f'<img src="data:image/png;base64,{weapon_64}">' if weapon_64 else f'<b>{weapon_name}</b>'

st.markdown(f'<div class="forge-container"><div class="weapon-box">{weapon_tag}</div><div class="stars-box">{star_html}</div><div style="font-size:35px; color:#ffc107; font-weight:bold; margin-left:5px;">+{st.session_state.level}</div></div>', unsafe_allow_html=True)

# Секція Ціни та Статистика (В РЯДОК)
st.write("---")
c1, c2, c3 = st.columns(3)

with c1:
    if sign_64: st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{sign_64}" width="20"></div>', unsafe_allow_html=True)
    p_sign = st.number_input("Ціна Знака", value=2500, step=100, label_visibility="collapsed")
    st.metric("Штук", st.session_state.signs_spent)

with c2:
    if sphere_64: st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{sphere_64}" width="20"></div>', unsafe_allow_html=True)
    p_sphere = st.number_input("Ціна Сфери", value=400, step=50, label_visibility="collapsed")
    st.metric("Штук", st.session_state.spheres_spent)

with c3:
    st.markdown('<div style="text-align:center; height:20px; font-size:12px; color:#6c757d;">Спроби</div>', unsafe_allow_html=True)
    st.metric("Всього", st.session_state.att)
    total = st.session_state.gold_spent + (st.session_state.signs_spent * p_sign) + (st.session_state.spheres_spent * p_sphere)
    st.markdown(f"<div style='background:#eee; font-size:10px; padding:2px; border-radius:4px; text-align:center;'><b>{total:,}💰</b></div>", unsafe_allow_html=True)

# Кнопки (В ОДИН РЯД)
st.write("")
use_signs = st.toggle("Знаки", value=True)
btn_col1, btn_col2, btn_col3 = st.columns([0.6, 0.6, 2])

with btn_col1:
    if st.button("♻️"):
        st.session_state.update({'level':0, 'gold_spent':0, 'signs_spent':0, 'spheres_spent':0, 'att':0, 'history':[]})
        st.rerun()

with btn_col2:
    if st.button("🚀"):
        while st.session_state.level < 10: sharpen(use_signs)
        st.balloons(); st.rerun()

with btn_col3:
    st.markdown('<div class="main-btn">', unsafe_allow_html=True)
    if st.button("🔥 ТОЧИТИ"):
        sharpen(use_signs); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Історія (Знизу, максимально вузька)
h_html = "".join([f"<span>{i} | </span>" for i in st.session_state.history])
st.markdown(f'<div class="history-box">{h_html}</div>', unsafe_allow_html=True)
