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

# --- СТИЛІЗАЦІЯ (CSS) ---
st.markdown(f"""
    <style>
    .block-container {{ padding-top: 1rem !important; padding-bottom: 0rem !important; }}
    .stApp {{ background-color: #f8f9fa; color: #333333; }}
    
    /* Статистика */
    [data-testid="stMetric"] {{
        background-color: transparent !important;
        padding: 0px !important;
        margin-bottom: -10px !important;
    }}
    [data-testid="stMetricLabel"] {{ font-size: 13px !important; color: #6c757d; justify-content: center; }}
    [data-testid="stMetricValue"] {{ font-size: 18px !important; color: #212529; text-align: center; }}

    /* Контейнер: Зброя та Зірки */
    .forge-container {{
        display: flex;
        flex-direction: row; /* Горизонтальне розташування */
        align-items: center;
        justify-content: center;
        gap: 20px;
        margin: 15px 0;
        width: 100%;
    }}
    
    /* ЗІРОЧКИ: Горизонтальний ряд з переносом */
    .stars-box {{
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;    /* Дозволяє переносити на новий ряд */
        justify-content: flex-start;
        align-content: center;
        width: 160px;       /* Обмежуємо ширину, щоб влазило рівно 5 зірок (30px * 5 + gap) */
        gap: 2px;
        min-height: 70px;
    }}
    
    .star-img-fixed {{
        width: 30px;
        height: 30px;
        object-fit: contain;
    }}

    /* Кнопки */
    .stButton>button {{
        width: 100%;
        height: 3.5em;
        font-weight: bold;
        border-radius: 12px;
    }}
    
    div[data-testid="stHorizontalBlock"] > div:last-child button {{
        background-color: #0d6efd !important;
        color: white !important;
        border: none !important;
    }}

    .stSelectbox label {{ color: #333333 !important; font-weight: bold !important; }}
    hr {{ margin: 0.5rem 0 !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- ЛОГІКА ---
if 'level' not in st.session_state:
    st.session_state.update({'level': 0, 'gold': 0, 'signs': 0, 'att': 0})

CHANCES = {0: 100.0, 1: 60.0, 2: 40.0, 3: 25.0, 4: 15.0, 5: 10.0, 6: 7.0, 7: 4.0, 8: 1.5, 9: 0.5}
WEAPON_IMAGES = {
    "Посох": "staff.png", "Меч": "sword.png", "Дворучний меч": "greatsword.png",
    "Сокира": "axe.png", "Дворучна сокира": "greataxe.png", "Булава": "mace.png",
    "Дворучна булава": "maul.png", "Спис": "spear.png", "Кинджал": "dagger.png",
    "Лук": "bow.png", "Арбалет": "crossbow.png"
}

def sharpen(use_signs):
    if st.session_state.level >= 10: return
    st.session_state.att += 1
    st.session_state.gold += int(650 + (st.session_state.level * 104))
    if use_signs: st.session_state.signs += 1
    
    chance = CHANCES.get(st.session_state.level, 0.5)
    if random.uniform(0, 100) <= chance:
        st.session_state.level += 1
    else:
        if not use_signs and st.session_state.level > 3:
            st.session_state.level = 0

# --- ІНТЕРФЕЙС ---

weapon_name = st.selectbox("Оберіть вашу зброю:", list(WEAPON_IMAGES.keys()))

img_file = WEAPON_IMAGES.get(weapon_name)
star_base64 = get_image_base64("star.png")

# Використовуємо один блок HTML для стабільного вирівнювання
star_html = ""
if star_base64:
    for _ in range(st.session_state.level):
        star_html += f'<img src="data:image/png;base64,{star_base64}" class="star-img-fixed">'
else:
    star_html = "⭐" * st.session_state.level

# Головний контейнер (Зброя + Зірки)
weapon_img_tag = f'<img src="data:image/png;base64,{get_image_base64(img_file)}" width="130">' if os.path.exists(img_file) else f'<h3>{weapon_name}</h3>'

st.markdown(f"""
    <div class="forge-container">
        <div class="weapon-box">{weapon_img_tag}</div>
        <div class="stars-box">{star_html}</div>
    </div>
""", unsafe_allow_html=True)

# Рівень та Шанс
c_chance = CHANCES.get(st.session_state.level, 0)
chance_clr = '#198754' if c_chance > 20 else '#dc3545'
st.markdown(f"""
    <div style="text-align: center;">
        <h1 style="font-size: 65px; color: #ffc107; margin: 0;">+{st.session_state.level}</h1>
        <p style="color: {chance_clr}; font-size: 16px; margin-bottom: 10px; font-weight: bold;">Ймовірність успіху: {c_chance}%</p>
    </div>
""", unsafe_allow_html=True)

# Статистика
s1, s2, s3 = st.columns(3)
s1.metric("Золото", f"{st.session_state.gold:,}")
s2.metric("Знаки", f"{st.session_state.signs:,}")
s3.metric("Спроби", st.session_state.att)

# Кнопки
st.divider()
use_signs = st.toggle("Використовувати знаки незламності", value=True)

c_res, c_auto, c_main = st.columns([1, 1, 2])
with c_res:
    if st.button("♻️"):
        st.session_state.update({'level': 0, 'gold': 0, 'signs': 0, 'att': 0})
        st.rerun()
with c_auto:
    if st.button("🚀"):
        while st.session_state.level < 10: sharpen(use_signs)
        st.balloons()
        st.rerun()
with c_main:
    if st.button("🔥 ТОЧИТИ"):
        sharpen(use_signs)
        st.rerun()
