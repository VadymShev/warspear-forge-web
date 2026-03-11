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
            # Додаємо унікальний ключ до скрипта, щоб він спрацьовував щоразу
            md = f"""
                <audio autoplay="true">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
            """
            st.components.v1.html(md, height=0)

# --- CSS СТИЛІЗАЦІЯ ---
st.markdown(f"""
    <style>
    .block-container {{ 
        padding-top: 3.5rem !important; 
        padding-bottom: 2rem !important;
        max-width: 500px !important;
    }}
    .main-forge-area {{ display: flex; flex-direction: row; align-items: center; justify-content: center; gap: 12px; margin-top: 10px; }}
    .level-container {{ display: flex; flex-direction: column; align-items: center; min-width: 70px; }}
    .level-display {{ font-size: 38px; color: #ffc107; font-weight: bold; line-height: 1; }}
    .chance-badge {{ font-size: 11px; background: #222; color: #00ff00; padding: 2px 6px; border-radius: 4px; margin-top: 4px; font-family: monospace; }}
    .weapon-box img {{ width: 85px !important; height: auto; }}
    .stars-box {{ display: flex; flex-direction: row; flex-wrap: wrap; width: 110px; gap: 2px; }}
    .star-img-fixed {{ width: 18px !important; height: 18px !important; }}
    
    .stButton>button {{ width: 100%; height: 3.2em; font-weight: bold; border-radius: 10px; }}
    .main-btn button {{ background-color: #0d6efd !important; color: white !important; height: 3.5em !important; }}
    .test-btn button {{ background-color: #dc3545 !important; color: white !important; font-size: 13px !important; }}
    .lvl-btn button {{ height: 2.5em !important; font-size: 12px !important; background-color: #f1f3f5 !important; color: #333 !important; border: 1px solid #dee2e6 !important; }}

    .stats-panel {{ text-align: center; background: #2b2d30; color: white; padding: 10px; border-radius: 10px; margin: 10px 0; border: 1px solid #444; }}
    </style>
    """, unsafe_allow_html=True)

# --- ШАНСИ ТА ЗБРОЯ ---
WEAPON_IMAGES = {
    "Меч": "sword.png", "Посох": "staff.png", "Дворучний меч": "greatsword.png",
    "Сокира": "axe.png", "Дворучна сокира": "greataxe.png", "Булава": "mace.png",
    "Дворучна булава": "maul.png", "Спис": "spear.png", "Кинджал": "dagger.png",
    "Лук": "bow.png", "Арбалет": "crossbow.png"
}
ONE_HANDED = ["Меч", "Сокира", "Булава", "Кинджал"]

def get_current_chances(weapon_name):
    chances = {0: 100.0, 1: 60.0, 2: 40.0, 3: 25.0, 4: 15.0, 5: 10.0, 6: 7.0, 7: 4.0, 8: 0.75, 9: 0.25}
    if weapon_name in ONE_HANDED:
        chances[8], chances[9] = 1.25, 0.5
    return chances

# --- СТАН ---
if 'level' not in st.session_state:
    st.session_state.update({
        'level': 0, 'gold_spent': 0, 'signs_spent': 0, 
        'spheres_spent': 0, 'att': 0, 'last_sound': None,
        'current_weapon': "Меч", 'best_res': 0
    })

def sharpen_step(use_signs):
    if st.session_state.level >= 10: return
    current_lvl = st.session_state.level
    chances = get_current_chances(st.session_state.current_weapon)
    chance = chances.get(current_lvl, 0.25)
    roll = random.uniform(0, 100)
    
    st.session_state.att += 1
    st.session_state.gold_spent += int(650 + (current_lvl * 104))
    st.session_state.spheres_spent += 1
    if use_signs: st.session_state.signs_spent += 1
    
    if roll <= chance:
        st.session_state.level += 1
        st.session_state.last_sound = "success"
    else:
        if use_signs or current_lvl <= 3:
            st.session_state.last_sound = None
        else:
            fail_type = random.choice(["stay", "down", "reset"])
            if fail_type == "down": st.session_state.level -= 1
            else: st.session_state.level = 0
            st.session_state.last_sound = "fail"

def run_mass_test(n):
    max_l = st.session_state.level
    start_lvl = st.session_state.level
    for _ in range(n):
        if st.session_state.level >= 10: break
        sharpen_step(False)
        if st.session_state.level > max_l: max_l = st.session_state.level
    st.session_state.best_res = max_l
    st.session_state.last_sound = "success" if st.session_state.level > start_lvl else "fail"

