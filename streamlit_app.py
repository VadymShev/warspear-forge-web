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
    .main-forge-area {{ display: flex; flex-direction: row; align-items: center; justify-content: center; gap: 12px; margin-top: 10px; }}
    .level-container {{ display: flex; flex-direction: column; align-items: center; min-width: 70px; }}
    .level-display {{ font-size: 38px; color: #ffc107; font-weight: bold; line-height: 1; }}
    .chance-badge {{ font-size: 11px; background: #222; color: #00ff00; padding: 2px 6px; border-radius: 4px; margin-top: 4px; font-family: monospace; }}
    .weapon-box img {{ width: 85px !important; height: auto; }}
    .stars-box {{ display: flex; flex-direction: row; flex-wrap: wrap; width: 110px; gap: 2px; }}
    .star-img-fixed {{ width: 18px !important; height: 18px !important; }}
    
    .stButton>button {{ width: 100%; height: 3.2em; font-weight: bold; border-radius: 10px; }}
    .main-btn button {{ background-color: #0d6efd !important; color: white !important; height: 3.5em !important; }}
    .test-btn button {{ background-color: #dc3545 !important; color: white !important; height: 3.5em !important; }}
    .lvl-btn button {{ height: 2.5em !important; font-size: 12px !important; background-color: #f1f3f5 !important; color: #333 !important; border: 1px solid #dee2e6 !important; }}

    .stats-panel {{ text-align: center; background: #2b2d30; color: white; padding: 10px; border-radius: 10px; margin: 10px 0; border: 1px solid #444; }}
    hr {{ margin: 0.5rem 0 !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- ДАНІ ТА ШАНСИ ---
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
        chances[8] = 1.25
        chances[9] = 0.5
    return chances

# --- ЛОГІКА СТАНУ ---
if 'level' not in st.session_state:
    st.session_state.update({
        'level': 0, 'gold_spent': 0, 'signs_spent': 0, 
        'spheres_spent': 0, 'att': 0, 'last_sound': None,
        'current_weapon': "Меч", 'best_res': 0
    })

def sharpen_logic(current_lvl, weapon_name, use_signs):
    chances = get_current_chances(weapon_name)
    chance = chances.get(current_lvl, 0.25)
    roll = random.uniform(0, 100)
    
    gold = int(650 + (current_lvl * 104))
    
    if roll <= chance:
        return current_lvl + 1, gold, True
    else:
        if use_signs or current_lvl <= 3:
            return current_lvl, gold, False
        else:
            fail_type = random.choice(["stay", "down", "reset"])
            if fail_type == "down": return current_lvl - 1, gold, False
            return 0, gold, False

def run_mass_test():
    max_lvl = 0
    for _ in range(50000):
        # Виконуємо одну спробу на поточному рівні
        new_lvl, gold, success = sharpen_logic(st.session_state.level, st.session_state.current_weapon, False)
        
        # Оновлюємо глобальну статистику
        st.session_state.att += 1
        st.session_state.gold_spent += gold
        st.session_state.spheres_spent += 1
        st.session_state.level = new_lvl
        
        if st.session_state.level > max_lvl:
            max_lvl = st.session_state.level
    
    st.session_state.best_res = max_lvl

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

# --- КНОПКИ ДІЇ ---
c_main, c_auto10, c_reset = st.columns([2, 1, 1])

with c_main:
    if use_signs:
        st.markdown('<div class="main-btn">', unsafe_allow_html=True)
        if st.button("🔥 ТОЧИТИ"): 
            lvl, g, s = sharpen_logic(st.session_state.level, st.session_state.current_weapon, True)
            st.session_state.level = lvl
            st.session_state.gold_spent += g
            st.session_state.att += 1
            st.session_state.spheres_spent += 1
            st.session_state.signs_spent += 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="test-btn">', unsafe_allow_html=True)
        if st.button("🎰 ТЕСТ 50к"): 
            run_mass_test()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

with c_auto10:
    if st.button("🚀 +10"):
        while st.session_state.level < 10:
            lvl, g, s = sharpen_logic(st.session_state.level, st.session_state.current_weapon, use_signs)
            st.session_state.level = lvl
            st.session_state.gold_spent += g
            st.session_state.att += 1
            st.session_state.spheres_spent += 1
            if use_signs: st.session_state.signs_spent += 1
            if not use_signs and (lvl == 0 or lvl < st.session_state.level): break 
        st.balloons(); st.rerun()

with c_reset:
    if st.button("♻️"):
        st.session_state.update({'level':0, 'gold_spent':0, 'signs_spent':0, 'spheres_spent':0, 'att':0, 'best_res':0})
        st.rerun()

# Швидка заточка (тільки зі знаками)
if use_signs:
    st.caption("Авто-заточка до рівня:")
    l6, l7, l8, l9 = st.columns(4)
    for i, col in enumerate([l6, l7, l8, l9], 6):
        with col:
            st.markdown('<div class="lvl-btn">', unsafe_allow_html=True)
            if st.button(f"+{i}"):
                while st.session_state.level < i:
                    lvl, g, s = sharpen_logic(st.session_state.level, st.session_state.current_weapon, True)
                    st.session_state.level = lvl
                    st.session_state.gold_spent += g
                    st.session_state.att += 1
                    st.session_state.spheres_spent += 1
                    st.session_state.signs_spent += 1
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
