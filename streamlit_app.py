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

def icon_metric(col, img_64, label, value):
    with col:
        if img_64: 
            st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{img_64}" width="22"></div>', unsafe_allow_html=True)
        st.metric(label, value)

# --- СТИЛІЗАЦІЯ (ОПТИМІЗАЦІЯ ПІД МОБІЛЬНІ) ---
st.markdown(f"""
    <style>
    /* Максимальне звуження бокових відступів */
    .block-container {{ 
        padding-top: 2rem !important; 
        padding-left: 0.5rem !important; 
        padding-right: 0.5rem !important; 
        max-width: 100% !important;
    }}
    
    .stApp {{ background-color: #f8f9fa; }}

    /* Компактний Forge-контейнер */
    .forge-container {{ 
        display: flex; 
        flex-direction: row; 
        align-items: center; 
        justify-content: center; 
        gap: 10px; 
        margin: 5px 0; 
    }}
    
    .weapon-box img {{ width: 100px !important; height: auto; }}
    
    .stars-box {{ 
        display: flex; 
        flex-direction: row; 
        flex-wrap: wrap; 
        width: 130px; /* Зменшено ширину для зірок */
        gap: 2px; 
        justify-content: flex-start;
    }}
    
    .star-img-fixed {{ width: 24px !important; height: 24px !important; }}

    /* Кнопки */
    .stButton>button {{ width: 100%; height: 3.2em; font-size: 14px !important; border-radius: 10px; }}
    
    /* Компактна історія */
    .history-box {{ 
        background: white; 
        padding: 5px; 
        border-radius: 8px; 
        border: 1px solid #dee2e6; 
        max-height: 100px; 
        overflow-y: auto; 
        font-size: 11px; 
    }}

    /* Зменшення шрифтів метрик */
    [data-testid="stMetricValue"] {{ font-size: 14px !important; }}
    [data-testid="stMetricLabel"] {{ font-size: 10px !important; }}
    
    hr {{ margin: 0.5rem 0 !important; }}
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
    if len(st.session_state.history) > 15: st.session_state.history.pop()

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

# Forge Block
star_html = "".join([f'<img src="data:image/png;base64,{star_64}" class="star-img-fixed">' for _ in range(st.session_state.level)]) if star_64 else "⭐" * st.session_state.level
weapon_tag = f'<img src="data:image/png;base64,{weapon_64}">' if weapon_64 else f'<b>{weapon_name}</b>'

st.markdown(f'<div class="forge-container"><div class="weapon-box">{weapon_tag}</div><div class="stars-box">{star_html}</div></div>', unsafe_allow_html=True)
st.markdown(f'<h1 style="text-align:center; font-size:45px; color:#ffc107; margin:0;">+{st.session_state.level}</h1>', unsafe_allow_html=True)

# Metrics
st.write("---")
m1, m2, m3 = st.columns(3)
icon_metric(m1, sign_64, "Знаки", st.session_state.signs_spent)
icon_metric(m2, sphere_64, "Сфери", st.session_state.spheres_spent)
icon_metric(m3, None, "Спроби", st.session_state.att)

# History and Price (В один ряд, дуже компактно)
col_h, col_p = st.columns([1.2, 1])
with col_h:
    h_html = "".join([f"<div>{i}</div>" for i in st.session_state.history])
    st.markdown(f'<div class="history-box">{h_html}</div>', unsafe_allow_html=True)
with col_p:
    p_sign = st.number_input("Знак", value=2500, step=100, label_visibility="collapsed")
    p_sphere = st.number_input("Сфера", value=400, step=50, label_visibility="collapsed")
    total = st.session_state.gold_spent + (st.session_state.signs_spent * p_sign) + (st.session_state.spheres_spent * p_sphere)
    st.markdown(f"<div style='background:#eee; font-size:12px; padding:4px; border-radius:5px; text-align:center;'><b>{total:,}💰</b></div>", unsafe_allow_html=True)

# Controls
st.write("")
use_signs = st.toggle("Знаки", value=True)
c1, c2, c3 = st.columns([1, 1, 2])
if c1.button("♻️"):
    st.session_state.update({'level':0, 'gold_spent':0, 'signs_spent':0, 'spheres_spent':0, 'att':0, 'history':[]})
    st.rerun()
if c2.button("🚀"):
    while st.session_state.level < 10: sharpen(use_signs)
    st.balloons(); st.rerun()
if c3.button("🔥 ТОЧИТИ"):
    sharpen(use_signs); st.rerun()
