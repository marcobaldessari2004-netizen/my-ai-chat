import streamlit as st
import google.generativeai as genai

st.title("La mia AI Personale 🤖")

# Configurazione Sicura
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.warning("Inserisci la chiave API nei Secrets per iniziare.")
except Exception as e:
    st.error(f"Errore di configurazione: {e}")

# Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("Scrivi qui..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    if "model" in locals():
        with st.chat_message("assistant"):
            try:
                response = model.generate_content(prompt)
                st.write(response.text)
                st.session_state.messages.append({"role": "model", "content": response.text})
            except Exception as e:
                st.error(f"Errore: {e}")
