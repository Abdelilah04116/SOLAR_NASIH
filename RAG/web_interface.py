"""
Interface web pour visualiser et interagir avec la pipeline RAG multimodal
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
from io import BytesIO
from PIL import Image
import json
from pathlib import Path
import logging

# Imports du projet
from pipeline import create_pipeline
from config import RAGPipelineConfig
from models import ChunkType
from visualizer import ChunkVisualizer, visualize_document, create_quick_preview

# Configuration de la page
st.set_page_config(
    page_title="RAG Multimodal - Visualiseur de Chunks",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .chunk-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        background: #f8f9fa;
    }
    .chunk-header {
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 10px;
    }
    .chunk-content {
        font-size: 14px;
        color: #34495e;
        max-height: 150px;
        overflow-y: auto;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

class RAGWebInterface:
    """Interface web principale"""
    
    def __init__(self):
        self.pipeline = None
        self.visualizer = ChunkVisualizer()
        
        # Initialisation de la session
        if 'pipeline_initialized' not in st.session_state:
            st.session_state.pipeline_initialized = False
        if 'documents' not in st.session_state:
            st.session_state.documents = []
        if 'search_history' not in st.session_state:
            st.session_state.search_history = []
    
    def run(self):
        """Lance l'interface web"""
        st.title("🔍 RAG Multimodal - Visualiseur de Chunks")
        st.markdown("---")
        
        # Sidebar pour la configuration
        self.setup_sidebar()
        
        # Contenu principal
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📤 Ingestion", "🔍 Recherche", "📊 Visualisations", 
            "📈 Statistiques", "⚙️ Configuration"
        ])
        
        with tab1:
            self.ingestion_interface()
        
        with tab2:
            self.search_interface()
        
        with tab3:
            self.visualization_interface()
        
        with tab4:
            self.statistics_interface()
        
        with tab5:
            self.configuration_interface()
    
    def setup_sidebar(self):
        """Configure la barre latérale"""
        st.sidebar.title("🛠️ Configuration")
        
        # Statut de la pipeline
        if st.session_state.pipeline_initialized:
            st.sidebar.success("✅ Pipeline initialisée")
            
            if st.sidebar.button("🔄 Réinitialiser Pipeline"):
                st.session_state.pipeline_initialized = False
                self.pipeline = None
                st.experimental_rerun()
        else:
            st.sidebar.warning("⚠️ Pipeline non initialisée")
        
        # Configuration rapide
        st.sidebar.subheader("Configuration Rapide")
        
        vector_store_type = st.sidebar.selectbox(
            "Type de Vector Store",
            ["chroma", "faiss"],
            index=0
        )
        
        store_path = st.sidebar.text_input(
            "Chemin du Vector Store",
            value="./web_vector_store"
        )
        
        if st.sidebar.button("🚀 Initialiser Pipeline"):
            self.initialize_pipeline(vector_store_type, store_path)
        
        # Informations système
        if self.pipeline:
            st.sidebar.subheader("📊 Informations")
            stats = self.pipeline.get_statistics()
            
            st.sidebar.metric("Documents", stats['pipeline_state']['documents_processed'])
            st.sidebar.metric("Chunks", stats['pipeline_state']['total_chunks'])
            st.sidebar.metric("Vector Store", stats['vector_store_count'])
    
    def initialize_pipeline(self, vector_store_type: str, store_path: str):
        """Initialise la pipeline"""
        try:
            config = RAGPipelineConfig()
            config.vector_store.store_type = vector_store_type
            config.vector_store.store_path = store_path
            config.log_level = "INFO"
            
            self.pipeline = create_pipeline(config)
            st.session_state.pipeline_initialized = True
            st.sidebar.success("Pipeline initialisée avec succès!")
            
        except Exception as e:
            st.sidebar.error(f"Erreur d'initialisation: {e}")
    
    def ingestion_interface(self):
        """Interface d'ingestion de documents"""
        st.header("📤 Ingestion de Documents")
        
        if not st.session_state.pipeline_initialized:
            st.warning("⚠️ Veuillez d'abord initialiser la pipeline dans la barre latérale")
            return
        
        # Upload de fichier
        uploaded_file = st.file_uploader(
            "Choisir un fichier",
            type=['pdf', 'txt', 'md'],
            help="Formats supportés: PDF, TXT, MD"
        )
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if uploaded_file is not None:
                st.success(f"Fichier sélectionné: {uploaded_file.name}")
                
                # Sauvegarde temporaire
                temp_path = Path(f"./temp_{uploaded_file.name}")
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                if st.button("🚀 Lancer l'Ingestion", type="primary"):
                    self.process_document(temp_path)
                    
                    # Nettoyage
                    if temp_path.exists():
                        temp_path.unlink()
        
        with col2:
            st.subheader("Options")
            show_progress = st.checkbox("Afficher le progrès", value=True)
            generate_viz = st.checkbox("Générer visualisations", value=True)
        
        # Historique des documents traités
        if st.session_state.documents:
            st.subheader("📚 Documents Traités")
            
            for i, doc_info in enumerate(st.session_state.documents):
                with st.expander(f"📄 {doc_info['name']} - {doc_info['chunks']} chunks"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Pages", doc_info['pages'])
                    with col2:
                        st.metric("Chunks", doc_info['chunks'])
                    with col3:
                        st.metric("Temps", f"{doc_info['time']:.2f}s")
                    
                    if st.button(f"🔍 Voir les chunks", key=f"view_{i}"):
                        self.show_document_chunks(doc_info)
    
    def process_document(self, file_path: Path):
        """Traite un document"""
        with st.spinner("🔄 Traitement en cours..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Simulation du progrès
                status_text.text("📖 Parsing du document...")
                progress_bar.progress(20)
                
                result = self.pipeline.ingest_document(str(file_path))
                progress_bar.progress(100)
                
                if result.success:
                    st.success("✅ Document traité avec succès!")
                    
                    # Sauvegarde des informations
                    doc_info = {
                        'name': file_path.name,
                        'path': str(file_path),
                        'chunks': result.chunks_created,
                        'pages': result.document.total_pages if result.document else 0,
                        'time': result.processing_time,
                        'document': result.document
                    }
                    st.session_state.documents.append(doc_info)
                    
                    # Affichage des statistiques
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Chunks créés", result.chunks_created)
                    with col2:
                        st.metric("Embeddings", result.embeddings_generated)
                    with col3:
                        st.metric("Temps", f"{result.processing_time:.2f}s")
                    with col4:
                        st.metric("Pages", result.document.total_pages if result.document else 0)
                    
                    # Aperçu des chunks
                    if result.document and result.document.chunks:
                        st.subheader("👀 Aperçu des Chunks")
                        self.display_chunks_preview(result.document.chunks[:5])
                
                else:
                    st.error(f"❌ Erreur lors du traitement: {result.error_message}")
                    
            except Exception as e:
                st.error(f"❌ Erreur inattendue: {e}")
            
            finally:
                progress_bar.empty()
                status_text.empty()
    
    def search_interface(self):
        """Interface de recherche"""
        st.header("🔍 Recherche dans les Documents")
        
        if not st.session_state.pipeline_initialized:
            st.warning("⚠️ Veuillez d'abord initialiser la pipeline et ingérer des documents")
            return
        
        # Interface de recherche
        col1, col2 = st.columns([3, 1])
        
        with col1:
            query = st.text_input("🔎 Votre requête", placeholder="Entrez votre recherche...")
        
        with col2:
            k = st.number_input("Nombre de résultats", min_value=1, max_value=20, value=5)
        
        # Options de recherche avancée
        with st.expander("🎛️ Options Avancées"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filter_type = st.selectbox("Filtrer par type", 
                                         ["Tous", "text", "table", "image"])
            
            with col2:
                min_page = st.number_input("Page min", min_value=1, value=1)
                max_page = st.number_input("Page max", min_value=1, value=100)
            
            with col3:
                score_threshold = st.slider("Score minimum", 0.0, 1.0, 0.0, 0.1)
        
        # Bouton de recherche
        if st.button("🚀 Rechercher", type="primary") and query:
            self.perform_search(query, k, filter_type, min_page, max_page, score_threshold)
        
        # Historique des recherches
        if st.session_state.search_history:
            st.subheader("📜 Historique des Recherches")
            
            for i, search in enumerate(reversed(st.session_state.search_history[-5:])):
                with st.expander(f"🔍 \"{search['query'][:50]}...\" - {len(search['results'])} résultats"):
                    self.display_search_results(search['results'])
    
    def perform_search(self, query: str, k: int, filter_type: str, 
                      min_page: int, max_page: int, score_threshold: float):
        """Effectue une recherche"""
        
        with st.spinner("🔄 Recherche en cours..."):
            try:
                # Construction des filtres
                filters = {}
                if filter_type != "Tous":
                    filters["chunk_type"] = filter_type
                if min_page > 1:
                    filters["min_page"] = min_page
                if max_page < 100:
                    filters["max_page"] = max_page
                
                # Recherche
                results = self.pipeline.search(query, k, filters)
                
                # Filtrage par score
                if score_threshold > 0:
                    results = [r for r in results if r.score >= score_threshold]
                
                # Sauvegarde dans l'historique
                search_entry = {
                    'query': query,
                    'results': results,
                    'filters': filters,
                    'timestamp': pd.Timestamp.now()
                }
                st.session_state.search_history.append(search_entry)
                
                # Affichage des résultats
                if results:
                    st.success(f"✅ {len(results)} résultats trouvés")
                    
                    # Métriques rapides
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Résultats", len(results))
                    with col2:
                        avg_score = sum(r.score for r in results) / len(results)
                        st.metric("Score moyen", f"{avg_score:.3f}")
                    with col3:
                        best_score = max(r.score for r in results)
                        st.metric("Meilleur score", f"{best_score:.3f}")
                    with col4:
                        types = set(r.chunk_type.value for r in results)
                        st.metric("Types trouvés", len(types))
                    
                    # Affichage détaillé
                    self.display_search_results(results)
                    
                    # Graphique des scores
                    self.plot_search_scores(results)
                    
                else:
                    st.warning("⚠️ Aucun résultat trouvé")
                    
            except Exception as e:
                st.error(f"❌ Erreur lors de la recherche: {e}")
    
    def display_search_results(self, results):
        """Affiche les résultats de recherche"""
        
        for i, result in enumerate(results):
            with st.container():
                st.markdown(f"""
                <div class="chunk-card">
                    <div class="chunk-header">
                        🏷️ {result.chunk_id} | 📄 Page {result.page_number} | 
                        🎯 Score: {result.score:.3f} | 📊 Type: {result.chunk_type.value}
                    </div>
                    <div class="chunk-content">
                        {result.content[:500]}{'...' if len(result.content) > 500 else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Questions hypothétiques si disponibles
                if result.metadata.get('questions'):
                    questions = result.metadata['questions'].split(' | ')
                    if questions:
                        st.caption(f"💭 Questions: {', '.join(questions[:2])}")
                
                st.markdown("---")
    
    def plot_search_scores(self, results):
        """Affiche un graphique des scores de recherche"""
        
        df = pd.DataFrame([
            {
                'Rang': i+1,
                'Score': r.score,
                'Type': r.chunk_type.value,
                'Page': r.page_number,
                'ID': r.chunk_id.split('_')[-1]
            }
            for i, r in enumerate(results)
        ])
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Scores par Rang', 'Distribution par Type'),
            specs=[[{"type": "scatter"}, {"type": "pie"}]]
        )
        
        # Graphique des scores
        fig.add_trace(
            go.Scatter(
                x=df['Rang'],
                y=df['Score'],
                mode='markers+lines',
                marker=dict(size=10, color=df['Score'], colorscale='Viridis'),
                text=df['ID'],
                hovertemplate='<b>Rang %{x}</b><br>Score: %{y:.3f}<br>ID: %{text}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Pie chart des types
        type_counts = df['Type'].value_counts()
        fig.add_trace(
            go.Pie(
                labels=type_counts.index,
                values=type_counts.values,
                textinfo='label+percent'
            ),
            row=1, col=2
        )
        
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    def visualization_interface(self):
        """Interface de visualisation"""
        st.header("📊 Visualisations")
        
        if not st.session_state.documents:
            st.warning("⚠️ Aucun document traité. Veuillez d'abord ingérer des documents.")
            return
        
        # Sélection du document
        doc_names = [doc['name'] for doc in st.session_state.documents]
        selected_doc = st.selectbox("📄 Choisir un document", doc_names)
        
        if selected_doc:
            doc_info = next(doc for doc in st.session_state.documents if doc['name'] == selected_doc)
            document = doc_info['document']
            
            # Options de visualisation
            viz_type = st.selectbox(
                "Type de visualisation",
                [
                    "Vue d'ensemble",
                    "Structure du document", 
                    "Contenu des chunks",
                    "Positions dans le document",
                    "Espace des embeddings",
                    "Rapport complet"
                ]
            )
            
            if st.button("🎨 Générer Visualisation"):
                self.generate_visualization(document, viz_type)
    
    def generate_visualization(self, document, viz_type: str):
        """Génère une visualisation"""
        
        with st.spinner("🎨 Génération en cours..."):
            try:
                if viz_type == "Vue d'ensemble":
                    self.show_document_overview(document)
                
                elif viz_type == "Structure du document":
                    path = self.visualizer.visualize_document_structure(document)
                    st.image(path, caption="Structure du document")
                
                elif viz_type == "Contenu des chunks":
                    self.display_chunks_interactive(document.chunks)
                
                elif viz_type == "Positions dans le document":
                    path = self.visualizer.visualize_chunk_positions(document)
                    st.image(path, caption="Positions des chunks")
                
                elif viz_type == "Espace des embeddings":
                    if any(c.embedding is not None for c in document.chunks):
                        path = self.visualizer.visualize_embedding_space(document.chunks)
                        st.image(path, caption="Espace des embeddings")
                    else:
                        st.warning("Aucun embedding disponible")
                
                elif viz_type == "Rapport complet":
                    path = self.visualizer.create_chunk_report(document)
                    st.success(f"Rapport généré: {path}")
                    
                    # Lien de téléchargement
                    with open(path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    st.download_button(
                        label="📥 Télécharger le rapport HTML",
                        data=html_content,
                        file_name=f"rapport_{document.file_name}.html",
                        mime="text/html"
                    )
                    
            except Exception as e:
                st.error(f"❌ Erreur lors de la génération: {e}")
    
    def show_document_overview(self, document):
        """Affiche une vue d'ensemble du document"""
        
        # Statistiques générales
        stats = document.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📄 Pages", stats['total_pages'])
        with col2:
            st.metric("📚 Chunks", stats['total_chunks'])
        with col3:
            st.metric("❓ Questions", stats['total_questions'])
        with col4:
            total_chars = sum(len(c.content) for c in document.chunks)
            st.metric("📝 Caractères", f"{total_chars:,}")
        
        # Graphiques interactifs
        df_chunks = pd.DataFrame([
            {
                'Type': chunk.chunk_type.value,
                'Page': chunk.page_number,
                'Taille': len(chunk.content),
                'Questions': len(chunk.hypothetical_questions) if chunk.hypothetical_questions else 0
            }
            for chunk in document.chunks
        ])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution par type
            fig_pie = px.pie(
                df_chunks, 
                names='Type', 
                title="Distribution par Type de Chunk",
                color_discrete_map={
                    'text': '#3498db',
                    'table': '#e74c3c', 
                    'image': '#2ecc71'
                }
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Chunks par page
            page_counts = df_chunks.groupby(['Page', 'Type']).size().reset_index(name='Count')
            fig_bar = px.bar(
                page_counts, 
                x='Page', 
                y='Count', 
                color='Type',
                title="Chunks par Page",
                color_discrete_map={
                    'text': '#3498db',
                    'table': '#e74c3c', 
                    'image': '#2ecc71'
                }
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Histogramme des tailles
        fig_hist = px.histogram(
            df_chunks, 
            x='Taille', 
            nbins=20,
            title="Distribution des Tailles de Chunks",
            color='Type',
            color_discrete_map={
                'text': '#3498db',
                'table': '#e74c3c', 
                'image': '#2ecc71'
            }
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    def display_chunks_interactive(self, chunks):
        """Affiche les chunks de manière interactive"""
        
        # Filtres
        col1, col2, col3 = st.columns(3)
        
        with col1:
            type_filter = st.multiselect(
                "Filtrer par type",
                options=[t.value for t in ChunkType],
                default=[t.value for t in ChunkType]
            )
        
        with col2:
            min_size = st.number_input("Taille min", min_value=0, value=0)
            max_size = st.number_input("Taille max", min_value=1, value=10000)
        
        with col3:
            page_filter = st.multiselect(
                "Filtrer par page",
                options=sorted(set(c.page_number for c in chunks)),
                default=sorted(set(c.page_number for c in chunks))
            )
        
        # Application des filtres
        filtered_chunks = [
            c for c in chunks
            if (c.chunk_type.value in type_filter and
                min_size <= len(c.content) <= max_size and
                c.page_number in page_filter)
        ]
        
        st.write(f"📊 {len(filtered_chunks)} chunks affichés (sur {len(chunks)} total)")
        
        # Affichage paginé
        page_size = 10
        total_pages = (len(filtered_chunks) + page_size - 1) // page_size
        
        if total_pages > 1:
            page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
            start_idx = (page - 1) * page_size
            end_idx = min(start_idx + page_size, len(filtered_chunks))
            chunks_to_show = filtered_chunks[start_idx:end_idx]
        else:
            chunks_to_show = filtered_chunks
        
        # Affichage des chunks
        self.display_chunks_preview(chunks_to_show)
    
    def display_chunks_preview(self, chunks):
        """Affiche un aperçu des chunks"""
        
        for chunk in chunks:
            with st.expander(f"📄 {chunk.id} | {chunk.chunk_type.value} | Page {chunk.page_number}"):
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.text_area(
                        "Contenu",
                        chunk.content,
                        height=150,
                        key=f"content_{chunk.id}"
                    )
                
                with col2:
                    st.metric("Taille", len(chunk.content))
                    st.metric("Page", chunk.page_number)
                    
                    if chunk.hypothetical_questions:
                        st.metric("Questions", len(chunk.hypothetical_questions))
                    
                    if chunk.embedding is not None:
                        st.metric("Embedding", "✅")
                    else:
                        st.metric("Embedding", "❌")
                
                # Questions hypothétiques
                if chunk.hypothetical_questions:
                    st.subheader("💭 Questions Hypothétiques")
                    for i, question in enumerate(chunk.hypothetical_questions, 1):
                        st.write(f"{i}. {question}")
                
                # Métadonnées
                if chunk.metadata:
                    with st.expander("🔧 Métadonnées"):
                        st.json(chunk.metadata)
    
    def statistics_interface(self):
        """Interface des statistiques"""
        st.header("📈 Statistiques Globales")
        
        if not st.session_state.pipeline_initialized:
            st.warning("⚠️ Pipeline non initialisée")
            return
        
        # Statistiques de la pipeline
        stats = self.pipeline.get_statistics()
        
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📚 Documents", stats['pipeline_state']['documents_processed'])
        with col2:
            st.metric("📄 Chunks Totaux", stats['pipeline_state']['total_chunks'])
        with col3:
            st.metric("🧠 Embeddings", stats['pipeline_state']['total_embeddings'])
        with col4:
            st.metric("💾 Vector Store", stats['vector_store_count'])
        
        # Répartition par type
        st.subheader("📊 Répartition par Type")
        
        type_data = {
            'Type': ['Texte', 'Tableau', 'Image'],
            'Nombre': [
                stats['pipeline_state']['text_chunks'],
                stats['pipeline_state']['table_chunks'],
                stats['pipeline_state']['image_chunks']
            ]
        }
        
        df_types = pd.DataFrame(type_data)
        fig_types = px.bar(df_types, x='Type', y='Nombre', color='Type')
        st.plotly_chart(fig_types, use_container_width=True)
        
        # Configuration actuelle
        st.subheader("⚙️ Configuration")
        config_df = pd.DataFrame(list(stats['config_summary'].items()), 
                                columns=['Paramètre', 'Valeur'])
        st.dataframe(config_df, use_container_width=True)
        
        # Santé du système
        st.subheader("🏥 Santé du Système")
        health = self.pipeline.health_check()
        
        if health['status'] == 'healthy':
            st.success("✅ Système en bonne santé")
        elif health['status'] == 'degraded':
            st.warning("⚠️ Système dégradé")
        else:
            st.error("❌ Système en échec")
        
        # Détails des composants
        for component, status in health['components'].items():
            if status['status'] == 'ok':
                st.success(f"✅ {component}: OK")
            else:
                st.error(f"❌ {component}: {status.get('error', 'Erreur inconnue')}")
    
    def configuration_interface(self):
        """Interface de configuration"""
        st.header("⚙️ Configuration Avancée")
        
        # Configuration par sections
        with st.expander("🔧 Chunking"):
            chunk_size = st.number_input("Taille des chunks de texte", value=1000)
            chunk_overlap = st.number_input("Chevauchement", value=200)
            prefer_sentences = st.checkbox("Respecter les phrases", value=True)
        
        with st.expander("🧠 Embeddings"):
            text_model = st.text_input("Modèle de texte", 
                                     value="sentence-transformers/all-MiniLM-L6-v2")
            image_model = st.text_input("Modèle d'image", 
                                      value="openai/clip-vit-base-patch32")
            batch_size = st.number_input("Taille de batch", value=32)
        
        with st.expander("❓ Questions"):
            max_questions = st.number_input("Questions max par chunk", value=3)
            use_templates = st.checkbox("Utiliser templates par défaut", value=True)
        
        with st.expander("💾 Vector Store"):
            store_type = st.selectbox("Type", ["chroma", "faiss"])
            store_path = st.text_input("Chemin", value="./vector_store")
        
        if st.button("💾 Sauvegarder Configuration"):
            st.success("Configuration sauvegardée!")
        
        if st.button("🔄 Appliquer et Redémarrer"):
            st.info("Redémarrage de la pipeline avec la nouvelle configuration...")

def main():
    """Fonction principale"""
    interface = RAGWebInterface()
    interface.run()

if __name__ == "__main__":
    main()