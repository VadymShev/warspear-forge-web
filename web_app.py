import streamlit as st
import random
import time

# Налаштування сторінки
st.set_page_config(page_title="Warspear Forge Web", page_icon="⚔️", layout="wide")

# Стилізація для "ігрового" вигляду
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #3a86ff; }
    .stButton>button { width: 100%; height: 3em; font-weight: bold; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- ЛОГІКА ТА ШАНСИ ---
if 'level' not in st.session_state:
    st.session_state.update({'level': 0, 'gold': 0, 'signs': 0, 'att': 0, 'history': []})

CHANCES = {0: 100.0, 1: 60.0, 2: 40.0, 3: 25.0, 4: 15.0, 5: 10.0, 6: 7.0, 7: 4.0, 8: 1.5, 9: 0.5}

def get_aura(lvl):
    if lvl >= 10: return "✨🟡✨ (ЛЕГЕНДАРНО)"
    if lvl >= 7: return "🔹🔵🔹 (Сяє)"
    if lvl >= 4: return "🔸🟢🔸 (Магічне)"
    return "⚪ (Звичайне)"

def sharpen(use_signs):
    if st.session_state.level >= 10: return
    
    st.session_state.att += 1
    st.session_state.gold += int(650 + (st.session_state.level * 104))
    # Знаки витрачаються завжди, як ти і просив
    st.session_state.signs += 1
    
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
    weapon = st.selectbox("Оберіть зброю", ["Посох", "Меч", "Дворучний меч", "Сокира", "Спис", "Лук", "Арбалет"])
    use_signs = st.toggle("Використовувати знаки незламності", value=True)
    
    if st.button("🔥 ТОЧИТИ"):
        sharpen(use_signs)
        
    if st.button("🚀 АВТО +10"):
        with st.spinner('Магічне заточування...'):
            limit = 0
            while st.session_state.level < 10 and limit < 5000:
                sharpen(use_signs)
                limit += 1
            st.balloons()

    if st.button("♻️ Скинути прогрес"):
        st.session_state.update({'level': 0, 'gold': 0, 'signs': 0, 'att': 0, 'history': []})
        st.rerun()

with col2:
    # Візуалізація рівня та аури
    c_chance = CHANCES.get(st.session_state.level, 0)
    
    st.markdown(f"""
    <div style="text-align: center; border: 2px solid #3a86ff; padding: 20px; border-radius: 20px;">
        <h1 style="font-size: 100px; color: #FFD700;">+{st.session_state.level}</h1>
        <h3>{get_aura(st.session_state.level)}</h3>
        <p style="font-size: 20px; color: #adb5bd;">{weapon}</p>
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
