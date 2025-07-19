from typing import Dict, Any, List
from langchain.tools import BaseTool, tool, Tool
from agents.base_agent import BaseAgent
from models.schemas import AgentType, Language
from services.gemini_service import GeminiService
from services.tavily_service import TavilyService
import logging

logger = logging.getLogger(__name__)

class CertificationAssistantAgent(BaseAgent):
    """
    Agent Assistant Certification - Accompagnement certifications et formations
    """
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.CERTIFICATION_ASSISTANT,
            description="Fournit des conseils sur la certification RGE, les démarches et la formation"
        )
        self.gemini_service = GeminiService()
        self.tavily_service = TavilyService()
        
        self.certifications = {
            "rge": {
                "organismes": {
                    "qualibat": {"code": "5911", "validite": "4 ans", "formation_continue": "7h/an"},
                    "qualifelec": {"code": "SP1", "validite": "4 ans", "formation_continue": "14h/4ans"},
                    "qualit_enr": {"code": "PV", "validite": "4 ans", "formation_continue": "7h/an"}
                },
                "prerequis": ["CAP électricité ou équivalent", "2 ans expérience", "assurance décennale"],
                "formation_duree": "3-5 jours",
                "cout_formation": "1500-2500€"
            },
            "habilitations_electriques": {
                "B1V": {"description": "Travaux hors tension BT", "recyclage": "3 ans"},
                "B2V": {"description": "Chargé de travaux BT", "recyclage": "3 ans"},
                "BR": {"description": "Intervention dépannage BT", "recyclage": "3 ans"},
                "H0B0": {"description": "Non électricien évoluant en zone électrique", "recyclage": "3 ans"}
            },
            "formations_complementaires": {
                "travail_hauteur": {"duree": "2 jours", "recyclage": "3 ans"},
                "caces_nacelle": {"duree": "3 jours", "validite": "5 ans"},
                "sauveteur_secouriste": {"duree": "2 jours", "recyclage": "2 ans"}
            }
        }
        
        self.certification_timeline = {
            "particulier_vers_pro": [
                "1. Formation électricité (CAP/BEP) - 1-2 ans",
                "2. Expérience terrain - 2 ans minimum", 
                "3. Assurance décennale - 1 mois",
                "4. Formation RGE - 1 semaine",
                "5. Audit organisme - 2-3 mois",
                "6. Obtention certification - Total: 3-4 ans"
            ],
            "electricien_vers_pv": [
                "1. Formation PV spécialisée - 3-5 jours",
                "2. Mise à jour assurance - 1 mois",
                "3. Audit organisme - 2-3 mois", 
                "4. Obtention RGE PV - Total: 4-6 mois"
            ]
        }
    
    def _init_tools(self) -> List[Tool]:
        return [
            Tool(
                name="check_certification_requirements",
                description="Vérifie les prérequis de certification",
                func=self._check_certification_requirements
            ),
            Tool(
                name="find_training_centers",
                description="Trouve les centres de formation",
                func=self._find_training_centers
            ),
            Tool(
                name="track_certification_validity",
                description="Suit la validité des certifications",
                func=self._track_certification_validity
            ),
            Tool(
                name="plan_certification_path",
                description="Planifie le parcours de certification",
                func=self._plan_certification_path
            ),
            Tool(
                name="estimate_certification_costs",
                description="Estime les coûts de certification",
                func=self._estimate_certification_costs
            ),
            Tool(
                name="find_funding_opportunities",
                description="Trouve les financements formation",
                func=self._find_funding_opportunities
            )
        ]
    
    def _get_system_prompt(self) -> str:
        return """
        Tu es l'Agent Assistant Certification du système Solar Nasih.
        
        Domaines d'expertise:
        - Certifications RGE (Reconnu Garant Environnement)
        - Qualifications électriques et habilitations
        - Formations professionnelles spécialisées
        - Maintien et renouvellement des compétences
        - Évolution réglementaire des certifications
        - Financement des formations
        
        Accompagnement personnalisé:
        - Évaluation du profil actuel
        - Choix de la certification adaptée
        - Planification du parcours formation
        - Suivi des échéances de renouvellement
        - Optimisation coûts/délais
        
        Fournis des informations précises et actualisées sur les organismes certificateurs.
        """
    
    def _check_certification_requirements(self, cert_type: str) -> str:
        """Vérifie les prérequis pour une certification"""
        cert_lower = cert_type.lower()
        
        if "rge" in cert_lower:
            rge_info = self.certifications["rge"]
            requirements = f"""
🎯 PRÉREQUIS CERTIFICATION RGE PHOTOVOLTAÏQUE

📋 CONDITIONS OBLIGATOIRES:
{chr(10).join([f"• {req}" for req in rge_info["prerequis"]])}

🏢 ORGANISMES CERTIFICATEURS:
"""
            for org, details in rge_info["organismes"].items():
                requirements += f"""
• {org.upper()}: Code {details['code']}
  - Validité: {details['validite']}
  - Formation continue: {details['formation_continue']}
"""
            
            requirements += f"""
⏱️ FORMATION INITIALE:
• Durée: {rge_info["formation_duree"]}
• Coût: {rge_info["cout_formation"]}

📚 PROGRAMME TYPE:
• Réglementation et normes (8h)
• Technologie photovoltaïque (8h)
• Dimensionnement et installation (8h)
• Maintenance et SAV (4h)
• Évaluation finale (4h)
            """
            return requirements
            
        elif "habilitation" in cert_lower or "électrique" in cert_lower:
            hab_info = self.certifications["habilitations_electriques"]
            habilitations = """
⚡ HABILITATIONS ÉLECTRIQUES POUR PV

🔧 HABILITATIONS REQUISES:
"""
            for code, details in hab_info.items():
                habilitations += f"""
• {code}: {details['description']}
  Recyclage: {details['recyclage']}
"""
            
            habilitations += """
📖 FORMATION TYPE:
• Module théorique (14h)
• Module pratique (7h) 
• Évaluation + avis médical
• Titre d'habilitation par employeur

⚠️ IMPORTANT: Habilitation ≠ Formation
L'employeur délivre l'habilitation après formation
            """
            return habilitations
            
        return f"Prérequis pour {cert_type}: analyse en cours. Spécifiez RGE ou habilitation électrique."
    
    def _find_training_centers(self, location: str) -> str:
        """Trouve les centres de formation proches"""
        training_centers = f"""
🏫 CENTRES DE FORMATION - RÉGION {location.upper()}

🎓 ORGANISMES PUBLICS:
• GRETA (Académie locale)
  - Formations RGE et habilitations
  - Financement CPF possible
  - Contact: greta-[région].fr

• CFA (Centre Formation Apprentis)
  - CAP/BEP électricité
  - Formations continues
  - Alternance possible

🏢 ORGANISMES PRIVÉS AGRÉÉS:
• AFPA (Agence Formation Professionnelle Adultes)
  - Formations métiers électricité
  - Accompagnement reconversion

• Centres spécialisés PV:
  - Tecsol Formation (Perpignan)
  - INES Education (Chambéry) 
  - Eklya School (Lyon)

🌐 FORMATION À DISTANCE:
• Modules e-learning disponibles
• Webinaires organismes certificateurs
• Classes virtuelles + stage pratique

📞 CONSEIL: Vérifiez agrément organisme certificateur
Contactez directement pour calendrier et tarifs
        """
        
        return training_centers
    
    def _track_certification_validity(self, cert_info: str) -> str:
        """Suit la validité des certifications"""
        tracking = """
📅 SUIVI VALIDITÉ CERTIFICATIONS

⏰ ÉCHÉANCES CRITIQUES:
• RGE: Renouvellement tous les 4 ans
• Habilitations électriques: Recyclage tous les 3 ans
• Travail en hauteur: Recyclage tous les 3 ans
• CACES nacelle: Renouvellement tous les 5 ans

🚨 ALERTES AUTOMATIQUES:
• 6 mois avant expiration: Planification formation
• 3 mois avant: Inscription session
• 1 mois avant: Dernière chance !

📊 FORMATION CONTINUE OBLIGATOIRE:
• Qualibat RGE: 7h/an minimum
• Qualifelec: 14h sur 4 ans
• Documentation des heures obligatoire

💡 BONNES PRATIQUES:
• Calendrier de suivi annuel
• Veille réglementaire continue
• Budget formation provisionné
• Certification backup (2 organismes)

📱 OUTILS RECOMMANDÉS:
• Apps organismes certificateurs
• Calendrier partagé équipe
• Tableau de bord formations
        """
        
        return tracking
    
    def _plan_certification_path(self, profile: str) -> str:
        """Planifie le parcours de certification selon le profil"""
        profile_lower = profile.lower()
        
        if "débutant" in profile_lower or "reconversion" in profile_lower:
            path = self.certification_timeline["particulier_vers_pro"]
            planning = f"""
🎯 PARCOURS CERTIFICATION - DÉBUTANT/RECONVERSION

📅 PLANNING COMPLET (3-4 ans):
{chr(10).join([f"{step}" for step in path])}

💰 BUDGET TOTAL ESTIMÉ:
• Formation électricité: 3,000-8,000€
• Expérience (salaire apprenti): 18,000€/an
• Assurance décennale: 1,500-3,000€/an
• Formation RGE: 2,000€
• Frais certification: 500€

🎁 FINANCEMENTS POSSIBLES:
• CPF (Compte Personnel Formation)
• Pôle Emploi (reconversion)
• Région (selon dispositifs locaux)
• Entreprise (apprentissage/contrat pro)

⚡ ACCÉLÉRATION POSSIBLE:
• VAE (Validation Acquis Expérience)
• Formation intensive
• Cumul expériences (électricité générale)
            """
            
        elif "électricien" in profile_lower:
            path = self.certification_timeline["electricien_vers_pv"]
            planning = f"""
🎯 PARCOURS CERTIFICATION - ÉLECTRICIEN EXPÉRIMENTÉ

📅 PLANNING ACCÉLÉRÉ (4-6 mois):
{chr(10).join([f"{step}" for step in path])}

💰 BUDGET RÉDUIT:
• Formation PV spécialisée: 2,000€
• Mise à jour assurance: 500€
• Frais audit: 500€
• TOTAL: ~3,000€

✅ AVANTAGES PROFIL:
• Base électricité acquise
• Habilitations déjà obtenues
• Expérience chantier
• Réseau professionnel

🚀 OPPORTUNITÉS:
• Spécialisation haute valeur
• Marché en croissance
• Diversification activité
            """
        else:
            planning = """
🎯 PARCOURS CERTIFICATION - PROFIL À PRÉCISER

📝 ÉVALUATION NÉCESSAIRE:
• Niveau actuel en électricité
• Expérience professionnelle
• Objectifs (salarié/indépendant)
• Contraintes (temps/budget)

📞 CONSEIL PERSONNALISÉ:
Contactez un conseiller formation pour:
• Bilan de compétences
• Plan de formation adapté
• Optimisation coûts/délais
            """
        
        return planning
    
    def _estimate_certification_costs(self, cert_details: str) -> str:
        """Estime les coûts de certification détaillés"""
        cost_breakdown = """
💰 ESTIMATION COÛTS CERTIFICATION RGE

📊 COÛTS DIRECTS:
• Formation initiale RGE PV: 1,500-2,500€
• Frais d'examen: 200-300€
• Audit initial: 500-800€
• Certification organisme: 300-500€
• TOTAL INITIAL: 2,500-4,100€

🔄 COÛTS RÉCURRENTS (par an):
• Formation continue: 300-500€
• Audit de surveillance: 400-600€
• Renouvellement: 200-300€
• TOTAL ANNUEL: 900-1,400€

💼 COÛTS INDIRECTS:
• Temps formation (perte activité): 1,000-2,000€
• Déplacements: 200-500€
• Hébergement: 300-600€
• Documentation: 100-200€

📈 RETOUR SUR INVESTISSEMENT:
• Accès marchés subventionnés
• Différentiation concurrentielle
• Tarifs majoration 10-20%
• Amortissement: 6-12 mois

💡 OPTIMISATIONS:
• Formation en groupe (réduction)
• CPF (jusqu'à 5,000€ pris en charge)
• OPCO (financement possible)
• Formation interne entreprise
        """
        
        return cost_breakdown
    
    def _find_funding_opportunities(self, profile: str) -> str:
        """Trouve les opportunités de financement formation"""
        funding = """
💳 FINANCEMENTS FORMATION DISPONIBLES

🎯 CPF (Compte Personnel Formation):
• Crédit: 500€/an (5,000€ max)
• Abondements possibles
• Formations éligibles certifiantes
• Démarches sur moncompteformation.gouv.fr

🏢 OPCO (Opérateurs Compétences):
• Constructys (BTP): 2,000€/an/salarié
• AFDAS (indépendants): 1,500€/an
• Plan formation entreprise
• Contrats apprentissage/professionnalisation

🏛️ PÔLE EMPLOI:
• AIF (Aide Individuelle Formation): jusqu'à 8,000€
• POEI (Préparation Opérationnelle Emploi): 9,400€
• AFC (Action Formation Conventionnée)
• Conditions: demandeur emploi

🏛️ AIDES RÉGIONALES:
• Chèque formation (500-2,000€)
• Dispositifs sectoriels BTP
• Fonds apprentissage
• Variables selon région

💼 FINANCEMENT EMPLOYEUR:
• Plan développement compétences
• CPF de transition professionnelle
• Congé formation (CIF remplacé)
• Accord branche BTP

🎓 ORGANISMES SPÉCIALISÉS:
• FAFIEC (informatique/études/conseil)
• FAFSEA (agriculture/environnement)
• UNIFAF (sanitaire/social)

📞 CONSEIL: Cumuler plusieurs dispositifs possible
Maximum prise en charge: 100% coûts pédagogiques
        """
        
        return funding
    
    def can_handle(self, user_input: str, context: Dict[str, Any] = None) -> float:
        cert_keywords = [
            "certification", "rge", "qualification", "formation", "diplôme",
            "habilitation", "qualibat", "qualifelec", "qualit'enr", "recyclage",
            "renouvellement", "cpf", "financement", "organisme", "audit"
        ]
        matches = sum(1 for kw in cert_keywords if kw in user_input.lower())
        return min(matches * 0.2, 1.0)
