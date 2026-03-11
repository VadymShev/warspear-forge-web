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

def play_sound(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>"""
            st.components.v1.html(md, height=0)

# --- СТИЛІЗАЦІЯ ---
st.markdown(f"""
    <style>
    .block-container {{ padding-top: 3.5rem !important; }}
    .stApp {{ background-color: #f8f9fa; }}
    .forge-container {{ display: flex; flex-direction: row; align-items: center; justify-content: center; gap: 20px; margin: 15px 0; }}
    .stars-box {{ display: flex; flex-direction: row; flex-wrap: wrap; width: 160px; gap: 2px; min-height: 70px; }}
    .star-img-fixed {{ width: 30px; height: 30px; object-fit: contain; }}
    .stButton>button {{ width: 100%; height: 3.5em; font-weight: bold; border-radius: 12px; }}
    div[data-testid="stHorizontalBlock"] > div:last-child button {{ background-color: #0d6efd !important; color: white !important; }}
    .history-box {{ background: white; padding: 10px; border-radius: 10px; border: 1px solid #dee2e6; max-height: 140px; overflow-y: auto; font-size: 13px; }}
    </style>
    """, unsafe_allow_html=True)

# --- ЛОГІКА ТА СТАН ---
if 'level' not in st.session_state:
    st.session_state.update({
        'level': 0, 'gold_spent': 0, 'signs_spent': 0, 
        'spheres_spent': 0, 'att': 0, 'last_sound': None,
        'history': []
    })

# Оновлені шанси (на 9 та 10 зменшено вдвічі)
CHANCES = {
    0: 100.0, 1: 60.0, 2: 40.0, 3: 25.0, 4: 15.0, 
    5: 10.0, 6: 7.0, 7: 4.0, 8: 0.75, 9: 0.25
}

WEAPON_IMAGES = {
    "Посох": "staff.png", "Меч": "sword.png", "Дворучний меч": "greatsword.png",
    "Сокира": "axe.png", "Дворучна сокира": "greataxe.png", "Булава": "mace.png",
    "Дворучна булава": "maul.png", "Спис": "spear.png", "Кинджал": "dagger.png",
    "Лук": "bow.png", "Арбалет": "crossbow.png"
}

def add_to_history(text):
    st.session_state.history.insert(0, text)
    if len(st.session_state.history) > 20: st.session_state.history.pop()

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
        # УСПІХ
        st.session_state.level += 1
        st.session_state.last_sound = "success"
        add_to_history(f"✅ +{old_lvl} ➡️ +{st.session_state.level}")
    else:
        # НЕВДАЧА
        if use_signs or st.session_state.level <= 3:
            # Збереження рівня (якщо зі знаками або рівень до +3)
            st.session_state.last_sound = None
            add_to_history(f"💨 Невдача: +{old_lvl} (збережено)")
        else:
            # Логіка БЕЗ знаків на рівнях 4+
            fail_type = random.choice(["stay", "down", "reset"])
            
            if fail_type == "stay":
                add_to_history(f"💨 Невдача: +{old_lvl} (збережено)")
                st.session_state.last_sound = None
            elif fail_type == "down":
                st.session_state.level -= 1
                add_to_history(f"📉 Пониження: +{old_lvl} ➡️ +{st.session_state.level}")
                st.session_state.last_sound = "fail"
            elif fail_type == "reset":
                st.session_state.level = 0
                add_to_history(f"❌ КРАХ: +{old_lvl} ➡️ +0")
                st.session_state.last_sound = "fail"

# --- ВІДТВОРЕННЯ ЗВУКУ ---
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

star_html = "".join([f'<img src="data:image/png;base64,{star_64}" class="star-img-fixed">' for _ in range(st.session_state.level)]) if star_64 else "⭐" * st.session_state.level
weapon_tag = f'<img src="data:image/png;base64,{weapon_64}" width="130">' if weapon_64 else f'<h3>{weapon_name}</h3>'

st.markdown(f'<div class="forge-container"><div class="weapon-box">{weapon_tag}</div><div class="stars-box">{star_html}</div></div>', unsafe_allow_html=True)
st.markdown(f'<h1 style="text-align:center; font-size:60px; color:#ffc107; margin:0;">+{st.session_state.level}</h1>', unsafe_allow_html=True)

st.write("---")
m1, m2, m3 = st.columns(3)
icon_metric(m1, sign_64, "Знаки", st.session_state.signs_spent) if 'icon_metric' not in locals() else None # Додано нижче для виклику

# (Повтор функції для коректності)
def icon_metric(col, img_64, label, value):
    with col:
        if img_64: st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{img_64}" width="25"></div>', unsafe_allow_html=True)
        st.metric(label, value)

icon_metric(m1, sign_64, "Знаки", st.session_state.signs_spent)
icon_metric(m2, sphere_64, "Сфери", st.session_state.spheres_spent)
icon_metric(m3, None, "Спроби", st.session_state.att)

col_hist, col_prices = st.columns([1, 1])
with col_hist:
    st.caption("📜 Історія")
    h_html = "".join([f"<div>{i}</div>" for i in st.session_state.history])
    st.markdown(f'<div class="history-box">{h_html}</div>', unsafe_allow_html=True)

with col_prices:
    st.caption("🛠️ Ціни")
    p_sign = st.number_input("Ціна Знаку", value=2500, step=100, label_visibility="collapsed")
    p_sphere = st.number_input("Ціна Сфери", value=400, step=50, label_visibility="collapsed")
    total = st.session_state.gold_spent + (st.session_state.signs_spent * p_sign) + (st.session_state.spheres_spent * p_sphere)
    st.markdown(f"<div style='background:#e9ecef; padding:5px; border-radius:5px; text-align:center; margin-top:5px;'><b>{total:,} 💰</b></div>", unsafe_allow_html=True)

st.write("")
use_signs = st.toggle("Знаки незламності", value=True)
c_res, c_auto, c_main = st.columns([1, 1, 2])

if c_res.button("♻️"):
    st.session_state.update({'level':0, 'gold_spent':0, 'signs_spent':0, 'spheres_spent':0, 'att':0, 'last_sound':None, 'history':[]})
    st.rerun()

if c_auto.button("🚀"):
    while st.session_state.level < 10: sharpen(use_signs)
    st.balloons(); st.rerun()

if c_main.button("🔥 ТОЧИТИ"):
    sharpen(use_signs); st.rerun()