# --- ВІЗУАЛ ---
img_file = WEAPON_IMAGES.get(st.session_state.current_weapon)
star_64 = get_image_base64("star.png")
weapon_64 = get_image_base64(img_file)
sign_64 = get_image_base64("sign.png")
sphere_64 = get_image_base64("sphere.png")

chances_map = get_current_chances(st.session_state.current_weapon)
current_chance = chances_map.get(st.session_state.level, 0.25)

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

def update_weapon(): st.session_state.current_weapon = st.session_state.weapon_selector
st.selectbox("Вибір зброї:", options=list(WEAPON_IMAGES.keys()), 
             index=list(WEAPON_IMAGES.keys()).index(st.session_state.current_weapon),
             key="weapon_selector", on_change=update_weapon, label_visibility="collapsed")

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

total_gold = st.session_state.gold_spent + (st.session_state.signs_spent * p_sign) + (st.session_state.spheres_spent * p_sphere)
st.markdown(f"""
    <div class="stats-panel">
        <div style="display: flex; justify-content: space-around; align-items: center;">
            <div style="text-align: left;"><span style="font-size: 10px; opacity: 0.7;">СПРОБИ:</span><br><b>{st.session_state.att}</b></div>
            <div style="text-align: right;"><span style="font-size: 10px; opacity: 0.7;">ЗОЛОТО:</span><br><b style="color: #4ade80;">{total_gold:,} 💰</b></div>
        </div>
        {f'<div style="font-size: 12px; margin-top:5px; color:#ffc107;">Найкращий результат тесту: +{st.session_state.best_res}</div>' if st.session_state.best_res > 0 else ''}
    </div>
""", unsafe_allow_html=True)

use_signs = st.toggle("Використовувати Знаки Незламності", value=True)

# --- ЗВУКОВА ЛОГІКА (РЕНДЕРИТЬСЯ ТУТ) ---
if st.session_state.last_sound:
    play_sound(f"{st.session_state.last_sound}.mp3")
    st.session_state.last_sound = None

# --- КНОПКИ ДІЇ ---
c_main, c_auto10, c_reset = st.columns([2, 1, 1])
with c_main:
    st.markdown('<div class="main-btn">', unsafe_allow_html=True)
    if st.button("🔥 ТОЧИТИ"): sharpen_step(use_signs); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with c_auto10:
    if st.button("🚀 +10"):
        while st.session_state.level < 10:
            old_l = st.session_state.level
            sharpen_step(use_signs)
            if not use_signs and st.session_state.level < old_l: break
        st.balloons(); st.rerun()
with c_reset:
    if st.button("♻️"):
        st.session_state.update({'level':0, 'gold_spent':0, 'signs_spent':0, 'spheres_spent':0, 'att':0, 'best_res':0})
        st.rerun()

if not use_signs:
    st.caption("Масовий тест спроб (без знаків):")
    t1, t2, t3, t4 = st.columns(4)
    with t1:
        if st.button("1к", key="t1"): run_mass_test(1000); st.rerun()
    with t2:
        if st.button("5к", key="t2"): run_mass_test(5000); st.rerun()
    with t3:
        if st.button("10к", key="t3"): run_mass_test(10000); st.rerun()
    with t4:
        if st.button("50к", key="t4"): run_mass_test(50000); st.rerun()

if use_signs:
    st.caption("Авто-заточка до рівня:")
    l6, l7, l8, l9 = st.columns(4)
    for i, col in enumerate([l6, l7, l8, l9], 6):
        with col:
            st.markdown('<div class="lvl-btn">', unsafe_allow_html=True)
            if st.button(f"+{i}"):
                while st.session_state.level < i: sharpen_step(True)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# Додай це в кінці файлу streamlit_app.py
st.write("---")
st.markdown(
    '<div style="text-align:center">'
    '<img src="https://hitwebcounter.com/counter/counter.php?page=warspear_forge_sim&style=0007&nbdigits=5&type=page&initCount=0" title="Free Counter" Alt="web counter" border="0" />'
    '<p style="font-size:10px; opacity:0.5;">Счетчик посещений</p>'
    '</div>', 
    unsafe_allow_html=True
)
