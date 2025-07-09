"""
Module de visualisation pour les chunks et la pipeline RAG multimodal
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json
import base64
from datetime import datetime
import io

# Imports pour la visualisation
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx

# Imports du projet
from models import Chunk, Document, ChunkType, SearchResult
from config import RAGPipelineConfig

logger = logging.getLogger(__name__)

class ChunkVisualizer:
    """Visualiseur principal pour les chunks et documents"""
    
    def __init__(self, config: Optional[RAGPipelineConfig] = None):
        self.config = config or RAGPipelineConfig()
        self.output_dir = Path("./visualizations")
        self.output_dir.mkdir(exist_ok=True)
        
        # Configuration des couleurs par type de chunk
        self.chunk_colors = {
            ChunkType.TEXT: '#3498db',      # Bleu
            ChunkType.TABLE: '#e74c3c',     # Rouge
            ChunkType.IMAGE: '#2ecc71',     # Vert
            ChunkType.MIXED: '#f39c12'      # Orange
        }
        
        # Configuration matplotlib
        plt.style.use('default')
        sns.set_palette("husl")
    
    def visualize_document_structure(self, document: Document, 
                                   save_path: Optional[str] = None) -> str:
        """Visualise la structure globale d'un document"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'Structure du Document: {document.file_name}', fontsize=16, fontweight='bold')
        
        # 1. Distribution des chunks par type
        ax1 = axes[0, 0]
        chunk_types = [chunk.chunk_type.value for chunk in document.chunks]
        type_counts = pd.Series(chunk_types).value_counts()
        
        colors = [self.chunk_colors.get(ChunkType(t), '#95a5a6') for t in type_counts.index]
        wedges, texts, autotexts = ax1.pie(type_counts.values, labels=type_counts.index, 
                                          autopct='%1.1f%%', colors=colors, startangle=90)
        ax1.set_title('Distribution des Types de Chunks')
        
        # 2. Chunks par page
        ax2 = axes[0, 1]
        page_data = pd.DataFrame([
            {'page': chunk.page_number, 'type': chunk.chunk_type.value} 
            for chunk in document.chunks
        ])
        
        if not page_data.empty:
            page_counts = page_data.groupby(['page', 'type']).size().unstack(fill_value=0)
            page_counts.plot(kind='bar', stacked=True, ax=ax2, 
                           color=[self.chunk_colors.get(ChunkType(col), '#95a5a6') 
                                 for col in page_counts.columns])
            ax2.set_title('Chunks par Page')
            ax2.set_xlabel('Numéro de Page')
            ax2.set_ylabel('Nombre de Chunks')
            ax2.legend(title='Type de Chunk')
        
        # 3. Taille des chunks
        ax3 = axes[1, 0]
        chunk_sizes = [len(chunk.content) for chunk in document.chunks]
        
        ax3.hist(chunk_sizes, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        ax3.set_title('Distribution des Tailles de Chunks')
        ax3.set_xlabel('Taille (caractères)')
        ax3.set_ylabel('Fréquence')
        ax3.axvline(np.mean(chunk_sizes), color='red', linestyle='--', 
                   label=f'Moyenne: {np.mean(chunk_sizes):.0f}')
        ax3.legend()
        
        # 4. Timeline des chunks (si métadonnées temporelles disponibles)
        ax4 = axes[1, 1]
        if all(hasattr(chunk, 'created_at') for chunk in document.chunks):
            chunk_times = [chunk.created_at for chunk in document.chunks]
            chunk_types_time = [chunk.chunk_type.value for chunk in document.chunks]
            
            time_df = pd.DataFrame({
                'time': chunk_times,
                'type': chunk_types_time
            }).sort_values('time')
            
            for i, chunk_type in enumerate(time_df['type'].unique()):
                type_data = time_df[time_df['type'] == chunk_type]
                ax4.scatter(type_data['time'], [i] * len(type_data), 
                           label=chunk_type, s=50, alpha=0.7,
                           color=self.chunk_colors.get(ChunkType(chunk_type), '#95a5a6'))
            
            ax4.set_title('Timeline de Création des Chunks')
            ax4.set_xlabel('Temps de Création')
            ax4.set_ylabel('Type de Chunk')
            ax4.legend()
        else:
            ax4.text(0.5, 0.5, 'Pas de données temporelles disponibles', 
                    ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title('Timeline de Création des Chunks')
        
        plt.tight_layout()
        
        # Sauvegarde
        if save_path is None:
            save_path = self.output_dir / f"document_structure_{document.file_hash[:8]}.png"
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Visualisation de structure sauvegardée: {save_path}")
        return str(save_path)
    
    def visualize_chunk_content(self, chunks: List[Chunk], 
                              max_chunks: int = 10,
                              save_path: Optional[str] = None) -> str:
        """Visualise le contenu détaillé des chunks"""
        chunks_to_show = chunks[:max_chunks]
        
        fig, ax = plt.subplots(figsize=(14, 2 * len(chunks_to_show)))
        
        y_positions = range(len(chunks_to_show))
        
        for i, chunk in enumerate(chunks_to_show):
            y = len(chunks_to_show) - i - 1
            
            # Couleur selon le type
            color = self.chunk_colors.get(chunk.chunk_type, '#95a5a6')
            
            # Barre représentant le chunk
            chunk_length = len(chunk.content)
            normalized_length = min(chunk_length / 1000, 10)  # Normaliser pour l'affichage
            
            rect = patches.Rectangle((0, y - 0.4), normalized_length, 0.8, 
                                   linewidth=1, edgecolor='black', 
                                   facecolor=color, alpha=0.7)
            ax.add_patch(rect)
            
            # Texte du chunk (tronqué)
            preview_text = chunk.content[:100] + "..." if len(chunk.content) > 100 else chunk.content
            preview_text = preview_text.replace('\n', ' ')
            
            # Informations du chunk
            chunk_info = f"ID: {chunk.id} | Type: {chunk.chunk_type.value} | Page: {chunk.page_number} | Taille: {chunk_length}"
            
            ax.text(0.1, y + 0.1, chunk_info, fontsize=9, fontweight='bold')
            ax.text(0.1, y - 0.1, preview_text, fontsize=8, style='italic')
            
            # Questions hypothétiques si disponibles
            if chunk.hypothetical_questions:
                questions_text = " | ".join(chunk.hypothetical_questions[:2])
                ax.text(0.1, y - 0.3, f"Questions: {questions_text}", fontsize=7, color='gray')
        
        ax.set_xlim(0, 12)
        ax.set_ylim(-0.5, len(chunks_to_show) - 0.5)
        ax.set_ylabel('Chunks')
        ax.set_xlabel('Taille Normalisée')
        ax.set_title(f'Contenu Détaillé des Chunks (Top {len(chunks_to_show)})')
        
        # Légende des types
        legend_elements = [patches.Patch(color=color, label=chunk_type.value) 
                          for chunk_type, color in self.chunk_colors.items()]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        
        # Sauvegarde
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = self.output_dir / f"chunk_content_{timestamp}.png"
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Visualisation de contenu sauvegardée: {save_path}")
        return str(save_path)
    
    def visualize_chunk_positions(self, document: Document, 
                                save_path: Optional[str] = None) -> str:
        """Visualise les positions des chunks dans le document (vue page par page)"""
        pages = sorted(set(chunk.page_number for chunk in document.chunks))
        
        fig, axes = plt.subplots(len(pages), 1, figsize=(12, 3 * len(pages)))
        if len(pages) == 1:
            axes = [axes]
        
        fig.suptitle(f'Position des Chunks par Page - {document.file_name}', fontsize=14)
        
        for page_idx, page_num in enumerate(pages):
            ax = axes[page_idx]
            
            # Chunks de cette page
            page_chunks = [c for c in document.chunks if c.page_number == page_num]
            
            # Simulation d'une page A4 (210x297mm)
            page_width, page_height = 210, 297
            
            for chunk in page_chunks:
                # Position simulée basée sur l'ordre et le type
                if hasattr(chunk, 'bbox') and chunk.bbox:
                    # Utiliser la vraie bbox si disponible
                    x, y, w, h = chunk.bbox
                    # Normaliser aux dimensions de la page
                    x = (x / 612) * page_width  # 612 points = largeur PDF standard
                    y = (y / 792) * page_height  # 792 points = hauteur PDF standard
                    w = (w / 612) * page_width
                    h = (h / 792) * page_height
                else:
                    # Position simulée
                    chunk_idx = page_chunks.index(chunk)
                    x = 10 + (chunk_idx % 2) * 90
                    y = 10 + (chunk_idx // 2) * 30
                    w = 80
                    h = 25
                
                color = self.chunk_colors.get(chunk.chunk_type, '#95a5a6')
                
                rect = patches.Rectangle((x, y), w, h, linewidth=1, 
                                       edgecolor='black', facecolor=color, alpha=0.6)
                ax.add_patch(rect)
                
                # Texte du chunk ID
                ax.text(x + w/2, y + h/2, chunk.id.split('_')[-1], 
                       ha='center', va='center', fontsize=8, fontweight='bold')
            
            ax.set_xlim(0, page_width)
            ax.set_ylim(0, page_height)
            ax.set_aspect('equal')
            ax.set_title(f'Page {page_num} ({len(page_chunks)} chunks)')
            ax.set_xlabel('Position X')
            ax.set_ylabel('Position Y')
        
        # Légende
        legend_elements = [patches.Patch(color=color, label=chunk_type.value) 
                          for chunk_type, color in self.chunk_colors.items()]
        plt.figlegend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        
        # Sauvegarde
        if save_path is None:
            save_path = self.output_dir / f"chunk_positions_{document.file_hash[:8]}.png"
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Visualisation des positions sauvegardée: {save_path}")
        return str(save_path)
    
    def create_interactive_chunk_explorer(self, document: Document, 
                                        save_path: Optional[str] = None) -> str:
        """Crée une visualisation interactive avec Plotly"""
        
        # Préparer les données
        chunk_data = []
        for chunk in document.chunks:
            chunk_data.append({
                'id': chunk.id,
                'type': chunk.chunk_type.value,
                'page': chunk.page_number,
                'size': len(chunk.content),
                'content_preview': chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                'questions_count': len(chunk.hypothetical_questions) if chunk.hypothetical_questions else 0,
                'has_embedding': chunk.embedding is not None,
                'created_at': chunk.created_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(chunk, 'created_at') else 'N/A'
            })
        
        df = pd.DataFrame(chunk_data)
        
        # Créer les sous-graphiques
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Distribution par Type', 'Taille vs Page', 
                          'Chunks par Page', 'Questions Générées'),
            specs=[[{"type": "pie"}, {"type": "scatter"}],
                   [{"type": "bar"}, {"type": "histogram"}]]
        )
        
        # 1. Pie chart des types
        type_counts = df['type'].value_counts()
        colors = [self.chunk_colors.get(ChunkType(t), '#95a5a6') for t in type_counts.index]
        
        fig.add_trace(
            go.Pie(labels=type_counts.index, values=type_counts.values,
                   marker_colors=colors, name="Types"),
            row=1, col=1
        )
        
        # 2. Scatter plot taille vs page
        for chunk_type in df['type'].unique():
            type_data = df[df['type'] == chunk_type]
            fig.add_trace(
                go.Scatter(x=type_data['page'], y=type_data['size'],
                          mode='markers', name=chunk_type,
                          marker=dict(color=self.chunk_colors.get(ChunkType(chunk_type), '#95a5a6'),
                                    size=8, opacity=0.7),
                          text=type_data['content_preview'],
                          hovertemplate='<b>%{text}</b><br>Page: %{x}<br>Taille: %{y}<extra></extra>'),
                row=1, col=2
            )
        
        # 3. Bar chart chunks par page
        page_counts = df.groupby(['page', 'type']).size().unstack(fill_value=0)
        for chunk_type in page_counts.columns:
            fig.add_trace(
                go.Bar(x=page_counts.index, y=page_counts[chunk_type],
                      name=chunk_type, 
                      marker_color=self.chunk_colors.get(ChunkType(chunk_type), '#95a5a6')),
                row=2, col=1
            )
        
        # 4. Histogramme des questions
        fig.add_trace(
            go.Histogram(x=df['questions_count'], name="Questions",
                        marker_color='lightblue'),
            row=2, col=2
        )
        
        # Mise à jour du layout
        fig.update_layout(
            title_text=f"Exploration Interactive - {document.file_name}",
            title_x=0.5,
            height=800,
            showlegend=True
        )
        
        # Sauvegarde
        if save_path is None:
            save_path = self.output_dir / f"interactive_explorer_{document.file_hash[:8]}.html"
        
        fig.write_html(save_path)
        
        logger.info(f"Explorateur interactif sauvegardé: {save_path}")
        return str(save_path)
    
    def visualize_embedding_space(self, chunks: List[Chunk], 
                                method: str = "umap",
                                save_path: Optional[str] = None) -> str:
        """Visualise l'espace des embeddings en 2D"""
        
        # Filtrer les chunks avec embeddings
        chunks_with_embeddings = [c for c in chunks if c.embedding is not None]
        
        if len(chunks_with_embeddings) < 3:
            logger.warning("Pas assez de chunks avec embeddings pour la visualisation")
            return ""
        
        # Extraire les embeddings
        embeddings = np.array([chunk.embedding for chunk in chunks_with_embeddings])
        
        # Réduction de dimensionnalité
        if method.lower() == "umap":
            try:
                import umap
                reducer = umap.UMAP(n_components=2, random_state=42)
                embedding_2d = reducer.fit_transform(embeddings)
            except ImportError:
                logger.warning("UMAP non disponible, utilisation de PCA")
                method = "pca"
        
        if method.lower() == "pca":
            from sklearn.decomposition import PCA
            reducer = PCA(n_components=2, random_state=42)
            embedding_2d = reducer.fit_transform(embeddings)
        
        elif method.lower() == "tsne":
            from sklearn.manifold import TSNE
            reducer = TSNE(n_components=2, random_state=42, perplexity=min(30, len(chunks_with_embeddings)-1))
            embedding_2d = reducer.fit_transform(embeddings)
        
        # Créer la visualisation
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Points colorés par type
        for chunk_type in set(chunk.chunk_type for chunk in chunks_with_embeddings):
            mask = [chunk.chunk_type == chunk_type for chunk in chunks_with_embeddings]
            type_embeddings = embedding_2d[mask]
            
            color = self.chunk_colors.get(chunk_type, '#95a5a6')
            ax.scatter(type_embeddings[:, 0], type_embeddings[:, 1], 
                      c=color, label=chunk_type.value, alpha=0.7, s=50)
        
        # Annotations pour quelques points
        for i, chunk in enumerate(chunks_with_embeddings[:10]):  # Limiter les annotations
            ax.annotate(chunk.id.split('_')[-1], 
                       (embedding_2d[i, 0], embedding_2d[i, 1]),
                       xytext=(5, 5), textcoords='offset points', 
                       fontsize=8, alpha=0.7)
        
        ax.set_title(f'Espace des Embeddings ({method.upper()})')
        ax.set_xlabel('Dimension 1')
        ax.set_ylabel('Dimension 2')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Sauvegarde
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = self.output_dir / f"embedding_space_{method}_{timestamp}.png"
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Visualisation d'embeddings sauvegardée: {save_path}")
        return str(save_path)
    
    def create_chunk_report(self, document: Document, 
                          save_path: Optional[str] = None) -> str:
        """Crée un rapport HTML complet avec toutes les visualisations"""
        
        # Générer toutes les visualisations
        struct_path = self.visualize_document_structure(document)
        content_path = self.visualize_chunk_content(document.chunks)
        position_path = self.visualize_chunk_positions(document)
        interactive_path = self.create_interactive_chunk_explorer(document)
        
        if document.chunks and any(c.embedding is not None for c in document.chunks):
            embedding_path = self.visualize_embedding_space(document.chunks)
        else:
            embedding_path = None
        
        # Statistiques détaillées
        stats = self._calculate_detailed_stats(document)
        
        # Générer le HTML
        html_content = self._generate_html_report(
            document, stats, struct_path, content_path, 
            position_path, interactive_path, embedding_path
        )
        
        # Sauvegarde
        if save_path is None:
            save_path = self.output_dir / f"chunk_report_{document.file_hash[:8]}.html"
        
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Rapport complet sauvegardé: {save_path}")
        return str(save_path)
    
    def _calculate_detailed_stats(self, document: Document) -> Dict[str, Any]:
        """Calcule des statistiques détaillées"""
        chunks = document.chunks
        
        stats = {
            'total_chunks': len(chunks),
            'total_characters': sum(len(c.content) for c in chunks),
            'avg_chunk_size': np.mean([len(c.content) for c in chunks]) if chunks else 0,
            'median_chunk_size': np.median([len(c.content) for c in chunks]) if chunks else 0,
            'chunks_by_type': {},
            'chunks_by_page': {},
            'questions_stats': {},
            'embedding_stats': {}
        }
        
        # Par type
        for chunk_type in ChunkType:
            type_chunks = [c for c in chunks if c.chunk_type == chunk_type]
            stats['chunks_by_type'][chunk_type.value] = {
                'count': len(type_chunks),
                'avg_size': np.mean([len(c.content) for c in type_chunks]) if type_chunks else 0,
                'total_chars': sum(len(c.content) for c in type_chunks)
            }
        
        # Par page
        pages = set(c.page_number for c in chunks)
        for page in pages:
            page_chunks = [c for c in chunks if c.page_number == page]
            stats['chunks_by_page'][page] = len(page_chunks)
        
        # Questions
        total_questions = sum(len(c.hypothetical_questions or []) for c in chunks)
        chunks_with_questions = len([c for c in chunks if c.hypothetical_questions])
        
        stats['questions_stats'] = {
            'total_questions': total_questions,
            'chunks_with_questions': chunks_with_questions,
            'avg_questions_per_chunk': total_questions / len(chunks) if chunks else 0
        }
        
        # Embeddings
        chunks_with_embeddings = len([c for c in chunks if c.embedding is not None])
        stats['embedding_stats'] = {
            'chunks_with_embeddings': chunks_with_embeddings,
            'embedding_coverage': chunks_with_embeddings / len(chunks) if chunks else 0
        }
        
        return stats
    
    def _generate_html_report(self, document: Document, stats: Dict[str, Any],
                            struct_path: str, content_path: str, position_path: str,
                            interactive_path: str, embedding_path: Optional[str]) -> str:
        """Génère le rapport HTML"""
        
        html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Rapport de Chunks - {document.file_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1, h2 {{ color: #2c3e50; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
                .stat-card {{ background: #ecf0f1; padding: 15px; border-radius: 8px; text-align: center; }}
                .stat-value {{ font-size: 2em; font-weight: bold; color: #3498db; }}
                .stat-label {{ color: #7f8c8d; margin-top: 5px; }}
                .visualization {{ margin: 30px 0; text-align: center; }}
                .visualization img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 5px; }}
                .info-section {{ background: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #3498db; color: white; }}
                .chunk-preview {{ max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 Rapport d'Analyse des Chunks</h1>
                
                <div class="info-section">
                    <h3>Informations du Document</h3>
                    <p><strong>Nom:</strong> {document.file_name}</p>
                    <p><strong>Pages:</strong> {document.total_pages}</p>
                    <p><strong>Hash:</strong> {document.file_hash[:16]}...</p>
                    <p><strong>Statut:</strong> {document.processing_status.value}</p>
                    <p><strong>Dernière mise à jour:</strong> {document.last_updated.strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
                
                <h2>📈 Statistiques Globales</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{stats['total_chunks']}</div>
                        <div class="stat-label">Chunks Totaux</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{stats['total_characters']:,}</div>
                        <div class="stat-label">Caractères Totaux</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{stats['avg_chunk_size']:.0f}</div>
                        <div class="stat-label">Taille Moyenne</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{stats['questions_stats']['total_questions']}</div>
                        <div class="stat-label">Questions Générées</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{stats['embedding_stats']['embedding_coverage']:.1%}</div>
                        <div class="stat-label">Couverture Embeddings</div>
                    </div>
                </div>
                
                <h2>🏗️ Structure du Document</h2>
                <div class="visualization">
                    <img src="{Path(struct_path).name}" alt="Structure du document">
                </div>
                
                <h2>📝 Contenu des Chunks</h2>
                <div class="visualization">
                    <img src="{Path(content_path).name}" alt="Contenu des chunks">
                </div>
                
                <h2>📍 Positions dans le Document</h2>
                <div class="visualization">
                    <img src="{Path(position_path).name}" alt="Positions des chunks">
                </div>
                
                {f'''<h2>🔍 Espace des Embeddings</h2>
                <div class="visualization">
                    <img src="{Path(embedding_path).name}" alt="Espace des embeddings">
                </div>''' if embedding_path else ''}
                
                <h2>🎯 Exploration Interactive</h2>
                <div class="info-section">
                    <p>Une version interactive de cette analyse est disponible: 
                    <a href="{Path(interactive_path).name}" target="_blank">Ouvrir l'explorateur interactif</a></p>
                </div>
                
                <h2>📋 Détails par Type de Chunk</h2>
                <table>
                    <tr>
                        <th>Type</th>
                        <th>Nombre</th>
                        <th>Taille Moyenne</th>
                        <th>Caractères Totaux</th>
                        <th>Pourcentage</th>
                    </tr>
        """
        
        for chunk_type, type_stats in stats['chunks_by_type'].items():
            if type_stats['count'] > 0:
                percentage = (type_stats['count'] / stats['total_chunks']) * 100
                html += f"""
                    <tr>
                        <td>{chunk_type}</td>
                        <td>{type_stats['count']}</td>
                        <td>{type_stats['avg_size']:.0f}</td>
                        <td>{type_stats['total_chars']:,}</td>
                        <td>{percentage:.1f}%</td>
                    </tr>
                """
        
        html += """
                </table>
                
                <h2>📄 Distribution par Page</h2>
                <table>
                    <tr>
                        <th>Page</th>
                        <th>Nombre de Chunks</th>
                    </tr>
        """
        
        for page, count in sorted(stats['chunks_by_page'].items()):
            html += f"""
                    <tr>
                        <td>Page {page}</td>
                        <td>{count}</td>
                    </tr>
            """
        
        # Liste des chunks individuels
        html += """
                </table>
                
                <h2>📑 Liste Détaillée des Chunks</h2>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Type</th>
                        <th>Page</th>
                        <th>Taille</th>
                        <th>Questions</th>
                        <th>Aperçu</th>
                    </tr>
        """
        
        for chunk in document.chunks[:50]:  # Limiter à 50 chunks pour la performance
            questions_count = len(chunk.hypothetical_questions) if chunk.hypothetical_questions else 0
            preview = chunk.content[:100].replace('\n', ' ').replace('\r', '') + "..." if len(chunk.content) > 100 else chunk.content
            
            html += f"""
                    <tr>
                        <td>{chunk.id}</td>
                        <td>{chunk.chunk_type.value}</td>
                        <td>{chunk.page_number}</td>
                        <td>{len(chunk.content)}</td>
                        <td>{questions_count}</td>
                        <td class="chunk-preview">{preview}</td>
                    </tr>
            """
        
        html += """
                </table>
                
                <div class="info-section">
                    <h3>💡 Notes</h3>
                    <ul>
                        <li>Ce rapport a été généré automatiquement par la pipeline RAG multimodal</li>
                        <li>Les visualisations montrent la structure et la distribution des chunks extraits</li>
                        <li>L'explorateur interactif permet une analyse plus approfondie</li>
                        <li>Les embeddings permettent de mesurer la similarité sémantique entre chunks</li>
                    </ul>
                </div>
                
                <footer style="text-align: center; margin-top: 50px; color: #7f8c8d;">
                    <p>Généré le {datetime.now().strftime("%Y-%m-%d à %H:%M:%S")}</p>
                </footer>
            </div>
        </body>
        </html>
        """
        
        return html

class SearchResultVisualizer:
    """Visualiseur pour les résultats de recherche"""
    
    def __init__(self):
        self.output_dir = Path("./search_visualizations")
        self.output_dir.mkdir(exist_ok=True)
    
    def visualize_search_results(self, query: str, results: List[SearchResult], 
                                save_path: Optional[str] = None) -> str:
        """Visualise les résultats de recherche"""
        
        if not results:
            logger.warning("Aucun résultat à visualiser")
            return ""
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle(f'Résultats de Recherche: "{query}"', fontsize=16, fontweight='bold')
        
        # 1. Scores de pertinence
        ax1 = axes[0, 0]
        scores = [r.score for r in results]
        chunk_ids = [r.chunk_id.split('_')[-1] for r in results]
        
        bars = ax1.bar(range(len(scores)), scores, color='skyblue', alpha=0.7)
        ax1.set_title('Scores de Pertinence')
        ax1.set_xlabel('Rang du Résultat')
        ax1.set_ylabel('Score')
        ax1.set_xticks(range(len(scores)))
        ax1.set_xticklabels(chunk_ids, rotation=45)
        
        # Annotations des scores
        for i, (bar, score) in enumerate(zip(bars, scores)):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{score:.3f}', ha='center', va='bottom', fontsize=9)
        
        # 2. Distribution par type
        ax2 = axes[0, 1]
        types = [r.chunk_type.value for r in results]
        type_counts = pd.Series(types).value_counts()
        
        chunk_colors = {
            'text': '#3498db',
            'table': '#e74c3c', 
            'image': '#2ecc71'
        }
        colors = [chunk_colors.get(t, '#95a5a6') for t in type_counts.index]
        
        wedges, texts, autotexts = ax2.pie(type_counts.values, labels=type_counts.index,
                                          autopct='%1.1f%%', colors=colors, startangle=90)
        ax2.set_title('Distribution par Type de Chunk')
        
        # 3. Pages sources
        ax3 = axes[1, 0]
        pages = [r.page_number for r in results]
        page_counts = pd.Series(pages).value_counts().sort_index()
        
        ax3.bar(page_counts.index, page_counts.values, color='lightcoral', alpha=0.7)
        ax3.set_title('Distribution par Page Source')
        ax3.set_xlabel('Numéro de Page')
        ax3.set_ylabel('Nombre de Résultats')
        
        # 4. Heatmap score vs rang
        ax4 = axes[1, 1]
        
        # Créer une matrice pour la heatmap
        matrix_data = []
        for i, result in enumerate(results):
            matrix_data.append([i+1, result.score, result.page_number, len(result.content)])
        
        if matrix_data:
            df_matrix = pd.DataFrame(matrix_data, columns=['Rang', 'Score', 'Page', 'Taille'])
            
            # Heatmap des corrélations
            corr_matrix = df_matrix.corr()
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=ax4)
            ax4.set_title('Corrélations entre Métriques')
        
        plt.tight_layout()
        
        # Sauvegarde
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = self.output_dir / f"search_results_{timestamp}.png"
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Visualisation de recherche sauvegardée: {save_path}")
        return str(save_path)
    
    def create_search_comparison(self, queries_results: Dict[str, List[SearchResult]],
                               save_path: Optional[str] = None) -> str:
        """Compare les résultats de plusieurs recherches"""
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle('Comparaison de Recherches Multiples', fontsize=16, fontweight='bold')
        
        # 1. Scores moyens par requête
        ax1 = axes[0, 0]
        query_names = list(queries_results.keys())
        avg_scores = [np.mean([r.score for r in results]) if results else 0 
                     for results in queries_results.values()]
        
        bars = ax1.bar(range(len(query_names)), avg_scores, color='lightgreen', alpha=0.7)
        ax1.set_title('Scores Moyens par Requête')
        ax1.set_xlabel('Requêtes')
        ax1.set_ylabel('Score Moyen')
        ax1.set_xticks(range(len(query_names)))
        ax1.set_xticklabels([q[:20] + "..." if len(q) > 20 else q for q in query_names], 
                           rotation=45, ha='right')
        
        # 2. Nombre de résultats par requête
        ax2 = axes[0, 1]
        result_counts = [len(results) for results in queries_results.values()]
        
        ax2.bar(range(len(query_names)), result_counts, color='orange', alpha=0.7)
        ax2.set_title('Nombre de Résultats par Requête')
        ax2.set_xlabel('Requêtes')
        ax2.set_ylabel('Nombre de Résultats')
        ax2.set_xticks(range(len(query_names)))
        ax2.set_xticklabels([q[:20] + "..." if len(q) > 20 else q for q in query_names],
                           rotation=45, ha='right')
        
        # 3. Distribution des types agrégée
        ax3 = axes[1, 0]
        all_types = []
        for results in queries_results.values():
            all_types.extend([r.chunk_type.value for r in results])
        
        if all_types:
            type_counts = pd.Series(all_types).value_counts()
            chunk_colors = {'text': '#3498db', 'table': '#e74c3c', 'image': '#2ecc71'}
            colors = [chunk_colors.get(t, '#95a5a6') for t in type_counts.index]
            
            wedges, texts, autotexts = ax3.pie(type_counts.values, labels=type_counts.index,
                                              autopct='%1.1f%%', colors=colors, startangle=90)
            ax3.set_title('Distribution Globale par Type')
        
        # 4. Box plot des scores
        ax4 = axes[1, 1]
        score_data = []
        labels = []
        
        for query, results in queries_results.items():
            if results:
                scores = [r.score for r in results]
                score_data.append(scores)
                labels.append(query[:15] + "..." if len(query) > 15 else query)
        
        if score_data:
            ax4.boxplot(score_data, labels=labels)
            ax4.set_title('Distribution des Scores par Requête')
            ax4.set_xlabel('Requêtes')
            ax4.set_ylabel('Scores')
            ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Sauvegarde
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = self.output_dir / f"search_comparison_{timestamp}.png"
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Comparaison de recherches sauvegardée: {save_path}")
        return str(save_path)

class PipelineMonitor:
    """Moniteur pour visualiser les performances de la pipeline"""
    
    def __init__(self):
        self.output_dir = Path("./monitoring")
        self.output_dir.mkdir(exist_ok=True)
        self.metrics_history = []
    
    def log_processing_metrics(self, document: Document, processing_time: float, 
                             chunks_created: int, embeddings_generated: int):
        """Enregistre les métriques de traitement"""
        metrics = {
            'timestamp': datetime.now(),
            'document_name': document.file_name,
            'pages': document.total_pages,
            'processing_time': processing_time,
            'chunks_created': chunks_created,
            'embeddings_generated': embeddings_generated,
            'chunks_per_second': chunks_created / processing_time if processing_time > 0 else 0,
            'characters_processed': sum(len(c.content) for c in document.chunks)
        }
        
        self.metrics_history.append(metrics)
    
    def create_performance_dashboard(self, save_path: Optional[str] = None) -> str:
        """Crée un dashboard de performance"""
        
        if not self.metrics_history:
            logger.warning("Aucune métrique disponible pour le dashboard")
            return ""
        
        df = pd.DataFrame(self.metrics_history)
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        fig.suptitle('Dashboard de Performance de la Pipeline', fontsize=16, fontweight='bold')
        
        # 1. Temps de traitement par document
        ax1 = axes[0, 0]
        ax1.plot(df.index, df['processing_time'], marker='o', color='blue', alpha=0.7)
        ax1.set_title('Temps de Traitement par Document')
        ax1.set_xlabel('Document #')
        ax1.set_ylabel('Temps (secondes)')
        ax1.grid(True, alpha=0.3)
        
        # 2. Chunks créés par document
        ax2 = axes[0, 1]
        ax2.bar(df.index, df['chunks_created'], color='green', alpha=0.7)
        ax2.set_title('Chunks Créés par Document')
        ax2.set_xlabel('Document #')
        ax2.set_ylabel('Nombre de Chunks')
        
        # 3. Vitesse de traitement
        ax3 = axes[0, 2]
        ax3.plot(df.index, df['chunks_per_second'], marker='s', color='red', alpha=0.7)
        ax3.set_title('Vitesse de Traitement')
        ax3.set_xlabel('Document #')
        ax3.set_ylabel('Chunks/seconde')
        ax3.grid(True, alpha=0.3)
        
        # 4. Distribution des temps de traitement
        ax4 = axes[1, 0]
        ax4.hist(df['processing_time'], bins=10, color='skyblue', alpha=0.7, edgecolor='black')
        ax4.set_title('Distribution des Temps de Traitement')
        ax4.set_xlabel('Temps (secondes)')
        ax4.set_ylabel('Fréquence')
        
        # 5. Relation taille vs temps
        ax5 = axes[1, 1]
        ax5.scatter(df['characters_processed'], df['processing_time'], alpha=0.7, color='purple')
        ax5.set_title('Caractères vs Temps de Traitement')
        ax5.set_xlabel('Caractères Traités')
        ax5.set_ylabel('Temps (secondes)')
        
        # Ligne de tendance
        z = np.polyfit(df['characters_processed'], df['processing_time'], 1)
        p = np.poly1d(z)
        ax5.plot(df['characters_processed'], p(df['characters_processed']), "r--", alpha=0.8)
        
        # 6. Efficacité des embeddings
        ax6 = axes[1, 2]
        embedding_efficiency = df['embeddings_generated'] / df['chunks_created']
        ax6.plot(df.index, embedding_efficiency, marker='^', color='orange', alpha=0.7)
        ax6.set_title('Efficacité des Embeddings')
        ax6.set_xlabel('Document #')
        ax6.set_ylabel('Ratio Embeddings/Chunks')
        ax6.set_ylim(0, 1.1)
        ax6.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Sauvegarde
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = self.output_dir / f"performance_dashboard_{timestamp}.png"
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Dashboard de performance sauvegardé: {save_path}")
        return str(save_path)

# Fonctions utilitaires pour l'intégration facile

def visualize_document(document: Document, output_dir: str = "./visualizations") -> Dict[str, str]:
    """Fonction utilitaire pour visualiser un document complet"""
    visualizer = ChunkVisualizer()
    visualizer.output_dir = Path(output_dir)
    visualizer.output_dir.mkdir(exist_ok=True)
    
    results = {}
    
    try:
        results['structure'] = visualizer.visualize_document_structure(document)
        results['content'] = visualizer.visualize_chunk_content(document.chunks)
        results['positions'] = visualizer.visualize_chunk_positions(document)
        results['interactive'] = visualizer.create_interactive_chunk_explorer(document)
        results['report'] = visualizer.create_chunk_report(document)
        
        if any(c.embedding is not None for c in document.chunks):
            results['embeddings'] = visualizer.visualize_embedding_space(document.chunks)
        
        logger.info(f"Visualisations créées dans {output_dir}")
        
    except Exception as e:
        logger.error(f"Erreur lors de la visualisation: {e}")
    
    return results

def visualize_search_results(query: str, results: List[SearchResult], 
                           output_dir: str = "./search_visualizations") -> str:
    """Fonction utilitaire pour visualiser des résultats de recherche"""
    visualizer = SearchResultVisualizer()
    visualizer.output_dir = Path(output_dir)
    visualizer.output_dir.mkdir(exist_ok=True)
    
    return visualizer.visualize_search_results(query, results)

def create_quick_preview(chunks: List[Chunk], max_chunks: int = 20) -> str:
    """Crée un aperçu rapide des chunks en mode texte"""
    preview = f"=== Aperçu de {len(chunks)} chunks ===\n\n"
    
    type_counts = {}
    total_chars = 0
    
    for chunk in chunks[:max_chunks]:
        chunk_type = chunk.chunk_type.value
        type_counts[chunk_type] = type_counts.get(chunk_type, 0) + 1
        total_chars += len(chunk.content)
        
        preview += f"📄 {chunk.id}\n"
        preview += f"   Type: {chunk_type} | Page: {chunk.page_number} | Taille: {len(chunk.content)} chars\n"
        preview += f"   Contenu: {chunk.content[:100]}{'...' if len(chunk.content) > 100 else ''}\n"
        
        if chunk.hypothetical_questions:
            preview += f"   Questions: {len(chunk.hypothetical_questions)} générées\n"
        
        preview += "\n"
    
    if len(chunks) > max_chunks:
        preview += f"... et {len(chunks) - max_chunks} chunks supplémentaires\n\n"
    
    preview += f"Statistiques:\n"
    preview += f"  Total: {len(chunks)} chunks\n"
    preview += f"  Caractères: {total_chars:,}\n"
    preview += f"  Types: {dict(type_counts)}\n"
    
    return preview