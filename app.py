import streamlit as st
import google.generativeai as genai

st.title("La mia AI Personale 🤖")

# Recupero chiave dai Secrets
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        if prompt := st.chat_input("Chiedimi qualcosa..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            
            with st.chat_message("assistant"):
                response = model.generate_content(prompt)
                st.write(response.text)
                st.session_state.messages.append({"role": "model", "content": response.text})
    except Exception as e:
        st.error(f"Si è verificato un errore: {e}")
else:
    st.error("Configura GEMINI_API_KEY nei Secrets di Streamlit!")
