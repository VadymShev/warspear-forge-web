import streamlit as st
import random
import os
import base64

# --- НАЛАШТУВАННЯ СТОРІНКИ ---
st.set_page_config(page_title="Warspear Forge Calc", page_icon="⚔️", layout="centered")

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# Функція для відтворення звуку .mp3 через HTML/JS
def play_sound(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <audio autoplay="true">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                """
            st.components.v1.html(md, height=0)

# --- СТИЛІЗАЦІЯ (CSS) ---
st.markdown(f"""
    <style>
    .block-container {{ padding-top: 3.5rem !important; }}
    .stApp {{ background-color: #f8f9fa; color: #333333; }}
    
    /* Статистика */
    [data-testid="stMetric"] {{
        background-color: transparent !important;
        padding: 0px !important;
        margin-bottom: -5px !important;
    }}
    [data-testid="stMetricLabel"] {{ font-size: 12px !important; color: #6c757d; justify-content: center; }}
    [data-testid="stMetricValue"] {{ font-size: 16px !important; color: #212529; text-align: center; }}

    /* Контейнер: Зброя та Зірки */
    .forge-container {{
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        gap: 20px;
        margin: 15px 0;
        width: 100%;
    }}
    
    .stars-box {{
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        justify-content: flex-start;
        align-content: center;
        width: 160px;
        gap: 2px;
        min-height: 70px;
    }}
    
    .star-img-fixed {{ width: 30px; height: 30px; object-fit: contain; }}

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

    /* Історія */
    .history-box {{
        background: white;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        max-height: 140px;
        overflow-y: auto;
        font-size: 13px;
        line-height: 1.4;
    }}
    
    hr {{ margin: 0.8rem 0 !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- ЛОГІКА ТА СТАН ---
if 'level' not in st.session_state:
    st.session_state.update({
        'level': 0, 'gold_spent': 0, 'signs_spent': 0, 
        'spheres_spent': 0, 'att': 0, 'last_sound': None,
        'history': []
    })

CHANCES = {0: 100.0, 1: 60.0, 2: 40.0, 3: 25.0, 4: 15.0, 5: 10.0, 6: 7.0, 7: 4.0, 8: 1.5, 9: 0.5}
WEAPON_IMAGES = {
    "Посох": "staff.png", "Меч": "sword.png", "Дворучний меч": "greatsword.png",
    "Сокира": "axe.png", "Дворучна сокира": "greataxe.png", "Булава": "mace.png",
    "Дворучна булава": "maul.png", "Спис": "spear.png", "Кинджал": "dagger.png",
    "Лук": "bow.png", "Арбалет": "crossbow.png"
}

def add_to_history(text):
    st.session_state.history.insert(0, text)
    if len(st.session_state.history) > 20:
        st.session_state.history.pop()

def sharpen(use_signs):
    if st.session_state.level >= 10: return
    
    st.session_state.att += 1
    st.session_state.gold_spent += int(650 + (st.session_state.level * 104))
    st.session_state.spheres_spent += 1
    if use_signs: 
        st.session_state.signs_spent += 1
    
    chance = CHANCES.get(st.session_state.level, 0.5)
    old_lvl = st.session_state.level
    
    if random.uniform(0, 100) <= chance:
        st.session_state.level += 1
        st.session_state.last_sound = "success"
        add_to_history(f"✅ +{old_lvl} ➡️ +{st.session_state.level}")
    else:
        if not use_signs and st.session_state.level > 3:
            st.session_state.level = 0
            st.session_state.last_sound = "fail" # Звук невдачі тільки при обнуленні
            add_to_history(f"❌ КРАХ: Предмет обнулився!")
        else:
            st.session_state.last_sound = None # Знаки врятували - звуку невдачі немає
            add_to_history(f"💨 Невдача: +{old_lvl} (збережено)")

# --- ВІДТВОРЕННЯ ЗВУКУ (.mp3) ---
if st.session_state.last_sound == "success":
    play_sound("success.mp3")
    st.session_state.last_sound = None
elif st.session_state.last_sound == "fail":
    play_sound("fail.mp3")
    st.session_state.last_sound = None

# --- ІНТЕРФЕЙС ---
weapon_name = st.selectbox("Оберіть предмет:", list(WEAPON_IMAGES.keys()))

img_file = WEAPON_IMAGES.get(weapon_name)
star_64 = get_image_base64("star.png")
sign_64 = get_image_base64("sign.png")
sphere_64 = get_image_base64("sphere.png")
weapon_64 = get_image_base64(img_file)

# Візуалізація
star_html = "".join([f'<img src="data:image/png;base64,{star_64}" class="star-img-fixed">' for _ in range(st.session_state.level)]) if star_64 else "⭐" * st.session_state.level
weapon_tag = f'<img src="data:image/png;base64,{weapon_64}" width="130">' if weapon_64 else f'<h3>{weapon_name}</h3>'

st.markdown(f"""
    <div class="forge-container">
        <div class="weapon-box">{weapon_tag}</div>
        <div class="stars-box">{star_html}</div>
    </div>
""", unsafe_allow_html=True)

st.markdown(f'<h1 style="text-align:center; font-size:60px; color:#ffc107; margin:0; line-height:1;">+{st.session_state.level}</h1>', unsafe_allow_html=True)

# Статистика
st.write("---")
m1, m2, m3 = st.columns(3)
def icon_metric(col, img_64, label, value):
    with col:
        if img_64: st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{img_64}" width="25"></div>', unsafe_allow_html=True)
        st.metric(label, value)

icon_metric(m1, sign_64, "Знаки", st.session_state.signs_spent)
icon_metric(m2, sphere_64, "Сфери", st.session_state.spheres_spent)
icon_metric(m3, None, "Спроби", st.session_state.att)

# Історія та Ціни
col_hist, col_prices = st.columns([1, 1])

with col_hist:
    st.caption("📜 Історія спроб")
    history_html = "".join([f"<div>{item}</div>" for item in st.session_state.history])
    st.markdown(f'<div class="history-box">{history_html}</div>', unsafe_allow_html=True)

with col_prices:
    st.caption("🛠️ Ціни та підсумок")
    price_sign = st.number_input("Ціна Знаку", value=2500, step=100, label_visibility="collapsed")
    price_sphere = st.number_input("Ціна Сфери", value=400, step=50, label_visibility="collapsed")
    total_cost = st.session_state.gold_spent + (st.session_state.signs_spent * price_sign) + (st.session_state.spheres_spent * price_sphere)
    st.markdown(f"<div style='background:#e9ecef; padding:5px; border-radius:5px; text-align:center; margin-top:5px;'><b>{total_cost:,} 💰</b></div>", unsafe_allow_html=True)

# Кнопки
st.write("")
use_signs = st.toggle("Знаки незламності", value=True)
c_res, c_auto, c_main = st.columns([1, 1, 2])

with c_res:
    if st.button("♻️"):
        st.session_state.update({'level':0, 'gold_spent':0, 'signs_spent':0, 'spheres_spent':0, 'att':0, 'last_sound':None, 'history':[]})
        st.rerun()
with c_auto:
    if st.button("🚀"):
        while st.session_state.level < 10: sharpen(use_signs)
        st.balloons(); st.rerun()
with c_main:
    if st.button("🔥 ТОЧИТИ"):
        sharpen(use_signs); st.rerun()
