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
        padding-top: 1rem !important; 
        padding-bottom: 2rem !important;
        padding-left: 0.5rem !important; 
        padding-right: 0.5rem !important; 
    }}
    
    .main-forge-area {{
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        gap: 12px;
        margin-top: 5px;
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
        font-size: 12px;
        background: #333;
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
    
    .star-img-fixed {{ width: 20px !important; height: 20px !important; }}

    .stButton>button {{ width: 100%; height: 3.5em; font-weight: bold; border-radius: 8px; }}
    
    /* Колір кнопки ТОЧИТИ */
    div[data-testid="stHorizontalBlock"] > div:first-child button {{
        background-color: #0d6efd !important;
        color: white !important;
    }}

    .total-gold-box {{
        text-align: center; 
        background: #2b2d30; 
        color: white;
        padding: 8px; 
        border-radius: 8px; 
        margin: 10px 0;
        border: 1px solid #444;
    }}
    
    hr {{ margin: 0.4rem 0 !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- ЛОГІКА ТА СТАН ---
if 'level' not in st.session_state:
    st.session_state.update({
        'level': 0, 'gold_spent': 0, 'signs_spent': 0, 
        'spheres_spent': 0, 'att': 0, 'last_sound': None,
        'history': [], 'weapon': "Меч"
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
    if len(st.session_state.history) > 5: st.session_state.history.pop()

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
        add_to_history(f"✅ +{st.session_state.level}")
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

# Завантаження картинок
img_file = WEAPON_IMAGES.get(st.session_state.weapon)
star_64 = get_image_base64("star.png")
sign_64 = get_image_base64("sign.png")
sphere_64 = get_image_base64("sphere.png")
weapon_64 = get_image_base64(img_file)

# --- 1. ВІЗУАЛ (РІВЕНЬ/ШАНС - ЗБРОЯ - ЗІРКИ) ---
current_chance = CHANCES.get(st.session_state.level, 0.25)
star_html = "".join([f'<img src="data:image/png;base64,{star_64}" class="star-img-fixed">' for _ in range(st.session_state.level)]) if star_64 else "⭐" * st.session_state.level
weapon_tag = f'<img src="data:image/png;base64,{weapon_64}">' if weapon_64 else "⚔️"

st.markdown(f"""
    <div class="main-forge-area">
        <div class="level-container">
            <div class="level-display">+{st.session_state.level}</div>
            <div class="chance-badge">{current_chance}%</div>
        </div>
        <div class="weapon-box">{weapon_tag}</div>
        <div class="stars-box">{star_html}</div>
    </div>
""", unsafe_allow_html=True)

# --- 2. ЕКОНОМІКА (ЗНАКИ ТА СФЕРИ) ---
st.write("---")
col_s1, col_s2 = st.columns(2)
with col_s1:
    if sign_64: st.image(f"data:image/png;base64,{sign_64}", width=22)
    p_sign = st.number_input("Ціна Знака", value=2500, step=100, label_visibility="collapsed", key="ps")
    st.caption(f"Витрачено: **{st.session_state.signs_spent}**")

with col_s2:
    if sphere_64: st.image(f"data:image/png;base64,{sphere_64}", width=22)
    p_sphere = st.number_input("Ціна Сфери", value=400, step=50, label_visibility="collapsed", key="psp")
    st.caption(f"Витрачено: **{st.session_state.spheres_spent}**")

# --- 3. ПІДСУМОК ТА ГАЛОЧКА ---
total_gold = st.session_state.gold_spent + (st.session_state.signs_spent * p_sign) + (st.session_state.spheres_spent * p_sphere)
st.markdown(f"""
    <div class="total-gold-box">
        <span style="font-size: 11px; opacity: 0.8;">Всього витрачено золота:</span><br>
        <b style="font-size: 20px; color: #4ade80;">{total_gold:,} 💰</b>
    </div>
""", unsafe_allow_html=True)

use_signs = st.toggle("Використовувати Знаки Незламності", value=True)

# --- 4. КНОПКИ (ТОЧИТИ, +10, СКИНУТИ) ---
st.write("")
c_main, c_auto, c_reset = st.columns([2, 1, 1])

if c_main.button("🔥 ТОЧИТИ"):
    sharpen(use_signs); st.rerun()

if c_auto.button("🚀 +10"):
    while st.session_state.level < 10: sharpen(use_signs)
    st.balloons(); st.rerun()

if c_reset.button("♻️"):
    st.session_state.update({'level':0, 'gold_spent':0, 'signs_spent':0, 'spheres_spent':0, 'att':0, 'history':[]})
    st.rerun()

# --- 5. ВИБІР ЗБРОЇ (В САМОМУ НИЗУ) ---
st.write("---")
st.session_state.weapon = st.selectbox("Змінити предмет:", list(WEAPON_IMAGES.keys()))
st.caption(f"Спроб: {st.session_state.att} | Історія: {' > '.join(st.session_state.history[:3])}")
