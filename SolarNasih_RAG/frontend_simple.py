import streamlit as st
import requests
import json

st.set_page_config(
    page_title="RAG Multimodal System",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 RAG Multimodal System")
st.markdown("Recherchez dans vos documents avec l'IA")

# Configuration API
API_BASE_URL = "http://localhost:8000"

# Sidebar
with st.sidebar:
    st.header("📁 Upload Documents")
    
    uploaded_files = st.file_uploader(
        "Choisissez vos fichiers",
        accept_multiple_files=True,
        type=['txt', 'pdf', 'jpg', 'jpeg', 'png', 'mp3', 'wav', 'mp4']
    )
    
    if uploaded_files and st.button("📤 Upload"):
        try:
            files = [("files", (file.name, file.getvalue(), file.type)) for file in uploaded_files]
            response = requests.post(f"{API_BASE_URL}/upload/files", files=files)
            
            if response.status_code == 200:
                result = response.json()
                st.success(f"✅ {len(uploaded_files)} fichiers uploadés!")
                st.json(result)
            else:
                st.error("❌ Erreur d'upload")
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")
    
    st.header("⚙️ Paramètres")
    method = st.selectbox("Méthode", ["hybrid", "vector", "keyword"])
    top_k = st.slider("Nombre de résultats", 1, 10, 5)
    generate_response = st.checkbox("Générer réponse IA", True)

# Interface principale
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🔍 Recherche")
    
    query = st.text_input("Posez votre question:", placeholder="Que voulez-vous savoir?")
    
    if st.button("🔍 Rechercher", type="primary") and query:
        with st.spinner("Recherche en cours..."):
            try:
                payload = {
                    "query": query,
                    "method": method,
                    "top_k": top_k,
                    "generate_response": generate_response
                }
                
                response = requests.post(f"{API_BASE_URL}/search/", json=payload)
                
                if response.status_code == 200:
                    results = response.json()
                    
                    # Réponse IA
                    if generate_response and results.get("generated_response"):
                        st.header("🤖 Réponse IA")
                        st.write(results["generated_response"]["response"])
                        
                        with st.expander("Détails de la réponse"):
                            st.json(results["generated_response"]["metadata"])
                    
                    # Résultats de recherche
                    st.header(f"📄 Résultats ({results['total_results']})")
                    
                    for i, result in enumerate(results["results"]):
                        with st.expander(f"📄 Résultat {i+1} - Score: {result['score']:.2f}"):
                            st.write(f"**Source:** {result['source']}")
                            st.write(f"**Type:** {result['doc_type']}")
                            st.write(f"**Contenu:**")
                            st.write(result["content"])
                            
                            if st.checkbox(f"Métadonnées {i+1}"):
                                st.json(result["metadata"])
                else:
                    st.error("❌ Erreur de recherche")
                    
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")

with col2:
    st.header("📊 Statut Système")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health/detailed")
        if response.status_code == 200:
            health = response.json()
            st.success("✅ Système opérationnel")
            st.metric("Statut", health["status"])
            
            if "system_metrics" in health:
                st.json(health["system_metrics"])
        else:
            st.error("❌ API non accessible")
    except:
        st.error("❌ Connexion impossible")
    
    st.header("💡 Conseils")
    st.markdown("""
    - **Uploadez** vos documents dans la sidebar
    - **Posez des questions** spécifiques  
    - **Explorez** différentes méthodes de recherche
    - **Consultez** la documentation API
    """)
    
    if st.button("📚 Documentation API"):
        st.markdown(f"[Ouvrir la documentation]({API_BASE_URL}/docs)")

# Pied de page
st.markdown("---")
st.markdown("🔍 RAG Multimodal System - Mode démo fonctionnel")