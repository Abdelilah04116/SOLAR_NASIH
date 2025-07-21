import streamlit as st
import requests
import json

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
        with st.spinner("Traitement en cours..."):
            response = requests.post(
                "http://localhost:8000/chat",
                json={"message": user_input}
            )
            
        if response.status_code == 200:
            data = response.json()
            
            # Gestion des différentes clés possibles dans la réponse
            if "message" in data:
                answer = data["message"]
            elif "response" in data:
                answer = data["response"]
            else:
                answer = f"Erreur : structure de réponse inattendue.\nDétail brut : {json.dumps(data, indent=2, ensure_ascii=False)}"
            
            # Ajout d'informations sur l'agent utilisé si disponible
            agent_info = ""
            if "agent_used" in data:
                agent_info = f" (Agent: {data['agent_used']})"
            
            # Stockage des données complètes pour l'affichage détaillé
            st.session_state["history"].append({
                "question": user_input,
                "answer": answer,
                "agent_info": agent_info,
                "full_data": data,  # Stockage des données complètes
                "timestamp": st.session_state.get("timestamp", 0) + 1
            })
            st.session_state["timestamp"] = st.session_state.get("timestamp", 0) + 1
        else:
            error_msg = f"Erreur API: {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f" - {json.dumps(error_detail, ensure_ascii=False)}"
            except:
                error_msg += f" - {response.text}"
            st.session_state["history"].append({
                "question": user_input,
                "answer": error_msg,
                "agent_info": "",
                "full_data": {"error": error_msg},
                "timestamp": st.session_state.get("timestamp", 0) + 1
            })
            st.session_state["timestamp"] = st.session_state.get("timestamp", 0) + 1
    except Exception as e:
        st.session_state["history"].append({
            "question": user_input,
            "answer": f"Erreur de connexion: {str(e)}",
            "agent_info": "",
            "full_data": {"error": str(e)},
            "timestamp": st.session_state.get("timestamp", 0) + 1
        })
        st.session_state["timestamp"] = st.session_state.get("timestamp", 0) + 1

# Affichage de l'historique
if st.session_state["history"]:
    st.markdown("## Historique des conversations")
    for i, conversation in enumerate(reversed(st.session_state["history"])):
        with st.expander(f"Conversation {len(st.session_state['history']) - i}", expanded=True):
            st.markdown(f"**Vous :** {conversation['question']}")
            st.markdown(f"**Solar Nasih{conversation['agent_info']} :**")
            
            # Affichage de la réponse principale
            st.markdown(conversation['answer'])
            
            # Affichage des détails des agents si disponibles
            if "agent_responses" in conversation.get("full_data", {}):
                st.markdown("---")
                st.markdown("**🔍 Détails des agents utilisés :**")
                
                agent_responses = conversation["full_data"]["agent_responses"]
                for agent_response in agent_responses:
                    agent_name = agent_response["agent_type"].replace("_", " ").title()
                    confidence = agent_response["confidence"]
                    success = agent_response["success"]
                    
                    # Indicateur de statut
                    status_emoji = "✅" if success else "❌"
                    confidence_emoji = "🟢" if confidence > 0.8 else "🟡" if confidence > 0.5 else "🔴"
                    
                    with st.container():
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            st.markdown(f"{status_emoji} {confidence_emoji}")
                        with col2:
                            st.markdown(f"**{agent_name}** (confiance: {confidence:.1%})")
                            if success:
                                st.markdown(f"*{agent_response['response'][:200]}...*")
                            else:
                                st.markdown(f"*{agent_response['response']}*")
            
            # Affichage des sources si disponibles
            if "sources" in conversation.get("full_data", {}) and conversation["full_data"]["sources"]:
                st.markdown("---")
                st.markdown("**📚 Sources utilisées :**")
                for source in conversation["full_data"]["sources"]:
                    st.markdown(f"• {source}")
            
            st.markdown("---")

# Bouton pour effacer l'historique
if st.button("Effacer l'historique"):
    st.session_state["history"] = []
    st.session_state["timestamp"] = 0
    st.rerun() 