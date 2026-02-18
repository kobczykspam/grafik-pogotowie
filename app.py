import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Konfiguracja strony
st.set_page_config(page_title="System Grafik - Pogotowie", layout="wide")

# Połączenie z Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- TUTAJ WKLEJ SWÓJ LINK DO ARKUSZA ---
URL_ARKUSZA = "https://docs.google.com/spreadsheets/d/1aOLREIfSOMpVYadu0_TKuXa_KO723rwHRGtWAC2vW2Y/edit?gid=1585384814#gid=1585384814"

# Funkcja pobierająca dane (ttl=0 wyłącza pamięć podręczną, dane są zawsze świeże)
def pobierz_dane(nazwa_karty):
    try:
        return conn.read(spreadsheet=URL_ARKUSZA, worksheet=nazwa_karty, ttl=0)
    except Exception as e:
        st.error(f"Błąd podczas pobierania karty {nazwa_karty}: {e}")
        return pd.DataFrame()

# Obsługa sesji użytkownika
if 'user' not in st.session_state:
    st.session_state['user'] = None

# --- EKRAN LOGOWANIA ---
if st.session_state['user'] is None:
    st.title("🚑 System Grafik - Logowanie")
    email_input = st.text_input("Podaj swój e-mail służbowy:")
    if st.button("Zaloguj się"):
        pracownicy = pobierz_dane("Pracownicy")
        if not pracownicy.empty and 'Email' in pracownicy.columns:
            # Standaryzacja na małe litery
            lista_maili = pracownicy['Email'].str.lower().str.strip().values
            if email_input.lower().strip() in lista_maili:
                st.session_state['user'] = email_input.lower().strip()
                st.success("Zalogowano pomyślnie!")
                st.rerun()
            else:
                st.error("Nie znaleziono tego adresu e-mail na liście pracowników.")
        else:
            st.error("Błąd bazy danych: Brak kolumny 'Email' w karcie Pracownicy.")

# --- PANEL PO ZALOGOWANIU ---
else:
    st.sidebar.title("🚑 Panel Pracownika")
    st.sidebar.info(f"Zalogowany: \n{st.session_state['user']}")
    
    menu = st.sidebar.radio("Nawigacja:", ["Mój Grafik", "Zgłoś dostępność", "Giełda zamian"])
    
    if st.sidebar.button("Wyloguj"):
        st.session_state['user'] = None
        st.rerun()

    # --- WIDOK: MÓJ GRAFIK ---
    if menu == "Mój Grafik":
        st.header("📅 Twoje zaplanowane dyżury")
        grafik = pobierz_dane("Grafik_Zatwierdzony")
        
        if not grafik.empty:
            moje_dyzury = grafik[grafik['Pracownik'].str.lower() == st.session_state['user']].copy()
            
            if moje_dyzury.empty:
                st.info("Nie masz przypisanych dyżurów w obecnym grafiku.")
            else:
                st.dataframe(moje_dyzury, use_container_width=True)
                
                # SEKCJA WYSTAWIANIA NA ZAMIANĘ
                st.write("---")
                st.subheader("🔄 Chcesz oddać dyżur?")
                opcje = moje_dyzury.apply(lambda x: f"{x['Data']} - {x['Zmiana']}", axis=1).tolist()
                wybor = st.selectbox("Wybierz dyżur do wystawienia na zamianę:", ["---"] + opcje)
                
                if st.button("Wystaw na giełdę zamian"):
                    if wybor != "---":
                        # Znalezienie wiersza w oryginalnym grafiku
                        idx = moje_dyzury.index[opcje.index(wybor)]
                        grafik.at[idx, 'Status Zamiany'] = "SZUKAM ZASTĘPSTWA"
                        
                        conn.update(spreadsheet=URL_ARKUSZA, worksheet="Grafik_Zatwierdzony", data=grafik)
                        st.success(f"Dyżur {wybor} jest teraz widoczny na giełdzie!")
                        st.rerun()
        else:
            st.warning("Nie udało się załadować danych grafiku.")

    # --- WIDOK: ZGŁOŚ DOSTĘPNOŚĆ ---
    elif menu == "Zgłoś dostępność":
        st.header("📝 Zgłoś swoją dyspozycyjność")
        st.write("Wybierz dni i zmiany, w których możesz pracować w przyszłym miesiącu.")
        
        with st.form("form_dostep", clear_on_submit=True):
            d_data = st.date_input("Data dyżuru")
            d_zmiana = st.selectbox("Preferowana zmiana", ["Dzień", "Noc", "Doba"])
            d_uwagi = st.text_input("Dodatkowe uwagi")
            submit = st.form_submit_button("Wyślij zgłoszenie")
            
            if submit:
                stara_dostepnosc = pobierz_dane("Dyspozycyjność")
                nowy_wiersz = pd.DataFrame([{
                    "Data": d_data.strftime("%Y-%m-%d"),
                    "Pracownik": st.session_state['user'],
                    "Zmiana": d_zmiana,
                    "Uwagi": d_uwagi
                }])
                aktualna = pd.concat([stara_dostepnosc, nowy_wiersz], ignore_index=True)
                
                conn.update(spreadsheet=URL_ARKUSZA, worksheet="Dyspozycyjność", data=aktualna)
                st.success("Zgłoszenie zostało zapisane w bazie!")
                st.balloons()

    # --- WIDOK: GIEŁDA ZAMIAN ---
    elif menu == "Giełda zamian":
        st.header("🔄 Dyżury do przejęcia")
        st.write("Poniżej znajdują się dyżury wystawione przez innych pracowników.")
        grafik_full = pobierz_dane("Grafik_Zatwierdzony")
        
        if not grafik_full.empty:
            zamiany = grafik_full[grafik_full['Status Zamiany'] == "SZUKAM ZASTĘPSTWA"]
            if zamiany.empty:
                st.info("Obecnie brak ofert zamiany.")
            else:
                st.table(zamiany[["Data", "Pracownik", "Zmiana", "Uwagi"]])
                st.info("Aby przejąć dyżur, skontaktuj się bezpośrednio z pracownikiem lub koordynatorem.")
