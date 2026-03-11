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

# --- CSS СТИЛІЗАЦІЯ ---
st.markdown(f"""
    <style>
    .block-container {{ 
        padding-top: 3.5rem !important; 
        padding-bottom: 2rem !important;
        padding-left: 0.5rem !important; 
        padding-right: 0.5rem !important; 
        max-width: 500px !important;
    }}
    
    .main-forge-area {{
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        gap: 12px;
        margin-top: 10px;
    }}
    
    .level-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 70px;
    }}

    .level-display {{
        font-size: 38px;
        color: #ffc107;
        font-weight: bold;
        line-height: 1;
    }}
    
    .chance-badge {{
        font-size: 11px;
        background: #222;
        color: #00ff00;
        padding: 2px 6px;
        border-radius: 4px;
        margin-top: 4px;
        font-family: monospace;
    }}
    
    .weapon-box img {{ width: 85px !important; height: auto; }}
    
    .stars-box {{
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        width: 110px;
        gap: 2px;
    }}
    
    .star-img-fixed {{ width: 18px !important; height: 18px !important; }}

    .stButton>button {{ width: 100%; height: 3.5em; font-weight: bold; border-radius: 10px; }}
    
    div[data-testid="stHorizontalBlock"] > div:first-child button {{
        background-color: #0d6efd !important;
        color: white !important;
        border: none;
    }}

    .stats-panel {{
        text-align: center; 
        background: #2b2d30; 
        color: white;
        padding: 10px; 
        border-radius: 10px; 
        margin: 10px 0;
        border: 1px solid #444;
    }}
    
    hr {{ margin: 0.5rem 0 !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- ЛОГІКА ТА СТАН ---
CHANCES = {0: 100.0, 1: 60.0, 2: 40.0, 3: 25.0, 4: 15.0, 5: 10.0, 6: 7.0, 7: 4.0, 8: 0.75, 9: 0.25}
WEAPON_IMAGES = {
    "Меч": "sword.png", "Посох": "staff.png", "Дворучний меч": "greatsword.png",
    "Сокира": "axe.png", "Дворучна сокира": "greataxe.png", "Булава": "mace.png",
    "Дворучна булава": "maul.png", "Спис": "spear.png", "Кинджал": "dagger.png",
    "Лук": "bow.png", "Арбалет": "crossbow.png"
}

if 'level' not in st.session_state:
    st.session_state.update({
        'level': 0, 'gold_spent': 0, 'signs_spent': 0, 
        'spheres_spent': 0, 'att': 0, 'last_sound': None,
        'current_weapon': "Меч"
    })

def sharpen(use_signs):
    if st.session_state.level >= 10: return
    st.session_state.att += 1
    st.session_state.gold_spent += int(650 + (st.session_state.level * 104))
    st.session_state.spheres_spent += 1
    if use_signs: st.session_state.signs_spent += 1
    
    chance = CHANCES.get(st.session_state.level, 0.25)
    roll = random.uniform(0, 100)
    
    if roll <= chance:
        st.session_state.level += 1
        st.session_state.last_sound = "success"
    else:
        if use_signs or st.session_state.level <= 3:
            st.session_state.last_sound = None
        else:
            fail_type = random.choice(["stay", "down", "reset"])
            if fail_type == "down":
                st.session_state.level -= 1
                st.session_state.last_sound = "fail"
            elif fail_type == "reset":
                st.session_state.level = 0
                st.session_state.last_sound = "fail"

# --- ВІДТВОРЕННЯ ЗВУКУ ---
if st.session_state.last_sound:
    play_sound(f"{st.session_state.last_sound}.mp3")
    st.session_state.last_sound = None

# Ресурси
img_file = WEAPON_IMAGES.get(st.session_state.current_weapon)
star_64 = get_image_base64("star.png")
sign_64 = get_image_base64("sign.png")
sphere_64 = get_image_base64("sphere.png")
weapon_64 = get_image_base64(img_file)

# --- 1. ВІЗУАЛ ---
current_chance = CHANCES.get(st.session_state.level, 0.25)
star_html = "".join([f'<img src="data:image/png;base64,{star_64}" class="star-img-fixed">' for _ in range(st.session_state.level)]) if star_64 else "⭐" * st.session_state.level
weapon_tag = f'<img src="data:image/png;base64,{weapon_64}">' if weapon_64 else "⚔️"

st.markdown(f"""
    <div class="main-forge-area">
        <div class="level-container">
            <div class="level-display">+{st.session_state.level}</div>
            <div class="chance-badge">шанс {current_chance}%</div>
        </div>
        <div class="weapon-box">{weapon_tag}</div>
        <div class="stars-box">{star_html}</div>
    </div>
""", unsafe_allow_html=True)

# --- 2. ЕКОНОМІКА ---
st.write("---")
col_s1, col_s2 = st.columns(2)
with col_s1:
    if sign_64: st.image(f"data:image/png;base64,{sign_64}", width=20)
    p_sign = st.number_input("Ціна Знака", value=2500, step=100, label_visibility="collapsed", key="ps")
    st.caption(f"Використано: **{st.session_state.signs_spent}**")

with col_s2:
    if sphere_64: st.image(f"data:image/png;base64,{sphere_64}", width=20)
    p_sphere = st.number_input("Ціна Сфери", value=400, step=50, label_visibility="collapsed", key="psp")
    st.caption(f"Використано: **{st.session_state.spheres_spent}**")

# --- 3. ПІДСУМОК ---
total_gold = st.session_state.gold_spent + (st.session_state.signs_spent * p_sign) + (st.session_state.spheres_spent * p_sphere)
st.markdown(f"""
    <div class="stats-panel">
        <div style="display: flex; justify-content: space-around; align-items: center;">
            <div style="text-align: left;">
                <span style="font-size: 10px; opacity: 0.7; text-transform: uppercase;">Спроби:</span><br>
                <b style="font-size: 18px; color: #fff;">{st.session_state.att}</b>
            </div>
            <div style="text-align: right;">
                <span style="font-size: 10px; opacity: 0.7; text-transform: uppercase;">Витрати золото:</span><br>
                <b style="font-size: 18px; color: #4ade80;">{total_gold:,} 💰</b>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

use_signs = st.toggle("Використовувати Знаки Незламності", value=True)

# --- 4. КНОПКИ ДІЇ ---
st.write("")
c_main, c_auto, c_reset = st.columns([2, 1, 1])

if c_main.button("🔥 ТОЧИТИ"):
    sharpen(use_signs)
    st.rerun()

if c_auto.button("🚀 +10"):
    while st.session_state.level < 10: sharpen(use_signs)
    st.balloons()
    st.rerun()

if c_reset.button("♻️"):
    st.session_state.update({'level':0, 'gold_spent':0, 'signs_spent':0, 'spheres_spent':0, 'att':0, 'last_sound': None})
    st.rerun()

# --- 5. НАЛАШТУВАННЯ ЗБРОЇ (НИЗ) ---
st.write("---")

# Функція для миттєвого оновлення
def update_weapon():
    st.session_state.current_weapon = st.session_state.weapon_selector

st.selectbox(
    "Змінити малюнок предмета:", 
    options=list(WEAPON_IMAGES.keys()), 
    index=list(WEAPON_IMAGES.keys()).index(st.session_state.current_weapon),
    key="weapon_selector",
    on_change=update_weapon
)
