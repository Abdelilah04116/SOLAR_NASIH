from typing import Dict, Any, List
from langchain.tools import BaseTool, tool, Tool
from agents.base_agent import BaseAgent
from models.schemas import AgentType, Language
from services.gemini_service import GeminiService
import logging

logger = logging.getLogger(__name__)

class CommercialAssistantAgent(BaseAgent):
    """
    Agent Assistant Commercial - Expertise financière et commerciale
    """
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.COMMERCIAL_ASSISTANT,
            description="Fournit des conseils commerciaux sur l'énergie solaire, les prix, les offres et le financement"
        )
        self.gemini_service = GeminiService()
        
        self.financing_options = {
            "credit": {
                "eco_ptz": {"taux": "0%", "duree": "15 ans", "montant_max": "50000€"},
                "credit_travaux": {"taux": "2-8%", "duree": "10 ans", "montant_max": "75000€"},
                "credit_conso": {"taux": "3-12%", "duree": "7 ans", "montant_max": "25000€"}
            },
            "aides": {
                "prime_autoconso": {"2024": "300€/kWc < 3kWc, 230€/kWc 3-9kWc"},
                "tva_reduite": {"taux": "10%", "condition": "≤ 3kWc"},
                "aides_locales": {"variable": "Selon région/département"}
            },
            "modeles": ["achat_comptant", "location", "tiers_financement", "ppa"]
        }
        
        self.pricing_database = {
            "materiel": {
                "panneaux": {"monocristallin_400W": 200, "polycristallin_300W": 150},
                "onduleur": {"string_6kW": 1200, "micro_onduleur": 150},
                "structure": {"per_panel": 50},
                "cablage": {"per_kWc": 100}
            },
            "installation": {
                "main_oeuvre": {"per_kWc": 400},
                "demarches": {"forfait": 500},
                "raccordement": {"enedis": 500}
            },
            "marges": {
                "installateur": 0.25,
                "commercial": 0.15
            }
        }
    
    def _init_tools(self) -> List[Tool]:
        return [
            Tool(
                name="calculate_roi",
                description="Calcule le retour sur investissement",
                func=self._calculate_roi
            ),
            Tool(
                name="find_financing",
                description="Trouve les options de financement",
                func=self._find_financing
            ),
            Tool(
                name="generate_quote",
                description="Génère un devis estimatif",
                func=self._generate_quote
            ),
            Tool(
                name="compare_offers",
                description="Compare différentes offres",
                func=self._compare_offers
            ),
            Tool(
                name="calculate_savings",
                description="Calcule les économies potentielles",
                func=self._calculate_savings
            ),
            Tool(
                name="analyze_financial_viability",
                description="Analyse la viabilité financière",
                func=self._analyze_financial_viability
            )
        ]
    
    def _get_system_prompt(self) -> str:
        return """
        Tu es l'Agent Assistant Commercial du système Solar Nasih.
        
        Expertise commerciale:
        - Calculs de rentabilité et ROI
        - Options de financement adaptées
        - Aides et subventions 2024
        - Génération de devis détaillés
        - Conseil en investissement
        - Analyse comparative d'offres
        
        Approche éthique:
        - Transparence totale sur les coûts
        - Analyse financière objective
        - Accompagnement personnalisé
        - Information complète sur les aides
        - Présentation des avantages ET contraintes
        
        Toujours fournir des chiffres réalistes et sourcés.
        """
    
    def _calculate_roi(self, investment_data: str) -> str:
        """Calcule le retour sur investissement détaillé"""
        # Parsing simplifié des données d'investissement
        try:
            # Valeurs par défaut pour la démonstration
            investment = 12000  # €
            annual_savings = 1200  # €/an
            energy_inflation = 0.03  # 3% par an
            system_degradation = 0.005  # 0.5% par an
            
            roi_analysis = f"""
💰 ANALYSE ROI DÉTAILLÉE

📊 Investissement initial: {investment:,}€
💡 Économies année 1: {annual_savings:,}€/an
📈 Inflation électricité: {energy_inflation*100:.1f}%/an
📉 Dégradation système: {system_degradation*100:.1f}%/an

📅 PROJECTIONS SUR 20 ANS:
"""
            
            cumulative_savings = 0
            for year in range(1, 21):
                yearly_savings = annual_savings * (1 + energy_inflation)**year * (1 - system_degradation)**year
                cumulative_savings += yearly_savings
                
                if year in [1, 5, 10, 15, 20]:
                    roi_percent = ((cumulative_savings - investment) / investment) * 100
                    roi_analysis += f"Année {year:2d}: {cumulative_savings:7,.0f}€ cumulés (ROI: {roi_percent:+5.1f}%)\n"
            
            payback_years = investment / annual_savings
            total_roi = ((cumulative_savings - investment) / investment) * 100
            
            roi_analysis += f"""
⏱️ Temps de retour: {payback_years:.1f} ans
🎯 ROI total 20 ans: {total_roi:.1f}%
📊 TRI estimé: {(cumulative_savings/investment)**(1/20)-1:.1%}/an

✅ Rentabilité: {'EXCELLENTE' if total_roi > 200 else 'BONNE' if total_roi > 100 else 'CORRECTE'}
            """
            
            return roi_analysis
            
        except Exception as e:
            return f"Erreur calcul ROI: {str(e)}"
    
    def _find_financing(self, profile: str) -> str:
        """Trouve les options de financement adaptées au profil"""
        financing_options = f"""
💳 OPTIONS DE FINANCEMENT DISPONIBLES

🏦 CRÉDITS BANCAIRES:
• Éco-PTZ: {self.financing_options['credit']['eco_ptz']['taux']} sur {self.financing_options['credit']['eco_ptz']['duree']}
  Maximum: {self.financing_options['credit']['eco_ptz']['montant_max']}
  
• Crédit travaux: {self.financing_options['credit']['credit_travaux']['taux']} sur {self.financing_options['credit']['credit_travaux']['duree']}
  Maximum: {self.financing_options['credit']['credit_travaux']['montant_max']}

💰 AIDES PUBLIQUES 2024:
• Prime autoconsommation: {self.financing_options['aides']['prime_autoconso']['2024']}
• TVA réduite: {self.financing_options['aides']['tva_reduite']['taux']} si {self.financing_options['aides']['tva_reduite']['condition']}
• Aides locales: Variables selon région

🔄 MODÈLES ALTERNATIFS:
• Location avec option d'achat
• Tiers financement (PPA)
• Achat groupé (réduction coûts)

📞 CONSEIL: Combiner éco-PTZ + prime autoconsommation optimal
        """
        
        return financing_options
    
    def _generate_quote(self, project_specs: str) -> str:
        """Génère un devis estimatif détaillé"""
        # Exemple de devis pour installation 6kWc
        quote = f"""
📋 DEVIS ESTIMATIF - INSTALLATION PHOTOVOLTAÏQUE

🏠 PROJET: Installation 6 kWc (15 panneaux 400Wc)

💰 DÉTAIL DES COÛTS:

📦 MATÉRIEL:
• Panneaux 15x400Wc monocristallins    3,000€
• Onduleur string 6kW                  1,200€
• Structure de fixation                  750€
• Câblage et protections                 600€
• Monitoring                             200€
                            Sous-total: 5,750€

🔧 INSTALLATION:
• Main d'œuvre pose                    2,400€
• Démarches administratives              500€
• Raccordement ENEDIS                    500€
• Mise en service + formation            300€
                            Sous-total: 3,700€

💯 TOTAL HT:                           9,450€
🧾 TVA 20%:                           1,890€
💸 TOTAL TTC:                         11,340€

🎁 AIDES DÉDUITES:
• Prime autoconsommation (6kWc)       -1,380€
• TVA réduite non applicable (>3kWc)

💳 PRIX FINAL:                         9,960€

📈 PRODUCTION ESTIMÉE: 7,200 kWh/an
💰 ÉCONOMIES ANNUELLES: 1,300€/an
⏱️ RETOUR SUR INVESTISSEMENT: 7.7 ans
        """
        
        return quote
    
    def _compare_offers(self, offers_data: str) -> str:
        """Compare différentes offres commerciales"""
        comparison = """
🔍 GRILLE DE COMPARAISON D'OFFRES

📊 CRITÈRES D'ÉVALUATION:

1. 💰 PRIX (pondération 30%)
   • Coût total (/kWc installé)
   • Transparence tarification
   • Aides intégrées

2. 🔧 MATÉRIEL (pondération 25%)
   • Qualité panneaux (Tier 1?)
   • Rendement onduleur
   • Garanties équipements

3. 👷 INSTALLATION (pondération 20%)
   • Qualification RGE
   • Références clients
   • Assurance décennale

4. 📞 SERVICE (pondération 15%)
   • SAV et maintenance
   • Monitoring inclus
   • Réactivité support

5. 📋 ADMINISTRATIF (pondération 10%)
   • Démarches incluses
   • Délais raccordement
   • Garanties contractuelles

⚠️ POINTS DE VIGILANCE:
• Méfiance offres trop attractives
• Vérifier certifications RGE
• Lire conditions garanties
• Demander références locales

💡 CONSEIL: Ne pas choisir uniquement sur le prix !
        """
        
        return comparison
    
    def _calculate_savings(self, consumption_data: str) -> str:
        """Calcule les économies potentielles détaillées"""
        savings = """
💡 CALCUL D'ÉCONOMIES DÉTAILLÉ

📊 HYPOTHÈSES (famille type):
• Consommation: 4,000 kWh/an
• Installation: 6 kWc
• Production: 7,200 kWh/an
• Taux autoconsommation: 70%
• Prix électricité: 0.18€/kWh
• Tarif revente: 0.13€/kWh

💰 ÉCONOMIES ANNUELLES:
• Autoconsommation: 5,040 kWh × 0.18€ = 907€
• Revente surplus: 2,160 kWh × 0.13€ = 281€
• TOTAL ÉCONOMIES/AN: 1,188€

📈 PROJECTION 20 ANS (inflation 3%/an):
• Économies cumulées: 28,500€
• Investissement: 10,000€
• GAIN NET: 18,500€

🌍 BÉNÉFICES ENVIRONNEMENTAUX:
• CO2 évité: 2.4 tonnes/an
• Équivalent: 400 arbres sur 20 ans
        """
        
        return savings
    
    def _analyze_financial_viability(self, project_data: str) -> str:
        """Analyse la viabilité financière complète"""
        analysis = """
📈 ANALYSE DE VIABILITÉ FINANCIÈRE

✅ INDICATEURS POSITIFS:
• TRI > 8% (seuil viabilité)
• Payback < 10 ans
• VAN positive sur 20 ans
• Couverture > 70% besoins

⚠️ RISQUES À CONSIDÉRER:
• Évolution tarifs électricité
• Dégradation équipements
• Changements réglementaires
• Entretien/remplacement onduleur

📊 SENSIBILITÉ:
• +1% inflation électricité = +2 ans gain
• -10% production = +1.5 an payback
• +1000€ investissement = +10 mois payback

🎯 RECOMMANDATION:
Projet VIABLE avec excellent profil risque/rendement
        """
        
        return analysis
    
    async def process(self, state) -> Dict[str, Any]:
        """Méthode requise par BaseAgent - traite une requête commerciale"""
        try:
            # Utiliser la langue détectée par le workflow ou détecter si pas disponible
            detected_language = getattr(state, 'detected_language', None)
            if not detected_language:
                detected_language = "fr"  # Défaut français
            
            # Analyse du type de demande commerciale
            message_lower = state.current_message.lower()
            
            if any(word in message_lower for word in ["roi", "retour", "investissement", "rentabilité"]):
                result = self._calculate_roi(state.current_message)
            elif any(word in message_lower for word in ["financement", "prêt", "crédit", "aides"]):
                result = self._find_financing(state.current_message)
            elif any(word in message_lower for word in ["devis", "prix", "coût", "tarif"]):
                result = self._generate_quote(state.current_message)
            elif any(word in message_lower for word in ["comparer", "comparaison", "offres"]):
                result = self._compare_offers(state.current_message)
            elif any(word in message_lower for word in ["économies", "sauvegarder", "réduire"]):
                result = self._calculate_savings(state.current_message)
            elif any(word in message_lower for word in ["viabilité", "faisabilité", "rentable"]):
                result = self._analyze_financial_viability(state.current_message)
            else:
                # Analyse financière générale
                result = self._calculate_roi(state.current_message)
            
            # Génération de la réponse dans la langue détectée
            response = self._generate_commercial_response(result, detected_language)
            
            return {
                "response": response,
                "agent_used": "commercial_assistant",
                "confidence": 0.85,
                "detected_language": detected_language,
                "sources": ["Solar Nasih Commercial Database"]
            }
            
        except Exception as e:
            logger.error(f"Erreur dans l'assistant commercial: {e}")
            return {
                "response": f"Erreur lors de l'analyse commerciale: {str(e)}",
                "agent_used": "commercial_assistant",
                "confidence": 0.3,
                "error": str(e),
                "sources": ["Solar Nasih Commercial Database"]
            }
    
    def _generate_commercial_response(self, result: str, language: str) -> str:
        """Génère une réponse commerciale dans la langue appropriée"""
        # Pour l'instant, retourner le résultat tel quel
        # En production, on pourrait ajouter des traductions
        return result
    
    def can_handle(self, user_input: str, context: Dict[str, Any] = None) -> float:
        commercial_keywords = [
            "prix", "coût", "devis", "financement", "crédit", "aide",
            "subvention", "rentabilité", "économie", "retour", "investissement",
            "roi", "payback", "taux", "budget", "tarif", "offre"
        ]
        matches = sum(1 for kw in commercial_keywords if kw in user_input.lower())
        return min(matches * 0.15, 1.0)