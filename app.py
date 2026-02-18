import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Grafik Pogotowie", layout="wide")

# Podłączamy się do Arkusza
conn = st.connection("gsheets", type=GSheetsConnection)

# --- TUTAJ WKLEJ LINK DO SWOJEGO ARKUSZA ---
URL_ARKUSZA = "https://docs.google.com/spreadsheets/d/1aOLREIfSOMpVYadu0_TKuXa_KO723rwHRGtWAC2vW2Y/edit?gid=0#gid=0"

# Funkcja pobierająca dane
def pobierz_dane(nazwa_karty):
    return conn.read(spreadsheet=URL_ARKUSZA, worksheet=nazwa_karty)

# --- PROSTE LOGOWANIE ---
if 'user' not in st.session_state:
    st.session_state['user'] = None

if st.session_state['user'] is None:
    st.title("🚑 System Grafik - Logowanie")
    email = st.text_input("Podaj swój e-mail z listy pracowników")
    if st.button("Zaloguj się"):
        # Sprawdzamy czy e-mail jest w tabeli Pracownicy
        pracownicy = pobierz_dane("Pracownicy")
        if email in pracownicy['Email'].values:
            st.session_state['user'] = email
            st.rerun()
        else:
            st.error("Nie znaleziono takiego e-maila w bazie!")
else:
    st.sidebar.write(f"Zalogowany: **{st.session_state['user']}**")
    if st.sidebar.button("Wyloguj"):
        st.session_state['user'] = None
        st.rerun()

    menu = st.sidebar.radio("Menu", ["Mój Grafik", "Zgłoś dostępność", "Zamiany"])

    if menu == "Mój Grafik":
        st.header("📅 Twój Grafik")
        grafik = pobierz_dane("Grafik_Zatwierdzony")
        moje_dyzury = grafik[grafik['Pracownik'] == st.session_state['user']]
        st.dataframe(moje_dyzury, use_container_width=True)

    elif menu == "Zgłoś dostępność":
        st.header("📝 Zgłoś kiedy możesz pracować")
        with st.form("form_dostepnosc"):
            data = st.date_input("Dzień")
            zmiana = st.selectbox("Zmiana", ["Dzień", "Noc", "Doba"])
            uwagi = st.text_input("Uwagi")
            submit = st.form_submit_button("Wyślij do bazy")
            
            if submit:
                # Tu w przyszłości dodamy kod dopisujący wiersz do Arkusza
                st.success("Zgłoszenie zostało wysłane (podgląd w Arkuszu Google)!")

    elif menu == "Zamiany":
        st.header("🔄 Giełda zamian")
        grafik = pobierz_dane("Grafik_Zatwierdzony")
        do_zamiany = grafik[grafik['Status Zamiany'] == "SZUKAM ZASTĘPSTWA"]
        st.table(do_zamiany)
