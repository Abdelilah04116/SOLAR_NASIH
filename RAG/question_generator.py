"""
Générateur de questions hypothétiques pour améliorer les embeddings
"""
import logging
import re
from typing import List, Dict, Any, Optional
from collections import Counter

from models import Chunk, ChunkType
from config import QuestionGenerationConfig

logger = logging.getLogger(__name__)

class HypotheticalQuestionGenerator:
    """Génère des questions hypothétiques pour améliorer la qualité des embeddings"""
    
    def __init__(self, config: QuestionGenerationConfig):
        self.config = config
        self.max_questions = config.max_questions_per_chunk
        self.min_question_length = config.min_question_length
        self.max_question_length = config.max_question_length
        
        # Templates de questions par défaut
        self.question_templates = self._load_question_templates()
        
        # Mots vides français
        self.stop_words = {
            'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'd', 'et', 'ou', 'mais', 
            'donc', 'car', 'que', 'qui', 'quoi', 'dont', 'où', 'quand', 'comment', 'pourquoi',
            'dans', 'sur', 'avec', 'sans', 'pour', 'par', 'en', 'à', 'au', 'aux', 'ce', 'cette',
            'ces', 'son', 'sa', 'ses', 'mon', 'ma', 'mes', 'ton', 'ta', 'tes', 'notre', 'nos',
            'votre', 'vos', 'leur', 'leurs', 'il', 'elle', 'ils', 'elles', 'nous', 'vous',
            'je', 'tu', 'se', 'si', 'ne', 'pas', 'plus', 'moins', 'très', 'bien', 'mal',
            'tout', 'tous', 'toute', 'toutes', 'autre', 'autres', 'même', 'mêmes'
        }
    
    def _load_question_templates(self) -> Dict[str, List[str]]:
        """Charge les templates de questions"""
        if self.config.use_default_templates:
            return {
                ChunkType.TEXT.value: [
                    "Qu'est-ce que ce texte explique concernant {keyword}?",
                    "Quelles sont les informations principales sur {keyword}?",
                    "Comment ce passage décrit-il {keyword}?",
                    "Que peut-on apprendre sur {keyword} dans ce contenu?",
                    "Quels sont les points clés mentionnés à propos de {keyword}?",
                    "Quelle est la définition de {keyword} selon ce texte?",
                    "Comment {keyword} est-il présenté dans ce document?",
                    "Quels aspects de {keyword} sont abordés ici?",
                    "Quelle est l'importance de {keyword} dans ce contexte?",
                    "Comment comprendre {keyword} à partir de cette explication?"
                ],
                ChunkType.TABLE.value: [
                    "Quelles données sont présentées dans ce tableau?",
                    "Que montre ce tableau concernant {keyword}?",
                    "Quelles sont les valeurs principales de ce tableau?",
                    "Comment interpréter les données de ce tableau?",
                    "Quelles conclusions peut-on tirer de ce tableau?",
                    "Quelles sont les tendances visibles dans ce tableau?",
                    "Comment ce tableau compare-t-il {keyword}?",
                    "Quels sont les résultats principaux de ce tableau?",
                    "Que révèle ce tableau sur {keyword}?",
                    "Quelles métriques importantes contient ce tableau?"
                ],
                ChunkType.IMAGE.value: [
                    "Que représente cette image?",
                    "Quels éléments visuels sont visibles dans cette image?",
                    "Comment cette image illustre-t-elle le concept de {keyword}?",
                    "Que peut-on observer dans cette image?",
                    "Quels détails importants contient cette image?",
                    "Comment cette image complète-t-elle l'information sur {keyword}?",
                    "Que montre cette image en relation avec {keyword}?",
                    "Quels sont les aspects visuels de {keyword} dans cette image?",
                    "Comment cette image aide-t-elle à comprendre {keyword}?",
                    "Quelle information visuelle apporte cette image sur {keyword}?"
                ]
            }
        else:
            return self.config.custom_templates or {}
    
    def generate_questions(self, chunks: List[Chunk]) -> List[Chunk]:
        """Génère des questions hypothétiques pour tous les chunks"""
        updated_chunks = []
        
        for chunk in chunks:
            try:
                questions = self._generate_chunk_questions(chunk)
                chunk.hypothetical_questions = questions
                updated_chunks.append(chunk)
                
            except Exception as e:
                logger.warning(f"Erreur lors de la génération de questions pour chunk {chunk.id}: {e}")
                chunk.hypothetical_questions = []
                updated_chunks.append(chunk)
        
        total_questions = sum(len(c.hypothetical_questions or []) for c in updated_chunks)
        logger.info(f"Génération de questions terminée: {total_questions} questions créées pour {len(updated_chunks)} chunks")
        
        return updated_chunks
    
    def _generate_chunk_questions(self, chunk: Chunk) -> List[str]:
        """Génère des questions pour un chunk spécifique"""
        content_type = chunk.chunk_type.value
        templates = self.question_templates.get(content_type, [])
        
        if not templates:
            logger.warning(f"Aucun template trouvé pour le type: {content_type}")
            return []
        
        # Extraction des mots-clés du contenu
        keywords = self._extract_keywords(chunk.content, chunk.chunk_type)
        
        # Génération des questions
        questions = []
        
        # Questions génériques (sans mots-clés)
        generic_templates = [t for t in templates if '{keyword}' not in t]
        for template in generic_templates[:self.max_questions//2]:
            questions.append(template)
        
        # Questions avec mots-clés
        keyword_templates = [t for t in templates if '{keyword}' in t]
        if keywords and keyword_templates:
            for i, template in enumerate(keyword_templates):
                if len(questions) >= self.max_questions:
                    break
                
                # Utiliser différents mots-clés pour diversifier
                keyword_index = i % len(keywords)
                keyword = keywords[keyword_index]
                
                question = template.format(keyword=keyword)
                
                # Vérifier la longueur de la question
                if self.min_question_length <= len(question) <= self.max_question_length:
                    questions.append(question)
        
        # Questions contextuelles spécifiques
        contextual_questions = self._generate_contextual_questions(chunk)
        questions.extend(contextual_questions)
        
        # Limiter au nombre maximum et filtrer
        questions = self._filter_and_limit_questions(questions)
        
        return questions
    
    def _extract_keywords(self, text: str, chunk_type: ChunkType) -> List[str]:
        """Extrait les mots-clés pertinents du texte"""
        if chunk_type == ChunkType.IMAGE:
            return self._extract_image_keywords(text)
        elif chunk_type == ChunkType.TABLE:
            return self._extract_table_keywords(text)
        else:
            return self._extract_text_keywords(text)
    
    def _extract_text_keywords(self, text: str) -> List[str]:
        """Extrait les mots-clés d'un texte"""
        # Nettoyage du texte
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        
        # Filtrage des mots vides et des mots trop courts
        meaningful_words = [
            word for word in words 
            if len(word) > 3 and word not in self.stop_words
        ]
        
        # Comptage des fréquences
        word_freq = Counter(meaningful_words)
        
        # Sélection des mots les plus fréquents
        top_words = [word for word, freq in word_freq.most_common(10)]
        
        # Recherche d'entités nommées simples (mots en majuscules)
        entities = re.findall(r'\b[A-Z][a-zA-Z]{2,}\b', text)
        entities = [e.lower() for e in entities if e.lower() not in self.stop_words]
        
        # Combinaison et déduplication
        keywords = list(dict.fromkeys(entities + top_words))
        
        return keywords[:8]  # Limiter à 8 mots-clés
    
    def _extract_table_keywords(self, text: str) -> List[str]:
        """Extrait les mots-clés d'un tableau"""
        # Pour les tableaux, extraire les en-têtes de colonnes
        lines = text.split('\n')
        if len(lines) > 0:
            header_line = lines[0]
            # Supposer que les colonnes sont séparées par | ou des espaces
            if '|' in header_line:
                columns = [col.strip() for col in header_line.split('|')]
            else:
                columns = header_line.split()
            
            # Nettoyer les noms de colonnes
            keywords = []
            for col in columns:
                col = re.sub(r'[^\w\s]', '', col.lower().strip())
                if len(col) > 2 and col not in self.stop_words:
                    keywords.append(col)
        else:
            keywords = self._extract_text_keywords(text)
        
        return keywords[:6]
    
    def _extract_image_keywords(self, text: str) -> List[str]:
        """Extrait les mots-clés d'une description d'image"""
        # Pour les images, extraire des concepts visuels
        visual_terms = []
        
        # Recherche de termes visuels dans la description
        visual_patterns = [
            r'\b(image|photo|figure|graphique|diagramme|schéma|illustration)\b',
            r'\b(couleur|forme|taille|position|style)\b',
            r'\b(pixel|résolution|format|qualité)\b'
        ]
        
        for pattern in visual_patterns:
            matches = re.findall(pattern, text.lower())
            visual_terms.extend(matches)
        
        # Extraire aussi les mots-clés généraux
        general_keywords = self._extract_text_keywords(text)
        
        # Combiner et prioriser les termes visuels
        keywords = list(dict.fromkeys(visual_terms + general_keywords))
        
        return keywords[:5]
    
    def _generate_contextual_questions(self, chunk: Chunk) -> List[str]:
        """Génère des questions contextuelles basées sur les métadonnées"""
        questions = []
        
        # Questions basées sur la page
        if chunk.page_number:
            questions.append(f"Que contient la page {chunk.page_number} de ce document?")
        
        # Questions basées sur le type de contenu
        if chunk.chunk_type == ChunkType.TABLE:
            if 'rows' in chunk.metadata:
                rows = chunk.metadata['rows']
                questions.append(f"Que montrent ces {rows} lignes de données?")
            
            if 'columns' in chunk.metadata:
                cols = chunk.metadata['columns']
                questions.append(f"Comment interpréter ces {cols} colonnes d'information?")
        
        elif chunk.chunk_type == ChunkType.IMAGE:
            if 'width' in chunk.metadata and 'height' in chunk.metadata:
                w, h = chunk.metadata['width'], chunk.metadata['height']
                questions.append(f"Que représente cette image de {w}x{h} pixels?")
        
        # Questions basées sur la position dans le document
        if hasattr(chunk, 'start_char') and hasattr(chunk, 'end_char'):
            if chunk.start_char is not None and chunk.end_char is not None:
                length = chunk.end_char - chunk.start_char
                if length > 2000:
                    questions.append("Quels sont les points principaux de ce long passage?")
                elif length < 200:
                    questions.append("Quelle information clé contient ce court extrait?")
        
        return questions[:2]  # Limiter les questions contextuelles
    
    def _filter_and_limit_questions(self, questions: List[str]) -> List[str]:
        """Filtre et limite les questions générées"""
        # Supprimer les doublons en préservant l'ordre
        unique_questions = list(dict.fromkeys(questions))
        
        # Filtrer par longueur
        filtered_questions = [
            q for q in unique_questions 
            if self.min_question_length <= len(q) <= self.max_question_length
        ]
        
        # Limiter au nombre maximum
        return filtered_questions[:self.max_questions]
    
    def get_question_statistics(self, chunks: List[Chunk]) -> Dict[str, Any]:
        """Retourne des statistiques sur les questions générées"""
        total_questions = 0
        questions_by_type = {}
        question_lengths = []
        
        for chunk in chunks:
            if chunk.hypothetical_questions:
                chunk_type = chunk.chunk_type.value
                count = len(chunk.hypothetical_questions)
                total_questions += count
                
                questions_by_type[chunk_type] = questions_by_type.get(chunk_type, 0) + count
                
                for question in chunk.hypothetical_questions:
                    question_lengths.append(len(question))
        
        avg_length = sum(question_lengths) / len(question_lengths) if question_lengths else 0
        
        return {
            "total_questions": total_questions,
            "questions_by_type": questions_by_type,
            "average_question_length": round(avg_length, 2),
            "min_question_length": min(question_lengths) if question_lengths else 0,
            "max_question_length": max(question_lengths) if question_lengths else 0,
            "chunks_with_questions": len([c for c in chunks if c.hypothetical_questions])
        }

class SimpleQuestionGenerator:
    """Version simplifiée du générateur de questions pour des cas d'usage basiques"""
    
    def __init__(self, max_questions_per_chunk: int = 3):
        self.max_questions = max_questions_per_chunk
        
        self.simple_templates = {
            ChunkType.TEXT.value: [
                "De quoi parle ce texte?",
                "Quelles sont les informations principales?",
                "Que peut-on apprendre de ce passage?"
            ],
            ChunkType.TABLE.value: [
                "Que montre ce tableau?",
                "Quelles données contient ce tableau?",
                "Comment interpréter ce tableau?"
            ],
            ChunkType.IMAGE.value: [
                "Que représente cette image?",
                "Que peut-on voir dans cette image?",
                "Que montre cette illustration?"
            ]
        }
    
    def generate_questions(self, chunks: List[Chunk]) -> List[Chunk]:
        """Génère des questions simples pour les chunks"""
        for chunk in chunks:
            content_type = chunk.chunk_type.value
            templates = self.simple_templates.get(content_type, [])
            
            chunk.hypothetical_questions = templates[:self.max_questions]
        
        return chunks

def create_question_generator(config: QuestionGenerationConfig) -> HypotheticalQuestionGenerator:
    """Factory function pour créer un générateur de questions"""
    return HypotheticalQuestionGenerator(config)