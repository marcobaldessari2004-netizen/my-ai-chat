import streamlit as st
import os
import subprocess
import sys

# Forza l'installazione della libreria mancante al volo
try:
    import google.generativeai as genai
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generative-ai"])
    import google.generativeai as genai

st.title("La mia AI Personale 🤖")

# Verifica chiave nei Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input("Scrivi qui..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            response = model.generate_content(prompt)
            st.write(response.text)
            st.session_state.messages.append({"role": "model", "content": response.text})
else:
    st.error("Manca la chiave GEMINI_API_KEY nei Secrets!")
