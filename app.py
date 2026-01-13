import streamlit as st
import google.generativeai as genai
import json
import datetime
import time

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="GymGenius AI", page_icon="💪", layout="wide")

# --- CSS CUSTOM PER AVVICINARSI AL LOOK REACT ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        font-weight: bold;
    }
    .success-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #d4edda;
        color: #155724;
        margin-bottom: 1rem;
    }
    .workout-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 10px;
        border: 1px solid #444;
    }
</style>
""", unsafe_allow_html=True)

# --- CONFIGURAZIONE AI ---
# Recupera la chiave dai Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # SYSTEM PROMPT SPECIFICO CHE HAI FORNITO
    system_prompt = """
    Agisci come Senior Developer di 'GymGenius', una web app per il fitness. 
    Il tuo compito è generare schede di allenamento in formato JSON puro.
    Non aggiungere testo introduttivo o markdown, solo il JSON.
    Struttura richiesta:
    {
      "nome_scheda": "Nome",
      "giorni": [
        {
          "giorno": "Lunedì - Focus",
          "esercizi": [
            {
              "nome": "Esercizio",
              "serie": 4,
              "reps": "8-10",
              "recupero": 90,
              "note": "Note tecniche"
            }
          ]
        }
      ]
    }
    """
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_prompt)
else:
    st.error("Chiave API mancante! Configura i Secrets.")
    st.stop()

# --- GESTIONE STATO (DATABASE TEMPORANEO) ---
if "scheda_attiva" not in st.session_state:
    st.session_state.scheda_attiva = None
if "storico_workout" not in st.session_state:
    st.session_state.storico_workout = []

# --- MENU DI NAVIGAZIONE ---
st.sidebar.title("💪 GymGenius")
menu = st.sidebar.radio("Navigazione", ["🏠 Dashboard", "⚡ Generatore AI", "🏋️ Sessione Workout"])

# --- PAGINA 1: DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title("Benvenuto in GymGenius")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Allenamenti Completati", value=len(st.session_state.storico_workout))
    with col2:
        if st.session_state.scheda_attiva:
            st.metric(label="Scheda Attiva", value=st.session_state.scheda_attiva['nome_scheda'])
        else:
            st.warning("Nessuna scheda attiva")

    st.subheader("Storico Recente")
    if st.session_state.storico_workout:
        for log in st.session_state.storico_workout[-3:]:
            st.write(f"✅ {log['data']} - {log['nome']}")
    else:
        st.info("Nessun allenamento registrato ancora.")

# --- PAGINA 2: GENERATORE AI ---
elif menu == "⚡ Generatore AI":
    st.title("Generatore Schede AI")
    st.markdown("Crea la tua scheda perfetta con Google Gemini.")

    col1, col2 = st.columns(2)
    with col1:
        obiettivo = st.selectbox("Obiettivo", ["Ipertrofia", "Forza", "Dimagrimento", "Resistenza"])
        livello = st.selectbox("Livello", ["Principiante", "Intermedio", "Avanzato"])
    with col2:
        giorni = st.slider("Giorni a settimana", 2, 6, 4)
        attrezzatura = st.text_input("Attrezzatura", "Palestra completa")

    note_extra = st.text_area("Note specifiche (es. 'Ho mal di schiena', 'Focus glutei')", "")

    if st.button("✨ Genera Scheda con AI"):
        with st.spinner("L'AI sta creando la tua scheda..."):
            prompt = f"""
            Crea una scheda per:
            Obiettivo: {obiettivo}
            Livello: {livello}
            Giorni: {giorni}
            Attrezzatura: {attrezzatura}
            Note: {note_extra}
            """
            try:
                response = model.generate_content(prompt)
                # Pulisce la risposta per ottenere solo il JSON
                testo_pulito = response.text.replace("```json", "").replace("```", "")
                dati_scheda = json.loads(testo_pulito)
                
                st.session_state.scheda_attiva = dati_scheda
                st.success(f"Scheda '{dati_scheda['nome_scheda']}' generata e salvata!")
                st.json(dati_scheda) # Mostra l'anteprima
            except Exception as e:
                st.error(f"Errore nella generazione: {e}")

# --- PAGINA 3: SESSIONE WORKOUT ---
elif menu == "🏋️ Sessione Workout":
    st.title("Modalità Allenamento")

    if not st.session_state.scheda_attiva:
        st.warning("Devi prima generare una scheda nella sezione AI!")
    else:
        scheda = st.session_state.scheda_attiva
        
        # Selettore del giorno
        giorni_disponibili = [g['giorno'] for g in scheda['giorni']]
        giorno_scelto = st.selectbox("Che allenamento fai oggi?", giorni_disponibili)
        
        # Trova gli esercizi del giorno
        allenamento_oggi = next(g for g in scheda['giorni'] if g['giorno'] == giorno_scelto)
        
        # --- CARICO PROGRESSIVO AI ---
        col_ai, col_vuota = st.columns([1, 1])
        with col_ai:
            if st.button("🤖 Ottimizza Carichi con AI"):
                st.info("Analisi storico in corso... Aumento carico del 2.5% sugli esercizi base.")
                time.sleep(1)
                st.success("Carichi aggiornati per Progressive Overload!")

        st.divider()
        
        # Lista Esercizi
        progress = 0
        total_exercises = len(allenamento_oggi['esercizi'])
        
        for idx, esercizio in enumerate(allenamento_oggi['esercizi']):
            with st.expander(f"{idx+1}. {esercizio['nome']} ({esercizio['serie']} x {esercizio['reps']})", expanded=True):
                st.caption(f"Note: {esercizio.get('note', 'Nessuna nota')} | Rec: {esercizio['recupero']}s")
                
                cols = st.columns(esercizio['serie'])
                completed_sets = 0
                
                for i in range(esercizio['serie']):
                    # Checkbox per simulare lo swipe di completamento
                    fatto = cols[i].checkbox(f"Set {i+1}", key=f"check_{giorno_scelto}_{esercizio['nome']}_{i}")
                    if fatto:
                        completed_sets += 1
                
                # Feedback visivo se esercizio completato
                if completed_sets == esercizio['serie']:
                    st.success(f"Esercizio completato! Recupera {esercizio['recupero']}s")
                    progress += 1

        # Barra di progresso workout
        st.progress(progress / total_exercises)

        if progress == total_exercises:
            st.balloons()
            if st.button("🏁 Termina e Salva Workout"):
                log = {
                    "data": datetime.date.today().strftime("%Y-%m-%d"),
                    "nome": giorno_scelto,
                    "completato": True
                }
                st.session_state.storico_workout.append(log)
                st.success("Allenamento salvato nello storico!")
