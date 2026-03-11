import streamlit as st
import random

st.set_page_config(page_title="Warspear Web Forge", page_icon="⚔️")

st.title("⚔️ Warspear Web Forge +10")

# Ініціалізація стану гри
if 'level' not in st.session_state:
    st.session_state.update({'level': 0, 'gold': 0, 'signs': 0, 'att': 0})

# Бокова панель
st.sidebar.header("Налаштування")
weapon = st.sidebar.selectbox("Зброя", ["Посох", "Меч", "Сокира", "Лук"])
use_signs = st.sidebar.checkbox("Використовувати знаки", value=True)

# Шанси
chances = {0: 100, 1: 60, 2: 40, 3: 25, 4: 15, 5: 10, 6: 7, 7: 4, 8: 1.5, 9: 0.5}

def sharpen():
    st.session_state.att += 1
    st.session_state.gold += (650 + st.session_state.level * 100)
    if use_signs: st.session_state.signs += 1
    
    chance = chances.get(st.session_state.level, 0.5)
    if random.uniform(0, 100) <= chance:
        st.session_state.level += 1
        st.balloons() if st.session_state.level == 10 else None
    else:
        if not use_signs and st.session_state.level > 3:
            st.session_state.level = 0

# Візуалізація
col1, col2 = st.columns(2)
with col1:
    st.metric("Рівень", f"+{st.session_state.level}")
    st.metric("Шанс", f"{chances.get(st.session_state.level, 0)}%")

with col2:
    # Емодзі-візуалізація аури
    aura = "⚪"
    if st.session_state.level >= 10: aura = "🔥✨🌟"
    elif st.session_state.level >= 7: aura = "🔵"
    elif st.session_state.level >= 4: aura = "🟢"
    
    st.write(f"### {aura} {weapon} {aura}")

if st.button("ТОЧИТИ!", use_container_width=True):
    sharpen()

st.write(f"💰 Золото: {st.session_state.gold} | 🛡️ Знаки: {st.session_state.signs}")