import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Grafik Pogotowie", layout="wide")

# --- PROSTE LOGOWANIE ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def login():
    st.title("Logowanie do Systemu Grafik")
    user = st.text_input("Użytkownik (e-mail)")
    if st.button("Zaloguj"):
        st.session_state['logged_in'] = True
        st.rerun()

if not st.session_state['logged_in']:
    login()
else:
    # --- MENU GŁÓWNE ---
    st.sidebar.title("Nawigacja")
    page = st.sidebar.radio("Wybierz:", ["Mój Grafik", "Zgłoś Dyspozycyjność", "Zamiany"])

    if page == "Mój Grafik":
        st.header("Twój aktualny grafik")
        # Tu kod będzie pobierał dane z Google Sheets
        st.info("Tutaj pojawi się kalendarz pobrany z Twojego arkusza Google.")

    elif page == "Zgłoś Dyspozycyjność":
        st.header("Wybierz daty dyżurów")
        wybrana_data = st.date_input("Wybierz dzień")
        zmiana = st.selectbox("Zmiana", ["Dzień", "Noc", "Doba"])
        if st.button("Zapisz moją dostępność"):
            st.success(f"Zapisano: {wybrana_data} - {zmiana}")

    elif page == "Zamiany":
        st.header("Giełda dyżurów")
        st.warning("Lista dyżurów wystawionych na zamianę przez kolegów.")
