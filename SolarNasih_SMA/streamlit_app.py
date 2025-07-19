import streamlit as st
import requests

st.set_page_config(page_title="Solar Nasih SMA", page_icon="☀️")
st.title("Solar Nasih SMA - Assistant Solaire")

st.markdown("""
Bienvenue sur l'interface Solar Nasih SMA !

Posez vos questions sur l'énergie solaire, la réglementation, la simulation, la certification, etc.
""")

if "history" not in st.session_state:
    st.session_state["history"] = []

user_input = st.text_input("Votre question :", "")

if st.button("Envoyer") and user_input.strip():
    try:
        response = requests.post(
            "http://localhost:8000/chat",  # Endpoint correct pour le chat
            json={"message": user_input}
        )
        if response.status_code == 200:
            data = response.json()
            if "response" in data:
                answer = data["response"]
            else:
                answer = f"Erreur : la réponse du serveur ne contient pas de clé 'response'.\nDétail brut : {data}"
            st.session_state["history"].append((user_input, answer))
        else:
            st.session_state["history"].append((user_input, f"Erreur API: {response.status_code}"))
    except Exception as e:
        st.session_state["history"].append((user_input, f"Erreur de connexion: {e}"))

if st.session_state["history"]:
    st.markdown("## Historique")
    for i, (q, a) in enumerate(reversed(st.session_state["history"])):
        st.markdown(f"**Vous :** {q}")
        st.markdown(f"**Solar Nasih :** {a}")
        st.markdown("---") 