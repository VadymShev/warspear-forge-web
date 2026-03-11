import streamlit as st
import random
import os

# Налаштування сторінки
st.set_page_config(page_title="Warspear Forge Web", page_icon="⚔️", layout="wide")

# Стилізація для "ігрового" вигляду
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #3a86ff; }
    .stButton>button { width: 100%; height: 3em; font-weight: bold; font-size: 20px; }
    
    /* Стиль для контейнера зброї та аури */
    .weapon-container {
        text-align: center;
        border: 2px solid #3a86ff;
        padding: 20px;
        border-radius: 20px;
        position: relative;
        overflow: hidden;
        transition: background-color 0.5s ease;
    }
    
    /* Пульсація для +10 */
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0px rgba(255, 215, 0, 0.7); }
        70% { box-shadow: 0 0 0 20px rgba(255, 215, 0, 0); }
        100% { box-shadow: 0 0 0 0px rgba(255, 215, 0, 0); }
    }
    .pulse-aura {
        animation: pulse 2s infinite;
        border-color: #FFD700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ЛОГІЧНІ ЗМІННІ ---
if 'level' not in st.session_state:
    st.session_state.update({'level': 0, 'gold': 0, 'signs': 0, 'att': 0, 'history': []})

CHANCES = {0: 100.0, 1: 60.0, 2: 40.0, 3: 25.0, 4: 15.0, 5: 10.0, 6: 7.0, 7: 4.0, 8: 1.5, 9: 0.5}

# Словник для співставлення назви зброї та файлу картинки (ЯКІ ТРЕБА ЗАВАНТАЖИТИ НА GITHUB)
WEAPON_IMAGES = {
    "Посох": "staff.png",
    "Меч": "sword.png",
    "Дворучний меч": "greatsword.png",
    "Сокира": "axe.png",
    "Дворучна сокира": "greataxe.png",
    "Булава": "mace.png",
    "Дворучна булава": "maul.png",
    "Спис": "spear.png",
    "Кинджал": "dagger.png",
    "Лук": "bow.png",
    "Арбалет": "crossbow.png"
}

def get_aura_settings(lvl):
    """Повертає CSS клас та колір фону аури"""
    if lvl >= 10: return "pulse-aura", "rgba(255, 215, 0, 0.3)" # Золота пульсуюча
    if lvl >= 7: return "", "rgba(58, 134, 255, 0.2)"        # Синя
    if lvl >= 4: return "", "rgba(0, 245, 212, 0.15)"       # Бірюзова
    return "", "transparent"                                # Без аури

def sharpen(use_signs):
    if st.session_state.level >= 10: return
    
    st.session_state.att += 1
    st.session_state.gold += int(650 + (st.session_state.level * 104))
    if use_signs: st.session_state.signs += 1
    
    chance = CHANCES.get(st.session_state.level, 0.5)
    roll = random.uniform(0, 100)
    
    if roll <= chance:
        st.session_state.level += 1
        st.session_state.history.insert(0, f"✅ Успіх! Тепер +{st.session_state.level}")
    else:
        if not use_signs and st.session_state.level > 3:
            st.session_state.level = 0
            st.session_state.history.insert(0, "💥 ЖАХ! Злетіло на +0!")
        else:
            st.session_state.history.insert(0, f"❌ Невдача (шанс був {chance}%)")

# --- ІНТЕРФЕЙС ---
st.title("⚒️ Кузня Айнавора: Web Edition")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Панель керування")
    weapon_name = st.selectbox("Оберіть зброю", list(WEAPON_IMAGES.keys()))
    use_signs = st.toggle("Використовувати знаки незламності", value=True)
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔥 ТОЧИТИ"):
            sharpen(use_signs)
    with col_btn2:
        if st.button("♻️ Скинути"):
            st.session_state.update({'level': 0, 'gold': 0, 'signs': 0, 'att': 0, 'history': []})
            st.rerun()
            
    if st.button("🚀 АВТО +10"):
        with st.spinner('Магічне заточування...'):
            limit = 0
            while st.session_state.level < 10 and limit < 5000:
                sharpen(use_signs)
                limit += 1
            if st.session_state.level == 10: st.balloons()

with col2:
    # Отримання налаштувань аури
    aura_class, aura_bg = get_aura_settings(st.session_state.level)
    c_chance = CHANCES.get(st.session_state.level, 0)
    
    # Створення HTML-контейнера для зброї
    st.markdown(f'<div class="weapon-container {aura_class}" style="background-color: {aura_bg};">', unsafe_allow_html=True)
    
    # Відображення картинки зброї (Якщо файл існує на GitHub)
    img_filename = WEAPON_IMAGES.get(weapon_name)
    if img_filename and os.path.exists(img_filename):
        # Streamlit вміє показувати картинки за назвою файлу, якщо вони в тій же папці
        st.image(img_filename, width=250)
    else:
        # Заглушка, якщо картинки немає
        st.warning(f"Потрібен файл {img_filename} на GitHub")
        st.markdown(f"<h1>⚔️</h1><p>{weapon_name}</p>", unsafe_allow_html=True)
        
    # Текст рівня та шансу
    st.markdown(f"""
        <h1 style="font-size: 100px; color: #FFD700; margin-top: -20px;">+{st.session_state.level}</h1>
        <h2 style="color: {'#2ecc71' if c_chance > 20 else '#e74c3c'};">Шанс: {c_chance}%</h2>
    </div>
    """, unsafe_allow_html=True)

# Статистика знизу
st.divider()
s1, s2, s3 = st.columns(3)
s1.metric("Витрачено золота", f"{st.session_state.gold:,}")
s2.metric("Витрачено знаків", f"{st.session_state.signs:,}")
s3.metric("Всього спроб", st.session_state.att)

# Лог подій
if st.session_state.history:
    st.expander("Історія заточування", expanded=True).write("\n".join(st.session_state.history[:10]))
