import streamlit as st
import random
import os
import base64

# Налаштування сторінки під мобільні пристрої
st.set_page_config(page_title="Warspear Forge", page_icon="⚔️", layout="centered")

# Функція для конвертації картинки в base64 (щоб вставити прямо в HTML)
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# Оновлена стилізація для смартфонів
st.markdown(f"""
    <style>
    .main {{ background-color: #0e1117; }}
    
    /* Очищення метрик (статистики) */
    [data-testid="stMetric"] {{
        background-color: transparent !important;
        border: none !important;
        text-align: center;
    }}
    [data-testid="stMetricLabel"] {{ font-size: 14px !important; justify-content: center; }}
    [data-testid="stMetricValue"] {{ font-size: 20px !important; }}

    /* Кнопки великі для пальців */
    .stButton>button {{
        width: 100%;
        height: 3.5em;
        font-weight: bold;
        font-size: 18px;
        border-radius: 12px;
        margin-bottom: 10px;
    }}

    /* Контейнер зброї без зайвих рамок */
    .weapon-display {{
        text-align: center;
        padding: 10px;
        margin-top: -20px;
    }}

    /* Зірочки з малим інтервалом */
    .star-row {{
        display: flex;
        justify-content: center;
        gap: 2px; /* Мінімальний інтервал */
        margin-bottom: 10px;
        height: 40px;
    }}
    .star-img {{
        width: 35px; /* Збільшений розмір */
        height: 35px;
        object-fit: contain;
    }}
    
    .chance-text {{
        font-size: 18px;
        font-style: italic;
        margin-top: 10px;
    }}
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

# --- ВІДОБРАЖЕННЯ (ЗВЕРХУ) ---

# Вибір зброї зверху (компактно)
weapon_name = st.selectbox("Зброя", list(WEAPON_IMAGES.keys()), label_visibility="collapsed")

# Основний блок візуалізації
st.markdown('<div class="weapon-display">', unsafe_allow_html=True)

# Малюємо зірочки через HTML для контролю інтервалу
star_base64 = get_image_base64("star.png")
star_html = ""
if star_base64:
    for _ in range(st.session_state.level):
        star_html += f'<img src="data:image/png;base64,{star_base64}" class="star-img">'
else:
    star_html = "⭐" * st.session_state.level

st.markdown(f'<div class="star-row">{star_html}</div>', unsafe_allow_html=True)

# Картинка зброї
img_file = WEAPON_IMAGES.get(weapon_name)
if os.path.exists(img_file):
    st.image(img_file, width=180)
else:
    st.markdown(f"<h2>{weapon_name}</h2>", unsafe_allow_html=True)

# Рівень та Шанс
c_chance = CHANCES.get(st.session_state.level, 0)
chance_clr = '#2ecc71' if c_chance > 20 else '#e74c3c'
st.markdown(f"""
    <h1 style="font-size: 70px; color: #FFD700; margin: 0;">+{st.session_state.level}</h1>
    <div class="chance-text" style="color: {chance_clr};">Шанс успіху: {c_chance}%</div>
    </div>
""", unsafe_allow_html=True)

# Статистика посередині (компактно в один рядок)
st.write("")
s1, s2, s3 = st.columns(3)
s1.metric("Золото", f"{st.session_state.gold:,}")
s2.metric("Знаки", f"{st.session_state.signs:,}")
s3.metric("Спроби", st.session_state.att)

# --- КЕРУВАННЯ (ЗНИЗУ) ---
st.divider()
use_signs = st.toggle("Знаки незламності", value=True)

if st.button("🔥 ТОЧИТИ"):
    sharpen(use_signs)
    st.rerun()

if st.button("🚀 АВТО +10"):
    while st.session_state.level < 10:
        sharpen(use_signs)
    st.balloons()
    st.rerun()

if st.button("♻️ СКИНУТИ", type="secondary"):
    st.session_state.update({'level': 0, 'gold': 0, 'signs': 0, 'att': 0})
    st.rerun()
