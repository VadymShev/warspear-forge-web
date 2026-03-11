import streamlit as st
import random
import os

# Налаштування сторінки
st.set_page_config(page_title="Warspear Forge Web", page_icon="⚔️", layout="wide")

# Оновлена стилізація
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    
    /* Прибираємо чорний фон і рамки з метрик (статистики) */
    [data-testid="stMetric"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    .stButton>button { width: 100%; height: 3em; font-weight: bold; font-size: 20px; }
    
    .weapon-container {
        text-align: center;
        border: 2px solid #3a86ff;
        padding: 20px;
        border-radius: 20px;
        position: relative;
        background-color: rgba(255, 255, 255, 0.03);
    }
    
    .star-container {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

if 'level' not in st.session_state:
    st.session_state.update({'level': 0, 'gold': 0, 'signs': 0, 'att': 0, 'history': []})

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
st.title("⚒️ Кузня Айнавора: Web Edition")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Керування")
    weapon_name = st.selectbox("Зброя", list(WEAPON_IMAGES.keys()))
    use_signs = st.toggle("Знаки незламності", value=True)
    
    if st.button("🔥 ТОЧИТИ"):
        sharpen(use_signs)
    if st.button("🚀 АВТО +10"):
        while st.session_state.level < 10:
            sharpen(use_signs)
        st.balloons()
    if st.button("♻️ Скинути прогрес"):
        st.session_state.update({'level': 0, 'gold': 0, 'signs': 0, 'att': 0})
        st.rerun()

with col2:
    st.markdown('<div class="weapon-container">', unsafe_allow_html=True)
    
    # ВІДОБРАЖЕННЯ ЗІРОЧОК
    if st.session_state.level > 0:
        star_cols = st.columns(st.session_state.level if st.session_state.level > 0 else 1)
        # Малюємо зірочки в ряд
        cols = st.columns(10) # створюємо 10 вузьких колонок для зірок
        for i in range(st.session_state.level):
            with cols[i]:
                if os.path.exists("star.png"):
                    st.image("star.png", width=30)
                else:
                    st.write("⭐")

    # Картинка зброї
    img_file = WEAPON_IMAGES.get(weapon_name)
    if os.path.exists(img_file):
        st.image(img_file, width=200)
    else:
        st.markdown(f"<h2>{weapon_name}</h2>", unsafe_allow_html=True)
        
    c_chance = CHANCES.get(st.session_state.level, 0)
    st.markdown(f"""
        <h1 style="font-size: 80px; color: #FFD700; margin-top: -10px;">+{st.session_state.level}</h1>
        <h3 style="color: {'#2ecc71' if c_chance > 20 else '#e74c3c'};">Шанс: {c_chance}%</h3>
    </div>
    """, unsafe_allow_html=True)

# СТАТИСТИКА БЕЗ ФОНУ
st.divider()
s1, s2, s3 = st.columns(3)
s1.metric("Витрачено золота", f"{st.session_state.gold:,}")
s2.metric("Витрачено знаків", f"{st.session_state.signs:,}")
s3.metric("Всього спроб", st.session_state.att)
