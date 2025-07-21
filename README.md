# SOLAR NASIH - Chatbot Expert en Énergie Solaire au Maroc 🌞

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-latest-green.svg)](https://python.langchain.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📋 Description

SOLAR NASIH est un chatbot intelligent spécialisé dans l'énergie solaire, conçu spécifiquement pour le contexte marocain. Il combine les dernières technologies d'IA (LLM + RAG +SMA) pour offrir des conseils techniques, des calculs personnalisés et un accompagnement complet dans les projets d'énergie solaire.

## 🎯 Fonctionnalités Principales

### 1. **Conseiller Technique Énergétique**
- Orientation technique pour particuliers, entreprises et collectivités
- Recommandations de solutions (photovoltaïque, thermique, autoconsommation)
- Conformité aux normes marocaines (RTCM, AMEE)
- Estimation des puissances et surfaces nécessaires

### 2. **Calculateur/Estimateur Automatisé**
- Pré-diagnostics et simulations énergétiques
- Calcul ROI et économies d'énergie
- Dimensionnement de panneaux solaires
- Comparaison solutions avec/sans stockage batterie

### 3. **Assistant Réglementaire**
- Information sur les aides AMEE, IRESEN
- Procédures CNDP, DOUANE
- Exonérations fiscales et appels à projets
- Modèles de documents administratifs

### 4. **Assistant Pédagogique**
- Formation interactive pour professionnels et étudiants
- Fiches explicatives techniques
- Quiz et modules de formation
- Concepts de base et avancés

### 5. **Support Commercial**
- Création de devis types
- Comparatifs matériel (panneaux Tier 1 vs low-cost)
- Réponse aux objections clients
- Génération d'emails automatisés

### 6. **Veille Technologique**
- Résumés mensuels des nouveautés
- Analyse des rapports IEA, AMEE
- Alertes sur nouvelles normes
- Suivi des appels à projets

##  Architecture du Système

```mermaid
graph TB
    A[Utilisateur] --> B[Interface Chat]
    B --> C[Moteur de Traitement]
    C --> D[Module RAG]
    C --> E[LLM Open Source]
    D --> F[Base Vectorielle]
    F --> G[Documents PDF]
    F --> H[Sites Web Spécialisés]
    F --> I[Données Structurées]
    
    C --> J[Modules Spécialisés]
    J --> K[Calculateur Technique]
    J --> L[Assistant Réglementaire]
    J --> M[Générateur Documents]
    J --> N[Veille Technologique]
    
    E --> O[Réponse Contextualisée]
    O --> B
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
    style E fill:#ffebee
```

##  Flux de Traitement RAG

```mermaid
sequenceDiagram
    participant U as Utilisateur
    participant I as Interface
    participant R as Moteur RAG
    participant V as Base Vectorielle
    participant L as LLM
    
    U->>I: Question en langue naturelle
    I->>R: Traitement de la requête
    R->>V: Recherche vectorielle
    V->>R: Documents pertinents
    R->>L: Contexte + Question
    L->>R: Réponse générée
    R->>I: Réponse contextualisée
    I->>U: Réponse finale multilingue
```

##  Structure des Données

```mermaid
erDiagram
    DOCUMENTS {
        string id PK
        string title
        string source
        string type
        datetime created_at
        string language
    }
    
    CHUNKS {
        string id PK
        string document_id FK
        text content
        vector embedding
        int chunk_index
    }
    
    CONVERSATIONS {
        string id PK
        string user_id
        datetime timestamp
        string language
        json metadata
    }
    
    MESSAGES {
        string id PK
        string conversation_id FK
        string role
        text content
        json attachments
        datetime timestamp
    }
    
    CALCULATIONS {
        string id PK
        string conversation_id FK
        string type
        json parameters
        json results
        datetime created_at
    }
    
    DOCUMENTS ||--o{ CHUNKS : contains
    CONVERSATIONS ||--o{ MESSAGES : includes
    CONVERSATIONS ||--o{ CALCULATIONS : generates
```

##  Installation et Configuration

### Prérequis
```bash
Python 3.8+
pip install -r requirements.txt
```

### Variables d'environnement
```env
# Configuration LLM
LLM_MODEL_NAME=llama-2-7b-chat
LLM_TEMPERATURE=0.7
MAX_TOKENS=2048

# Configuration RAG
VECTOR_DB_TYPE=faiss
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=5

# Configuration multilingue
SUPPORTED_LANGUAGES=fr,ar,en,ber,ary
DEFAULT_LANGUAGE=fr

# Base de données
DATABASE_URL=postgresql://user:pass@localhost/solar_nasih
REDIS_URL=redis://localhost:6379

# APIs externes
WEATHER_API_KEY=your_weather_api_key
SOLAR_IRRADIANCE_API_KEY=your_solar_api_key
```

### Installation
```bash


# Installer les dépendances
pip install -r requirements.txt

# Configurer la base de données
python scripts/setup_db.py

# Initialiser la base vectorielle
python scripts/initialize_rag.py

# Lancer l'application
python app.py
```

##  Pipeline de Données

```mermaid
flowchart TD
    A[Sources de Données] --> B[Collecte]
    B --> C[Prétraitement]
    C --> D[Chunking]
    D --> E[Embeddings]
    E --> F[Stockage Vectoriel]
    
    A1[PDF AMEE/IRESEN] --> B
    A2[Sites Web] --> B
    A3[Documentation Technique] --> B
    A4[Réglementation] --> B
    
    C --> C1[Nettoyage Texte]
    C --> C2[Extraction Métadonnées]
    C --> C3[Détection Langue]
    
    D --> D1[Découpage Intelligent]
    D --> D2[Préservation Contexte]
    
    E --> E1[Modèle Embedding]
    E --> E2[Normalisation]
    
    F --> F1[Index FAISS]
    F --> F2[Métadonnées]
    
    style A fill:#e3f2fd
    style F fill:#e8f5e8
```

##  Support Multilingue

Le chatbot SOLAR NASIH supporte plusieurs langues :

- **Français** (fr) - Langue principale
- **Arabe littéraire** (ar) - Documentation officielle
- **Anglais** (en) - Documentation technique internationale
- **Darija** (ary) - Dialecte marocain
- **Amazigh** (ber) - Langues berbères

##  Modules Techniques

### Calculateur Solaire
```python
# Exemple d'utilisation
from solar_nasih.calculators import SolarCalculator

calc = SolarCalculator()
result = calc.estimate_system_size(
    monthly_consumption=500,  # kWh
    location="Casablanca",
    roof_area=100,  # m²
    orientation="Sud",
    inclination=30
)
```

### Assistant Réglementaire
```python
from solar_nasih.regulatory import RegulatoryAssistant

assistant = RegulatoryAssistant()
subsidies = assistant.get_available_subsidies(
    project_type="residential",
    region="Casablanca-Settat",
    capacity=5  # kW
)
```

## Métriques et Monitoring

```mermaid
graph TD
    subgraph Métriques["Tableau de Bord SOLAR NASIH"]
        A["Utilisateurs Actifs<br/>1,234"]
        B["Questions Traitées<br/>15,678"]
        C["Calculs Réalisés<br/>2,345"] 
        D["Taux de Satisfaction<br/>94.5%"]
    end

    subgraph Langues["Utilisation par Langue"]
        E["Français (45%)"]
        F["Arabe (30%)"]
        G["Anglais (15%)"]
        H["Darija (8%)"]
        I["Amazigh (2%)"]
    end

    subgraph Requêtes["Types de Requêtes"]
        J["Calculs (35%)"]
        K["Réglementaire (25%)"]
        L["Technique (20%)"]
        M["Commercial (15%)"]
        N["Formation (5%)"]
    end

    style Métriques fill:#f0f0f0,stroke:#333
    style Langues fill:#e1f5fe,stroke:#333
    style Requêtes fill:#e8f5e9,stroke:#333
```

##  Tests et Validation

### Jeux de Test
- **Tests Techniques** : Calculs de dimensionnement, ROI, économies
- **Tests Réglementaires** : Conformité RTCM, procédures AMEE
- **Tests Multilingues** : Réponses cohérentes dans toutes les langues
- **Tests de Performance** : Temps de réponse, précision RAG

### Métriques d'Évaluation
- **Précision** : Exactitude des calculs techniques
- **Pertinence** : Qualité des réponses RAG
- **Cohérence** : Uniformité multilingue
- **Satisfaction** : Feedback utilisateurs




##  Remerciements

- **AMEE** - Agence Marocaine pour l'Efficacité Énergétique
- **IRESEN** - Institut de Recherche en Énergie Solaire et Énergies Nouvelles
- **ONUDI** - Organisation des Nations Unies pour le Développement Industriel
- **IEA** - International Energy Agency

##  Support

Pour toute question ou support :
- Email : abdelilahourti@gmail.com


---

**SOLAR NASIH** - Votre expert en énergie solaire au Maroc 🇲🇦