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

# --- УЛЬТРА-КОМПАКТНИЙ CSS ---
st.markdown(f"""
    <style>
    .block-container {{ 
        padding-top: 1rem !important; 
        padding-bottom: 0rem !important;
        padding-left: 0.5rem !important; 
        padding-right: 0.5rem !important; 
    }}
    
    /* Контейнер головного візуала: [Рівень] [Зброя] [Зірки] */
    .main-forge-area {{
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        gap: 15px;
        margin: 10px 0;
    }}
    
    .level-display {{
        font-size: 40px;
        color: #ffc107;
        font-weight: bold;
        min-width: 60px;
        text-align: right;
    }}
    
    .weapon-box img {{ width: 90px !important; height: auto; }}
    
    .stars-box {{
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        width: 110px;
        gap: 2px;
    }}
    
    .star-img-fixed {{ width: 20px !important; height: 20px !important; }}

    /* Кнопки в ряд */
    .stButton>button {{ 
        width: 100%; 
        height: 3.5em; 
        font-weight: bold;
    }}
    
    /* Стиль для кнопки ТОЧИТИ */
    div[data-testid="stHorizontalBlock"] > div:first-child button {{
        background-color: #0d6efd !important;
        color: white !important;
    }}

    /* Поля вводу */
    .stNumberInput input {{
        padding: 2px 5px !important;
    }}
    
    hr {{ margin: 0.5rem 0 !important; }}
    
    .history-text {{
        font-size: 11px;
        color: #6c757d;
        text-align: center;
    }}
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
    if len(st.session_state.history) > 5: st.session_state.history.pop()

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
                add_to_history(f"📉 -1 рівень")
            elif fail_type == "reset":
                st.session_state.level = 0
                st.session_state.last_sound = "fail"
                add_to_history(f"❌ КРАХ +0")

# --- ВІДТВОРЕННЯ ЗВУКУ ---
if st.session_state.last_sound:
    play_sound(f"{st.session_state.last_sound}.mp3")
    st.session_state.last_sound = None

# --- 1. ВИБІР ЗБРОЇ (ЗВЕРХУ) ---
weapon_name = st.selectbox("Оберіть предмет:", list(WEAPON_IMAGES.keys()), label_visibility="collapsed")

# Завантаження ресурсів
img_file = WEAPON_IMAGES.get(weapon_name)
star_64 = get_image_base64("star.png")
sign_64 = get_image_base64("sign.png")
sphere_64 = get_image_base64("sphere.png")
weapon_64 = get_image_base64(img_file)

# --- 2. ВІЗУАЛ (РІВЕНЬ - ЗБРОЯ - ЗІРКИ) ---
star_html = "".join([f'<img src="data:image/png;base64,{star_64}" class="star-img-fixed">' for _ in range(st.session_state.level)]) if star_64 else "⭐" * st.session_state.level
weapon_tag = f'<img src="data:image/png;base64,{weapon_64}">' if weapon_64 else "⚔️"

st.markdown(f"""
    <div class="main-forge-area">
        <div class="level-display">+{st.session_state.level}</div>
        <div class="weapon-box">{weapon_tag}</div>
        <div class="stars-box">{star_html}</div>
    </div>
""", unsafe_allow_html=True)

# --- 3. ЗНАКИ ТА СФЕРИ (ЦІНА ТА КІЛЬКІСТЬ) ---
st.write("---")
col_s1, col_s2 = st.columns(2)

with col_s1:
    if sign_64: st.image(f"data:image/png;base64,{sign_64}", width=25)
    p_sign = st.number_input("Ціна Знака", value=2500, step=100, label_visibility="collapsed", key="ps")
    st.caption(f"Витрачено: **{st.session_state.signs_spent}** шт.")

with col_s2:
    if sphere_64: st.image(f"data:image/png;base64,{sphere_64}", width=25)
    p_sphere = st.number_input("Ціна Сфери", value=400, step=50, label_visibility="collapsed", key="psp")
    st.caption(f"Витрачено: **{st.session_state.spheres_spent}** шт.")

# --- 4. ЗОЛОТО ТА ГАЛОЧКА ---
total_gold = st.session_state.gold_spent + (st.session_state.signs_spent * p_sign) + (st.session_state.spheres_spent * p_sphere)
st.markdown(f"""
    <div style="text-align: center; background: #e9ecef; padding: 5px; border-radius: 8px; margin-bottom: 5px;">
        <span style="font-size: 12px; color: #666;">Загальні витрати:</span><br>
        <b style="font-size: 18px; color: #198754;">{total_gold:,} 💰</b>
    </div>
""", unsafe_allow_html=True)

use_signs = st.toggle("Використовувати Знаки Незламності", value=True)

# --- 5. КНОПКИ (В КІНЦІ) ---
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

# Маленька історія в самому низу
st.markdown(f'<p class="history-text">{" | ".join(st.session_state.history)}</p>', unsafe_allow_html=True)
