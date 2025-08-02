from typing import Dict, Any, List
from langchain.tools import BaseTool, tool
from agents.base_agent import BaseAgent
from models.schemas import AgentType, Language
from services.gemini_service import GeminiService
import logging
from datetime import datetime
import json
from langchain.tools import Tool

logger = logging.getLogger(__name__)

class DocumentGeneratorAgent(BaseAgent):
    """
    Agent Générateur de Documents - Création de documents professionnels
    """
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.DOCUMENT_GENERATOR,
            description="Génère des documents administratifs, techniques et commerciaux pour les projets solaires"
        )
        self.gemini_service = GeminiService()
        
        self.document_templates = {
            "devis": {
                "sections": ["en_tete", "client", "projet", "materiel", "installation", "prix", "conditions"],
                "format": "PDF",
                "duree_validite": "30 jours"
            },
            "rapport_etude": {
                "sections": ["synthese", "analyse_site", "dimensionnement", "production", "financier", "planning"],
                "format": "PDF + annexes",
                "pages": "15-25 pages"
            },
            "contrat": {
                "sections": ["parties", "objet", "specifications", "prix", "planning", "garanties", "clauses"],
                "format": "PDF signable",
                "mentions_legales": "obligatoires"
            },
            "attestation": {
                "sections": ["identification", "installation", "conformite", "mise_en_service", "garanties"],
                "format": "PDF officiel",
                "validite": "permanente"
            },
            "fiche_technique": {
                "sections": ["equipement", "caracteristiques", "installation", "maintenance", "securite"],
                "format": "PDF + QR code",
                "mise_a_jour": "automatique"
            }
        }
        
        self.legal_mentions = {
            "devis": [
                "Devis valable 30 jours",
                "TVA applicable selon réglementation",
                "Acompte 30% à la commande",
                "Solde à la réception des travaux",
                "Garantie décennale incluse"
            ],
            "contrat": [
                "Délai de rétractation 14 jours",
                "Assurance décennale obligatoire",
                "Garantie parfait achèvement 1 an",
                "Garantie équipements selon fabricant",
                "Clause de révision prix si > 3 mois"
            ]
        }
    
    def _init_tools(self) -> List[Tool]:
        return [
            Tool(
                name="generate_quote_document",
                description="Génère un document de devis",
                func=self._generate_quote_document
            ),
            Tool(
                name="create_technical_report",
                description="Crée un rapport technique",
                func=self._create_technical_report
            ),
            Tool(
                name="generate_contract",
                description="Génère un contrat",
                func=self._generate_contract
            ),
            Tool(
                name="create_certificate",
                description="Crée une attestation",
                func=self._create_certificate
            ),
            Tool(
                name="generate_technical_sheet",
                description="Génère une fiche technique",
                func=self._generate_technical_sheet
            ),
            Tool(
                name="customize_template",
                description="Personnalise un template",
                func=self._customize_template
            )
        ]
    
    def _get_system_prompt(self) -> str:
        return """
        Tu es l'Agent Générateur de Documents du système Solar Nasih.
        
        Types de documents professionnels:
        - Devis commerciaux détaillés et conformes
        - Rapports d'étude technique complets
        - Contrats d'installation sécurisés
        - Attestations et certificats officiels
        - Fiches techniques produits
        - Documents administratifs
        
        Standards de qualité:
        - Mise en forme professionnelle impeccable
        - Respect strict des mentions légales
        - Données techniques précises et vérifiées
        - Clarté et lisibilité optimales
        - Adaptation au destinataire
        
        Personnalisation automatique:
        - Logo et charte graphique entreprise
        - Coordonnées et certifications
        - Conditions générales spécifiques
        - Signatures électroniques possibles
        
        Toujours inclure les mentions légales obligatoires.
        """
    
    def _generate_quote_document(self, quote_data: str) -> str:
        """Génère un document de devis détaillé"""
        quote_document = """
📄 DEVIS PHOTOVOLTAÏQUE GÉNÉRÉ

═══════════════════════════════════════════════════════
                    ENTREPRISE SOLAR PRO
              123 Avenue du Soleil, 69000 Lyon
                 Tél: 04.XX.XX.XX.XX
               Email: contact@solarpro.fr
                   RGE Qualibat 5911
═══════════════════════════════════════════════════════

📅 DEVIS N°: DEV-2024-001                 Date: 15/01/2024
👤 CLIENT: M. et Mme DUPONT
🏠 ADRESSE: 456 Rue de la Paix, 69100 Villeurbanne

═══════════════════════════════════════════════════════
                      OBJET DU DEVIS
═══════════════════════════════════════════════════════

Installation photovoltaïque 6 kWc en intégration au bâti
Autoconsommation avec revente du surplus

═══════════════════════════════════════════════════════
                    DÉTAIL DE L'OFFRE
═══════════════════════════════════════════════════════

📦 MATÉRIEL FOURNI:
• 15 panneaux photovoltaïques 400Wc          3,000.00€
  (Monocristallins, garantie 25 ans)
• 1 onduleur string 6kW avec monitoring       1,200.00€
  (Garantie fabricant 10 ans)
• Structure de fixation aluminium               750.00€
• Câblage DC et protections                     400.00€
• Coffret de protection AC                      200.00€
• Compteur de production                        150.00€
                                    Sous-total: 5,700.00€

🔧 INSTALLATION ET SERVICES:
• Main d'œuvre pose et raccordement          2,400.00€
• Démarches administratives complètes          500.00€
• Mise en service et formation                  300.00€
• Garantie main d'œuvre 10 ans                   0.00€
                                    Sous-total: 3,200.00€

═══════════════════════════════════════════════════════
                      RÉCAPITULATIF
═══════════════════════════════════════════════════════

💰 Total HT:                                8,900.00€
🧾 TVA 20%:                                 1,780.00€
💸 Total TTC:                              10,680.00€

🎁 AIDES DÉDUITES:
• Prime autoconsommation 6kWc               -1,380.00€
💳 PRIX NET À PAYER:                        9,300.00€

═══════════════════════════════════════════════════════
              PERFORMANCE ET RENTABILITÉ
═══════════════════════════════════════════════════════

📈 Production annuelle estimée: 7,200 kWh
💡 Taux d'autoconsommation: 70%
💰 Économies annuelles: 1,100€
⏱️ Retour sur investissement: 8.5 ans
🌍 CO2 évité: 2.3 tonnes/an

═══════════════════════════════════════════════════════
                    CONDITIONS
═══════════════════════════════════════════════════════

• Devis valable 30 jours à compter de ce jour
• Acompte de 30% à la signature
• Solde à la réception des travaux
• Délai d'exécution: 4-6 semaines
• Garantie décennale incluse

        """
        
        return quote_document
    
    def _create_technical_report(self, project_data: str) -> str:
        """Crée un rapport technique complet"""
        technical_report = """
📋 RAPPORT D'ÉTUDE TECHNIQUE PHOTOVOLTAÏQUE

═══════════════════════════════════════════════════════
                      SYNTHÈSE EXÉCUTIVE
═══════════════════════════════════════════════════════

🎯 PROJET: Installation 6kWc autoconsommation
📍 LOCALISATION: Lyon (69100)
🏠 TYPE: Maison individuelle, toiture tuiles
✅ FAISABILITÉ: Excellente (score: 9/10)

═══════════════════════════════════════════════════════
                    ANALYSE DU SITE
═══════════════════════════════════════════════════════

🏠 CARACTÉRISTIQUES BÂTIMENT:
• Surface toiture: 80 m²
• Orientation: Sud-Sud/Est (-15°)
• Inclinaison: 32°
• Ombrage: Minimal (cheminée)
• État toiture: Bon (réfection 2018)

🌤️ DONNÉES MÉTÉOROLOGIQUES:
• Irradiation Lyon: 1,300 kWh/m²/an
• Heures équivalent plein soleil: 1,300h
• Température moyenne: 13°C
• Coefficient correction site: 0.95

═══════════════════════════════════════════════════════
                    DIMENSIONNEMENT
═══════════════════════════════════════════════════════

⚡ INSTALLATION PROPOSÉE:
• Puissance: 6.0 kWc
• Panneaux: 15 × 400Wc monocristallins
• Surface panneaux: 30 m²
• Onduleur: 6kW string

📊 CALCULS DE PRODUCTION:
• Production théorique: 6.0 kWc × 1,300h = 7,800 kWh
• Pertes système: -8% = 7,176 kWh
• Production réelle estimée: 7,200 kWh/an

🔌 RÉPARTITION ÉNERGÉTIQUE:
• Autoconsommation (70%): 5,040 kWh
• Injection réseau (30%): 2,160 kWh
• Taux de couverture besoins: 85%

═══════════════════════════════════════════════════════
                   ANALYSE FINANCIÈRE
═══════════════════════════════════════════════════════

💰 INVESTISSEMENT:
• Coût total TTC: 10,680€
• Prime autoconsommation: -1,380€
• Investissement net: 9,300€

📈 RENTABILITÉ:
• Économies année 1: 1,100€
• TRI 20 ans: 9.2%
• VAN 20 ans: 8,450€
• Temps de retour: 8.5 ans

═══════════════════════════════════════════════════════
                      PLANNING
═══════════════════════════════════════════════════════

📅 ÉTAPES RÉALISATION:
1. Signature contrat: J0
2. Démarches administratives: J+7
3. Commande matériel: J+14
4. Installation: J+30 à J+32
5. Raccordement ENEDIS: J+45
6. Mise en service: J+60

═══════════════════════════════════════════════════════
                   RECOMMANDATIONS
═══════════════════════════════════════════════════════

✅ POINTS FORTS:
• Exposition optimale
• Toiture en excellent état
• Consommation adaptée
• Rentabilité attractive

⚠️ POINTS D'ATTENTION:
• Optimiser consommation diurne
• Prévoir maintenance préventive
• Surveiller ombrage évolutif

🎯 CONCLUSION:
Projet hautement recommandé avec excellent potentiel
de rentabilité et d'autoconsommation.

        """
        
        return technical_report
    
    def _generate_contract(self, contract_data: str) -> str:
        """Génère un contrat d'installation"""
        contract = """
📜 CONTRAT D'INSTALLATION PHOTOVOLTAÏQUE

═══════════════════════════════════════════════════════
                        PARTIES
═══════════════════════════════════════════════════════

🏢 ENTREPRISE: SOLAR PRO SARL
Capital: 50,000€ - SIRET: 123 456 789 00012
RGE Qualibat 5911 - Assurance Allianz Police n°XXX

👤 CLIENT: M. Jean DUPONT & Mme Marie DUPONT
Adresse: 456 Rue de la Paix, 69100 Villeurbanne

═══════════════════════════════════════════════════════
                    OBJET DU CONTRAT
═══════════════════════════════════════════════════════

Installation complète système photovoltaïque 6kWc
selon devis DEV-2024-001 du 15/01/2024

═══════════════════════════════════════════════════════
                   SPÉCIFICATIONS TECHNIQUES
═══════════════════════════════════════════════════════

📦 MATÉRIEL INSTALLÉ:
• 15 panneaux photovoltaïques 400Wc garantie 25 ans
• 1 onduleur 6kW garantie fabricant 10 ans
• Structure fixation alu garantie 10 ans
• Câblage et protections conformes NF C 15-100

🔧 PRESTATIONS INCLUSES:
• Étude technique préalable
• Fourniture et pose complète
• Raccordement électrique
• Démarches administratives
• Formation utilisation
• Mise en service

═══════════════════════════════════════════════════════
                    CONDITIONS FINANCIÈRES
═══════════════════════════════════════════════════════

💰 PRIX TOTAL: 9,300€ TTC (après déduction prime)

💳 MODALITÉS PAIEMENT:
• Acompte signature: 30% = 2,790€
• Acompte livraison matériel: 40% = 3,720€
• Solde réception travaux: 30% = 2,790€

═══════════════════════════════════════════════════════
                        PLANNING
═══════════════════════════════════════════════════════

📅 DÉLAIS CONTRACTUELS:
• Début travaux: maximum 6 semaines après signature
• Durée installation: 3 jours ouvrés
• Mise en service: sous 8 semaines

⚠️ PÉNALITÉS RETARD: 0.1% prix TTC par jour

═══════════════════════════════════════════════════════
                        GARANTIES
═══════════════════════════════════════════════════════

🛡️ GARANTIES ACCORDÉES:
• Garantie décennale: dommages compromettant solidité
• Garantie parfait achèvement: 1 an toutes malfaçons
• Garantie bon fonctionnement: 2 ans équipements
• Garantie fabricants: selon conditions constructeurs

📞 SERVICE APRÈS-VENTE: 7j/7 intervention sous 48h

═══════════════════════════════════════════════════════
                    CLAUSES PARTICULIÈRES
═══════════════════════════════════════════════════════

🏠 OBLIGATIONS CLIENT:
• Accès libre au chantier
• Alimentation électrique 220V disponible
• Évacuation gravats non comprise
• Assurance habitation à jour

⚡ OBLIGATIONS ENTREPRISE:
• Respect normes en vigueur
• Personnel qualifié RGE
• Nettoyage fin de chantier
• Attestation conformité Consuel

═══════════════════════════════════════════════════════
                    MENTIONS LÉGALES
═══════════════════════════════════════════════════════

📋 DISPOSITIONS LÉGALES:
• Délai rétractation: 14 jours calendaires
• Médiation consommation: www.medicationconso.fr
• Juridiction compétente: Tribunal de Lyon
• Loi applicable: française

✍️ SIGNATURES:

Date: ___/___/2024

L'ENTREPRISE:                    LE CLIENT:
[Signature + Cachet]            [Signature précédée de]
                                "Lu et approuvé"

        """
        
        return contract
    
    def _create_certificate(self, cert_data: str) -> str:
        """Crée une attestation ou certificat"""
        certificate = """
🏆 ATTESTATION DE CONFORMITÉ

═══════════════════════════════════════════════════════
              ATTESTATION DE MISE EN SERVICE
           INSTALLATION PHOTOVOLTAÏQUE
═══════════════════════════════════════════════════════

📋 INSTALLATION:
• N° dossier: INS-2024-001
• Date mise en service: 15/03/2024
• Localisation: 456 Rue de la Paix, 69100 Villeurbanne
• Propriétaire: M. et Mme DUPONT

⚡ CARACTÉRISTIQUES TECHNIQUES:
• Puissance installée: 6.00 kWc
• Nombre de panneaux: 15 modules 400Wc
• Onduleur: 1 × 6kW string
• Type raccordement: Autoconsommation avec vente surplus

🔍 CONTRÔLES EFFECTUÉS:
✅ Conformité installation électrique NF C 15-100
✅ Résistance isolement > 1MΩ
✅ Continuité masses et liaisons équipotentielles
✅ Fonctionnement protections différentielles
✅ Test déclenchement onduleur
✅ Vérification étiquetage et signalisation
✅ Contrôle fixations mécaniques
✅ Mesure production initiale: 3.2 kW (conditions test)

📊 PRODUCTION PREMIÈRE SEMAINE:
• Production totale: 145 kWh
• Performance ratio: 98%
• Fonctionnement nominal confirmé

🏢 ENTREPRISE INSTALLATRICE:
SOLAR PRO SARL - RGE Qualibat 5911
Technicien certifié: Jean MARTIN
Assurance décennale: Allianz Police n°XXX

📅 GARANTIES APPLICABLES:
• Garantie installation: 10 ans
• Garantie panneaux: 25 ans produit, 25 ans performance
• Garantie onduleur: 10 ans fabricant
• Garantie décennale: dommages solidité/étanchéité

✍️ CERTIFICATION:
Je soussigné Jean MARTIN, technicien RGE, certifie que
l'installation photovoltaïque décrite ci-dessus est
conforme aux normes en vigueur et fonctionne normalement.

Date: 15/03/2024
Signature: [Signature technicien]
Cachet entreprise: [Cachet SOLAR PRO]

═══════════════════════════════════════════════════════
Cette attestation fait foi pour toutes démarches
administratives et demandes de garantie.
═══════════════════════════════════════════════════════

        """
        
        return certificate
    
    def _generate_technical_sheet(self, equipment_data: str) -> str:
        """Génère une fiche technique équipement"""
        tech_sheet = """
📘 FICHE TECHNIQUE INSTALLATION

═══════════════════════════════════════════════════════
           PANNEAU PHOTOVOLTAÏQUE 400Wc
              Référence: SPM-400-MC
═══════════════════════════════════════════════════════

⚡ CARACTÉRISTIQUES ÉLECTRIQUES (STC):
• Puissance nominale: 400 Wc
• Tension circuit ouvert (Voc): 49.2 V
• Courant court-circuit (Isc): 10.8 A
• Tension MPP (Vmpp): 40.8 V
• Courant MPP (Impp): 9.8 A
• Rendement: 20.6%

🌡️ COEFFICIENTS TEMPÉRATURE:
• Puissance: -0.38%/°C
• Tension: -0.29%/°C
• Courant: +0.048%/°C
• NOCT: 42±2°C

📏 DIMENSIONS PHYSIQUES:
• Longueur × Largeur: 2,094 × 1,038 mm
• Épaisseur: 35 mm
• Poids: 22.5 kg
• Cellules: 144 (6×24) monocristallines

🏗️ CONSTRUCTION:
• Verre face avant: 3.2mm trempé anti-reflet
• Encapsulant: EVA haute transparence
• Face arrière: Backsheet blanc
• Cadre: Aluminium anodisé
• Boîte de jonction: IP67, 3 diodes bypass

🛡️ CERTIFICATIONS:
• IEC 61215:2016 (Type approval)
• IEC 61730-1&2:2016 (Safety)
• UL 61730 (US safety)
• CE marking conformity

🌦️ CONDITIONS UTILISATION:
• Température: -40°C à +85°C
• Charge vent: 2400 Pa (face avant)
• Charge neige: 5400 Pa (face arrière)
• Impact grêle: 25mm à 23 m/s

🔧 INSTALLATION:
• Fixation: 4 points sur cadre
• Espacement: minimum 10mm entre modules
• Mise à terre: via cadre aluminium
• Orientation: ±15° optimal

⚠️ SÉCURITÉ:
• Risque électrocution en présence lumière
• Porter EPI lors manipulation
• Éviter ombrage partiel (point chaud)
• Ne pas marcher sur les panneaux

📞 SUPPORT TECHNIQUE:
• Hotline: 0800 XXX XXX
• Email: support@manufacturer.com
• Documentation: www.manufacturer.com/support

═══════════════════════════════════════════════════════
QR Code documentation complète: [QR CODE]
═══════════════════════════════════════════════════════

        """
        
        return tech_sheet
    
    def _customize_template(self, template_data: str) -> str:
        """Personnalise un template selon les besoins"""
        customization = """
🎨 PERSONNALISATION TEMPLATE DISPONIBLE

═══════════════════════════════════════════════════════
                    OPTIONS DE PERSONNALISATION
═══════════════════════════════════════════════════════

🏢 IDENTITÉ ENTREPRISE:
• Logo haute définition (formats: PNG, SVG)
• Charte graphique couleurs
• Coordonnées complètes
• Certifications et agréments
• Signature électronique

📄 MISE EN FORME:
• Police corporate (Arial, Calibri, custom)
• Couleurs thème (primaire, secondaire, accent)
• Layout adaptatif (A4, US Letter)
• En-têtes et pieds de page personnalisés

📋 CONTENU MODULAIRE:
• Sections standard ou custom
• Clauses spécifiques métier
• Conditions générales entreprise
• Tarification automatique
• Calculs intégrés

🔧 FONCTIONNALITÉS AVANCÉES:
• Génération PDF sécurisé
• Signature électronique intégrée
• QR codes traçabilité
• Watermark anti-copie
• Versioning automatique

📊 DONNÉES DYNAMIQUES:
• Import données client (CRM)
• Calculs techniques automatiques
• Prix catalogue actualisé
• Conditions commerciales variables

💾 FORMATS EXPORT:
• PDF (impression/envoi)
• Word (édition)
• HTML (web)
• JSON (intégration)

═══════════════════════════════════════════════════════
                    TEMPLATES DISPONIBLES
═══════════════════════════════════════════════════════

📋 COMMERCIAUX:
• Devis standard/détaillé
• Proposition commerciale
• Bon de commande
• Facture proforma

📋 TECHNIQUES:
• Rapport étude
• Fiche technique
• Plan installation
• Schéma électrique

📋 CONTRACTUELS:
• Contrat type
• Avenant
• PV réception
• Attestation conformité

📋 ADMINISTRATIFS:
• Demande raccordement
• Déclaration préalable
• Dossier subvention
• Rapport formation

🎯 CONFIGURATION SUR MESURE:
Chaque template peut être adapté selon:
• Secteur activité (résidentiel/tertiaire/industrie)
• Type client (particulier/professionnel)
• Gamme produit (standard/premium)
• Région (spécificités locales)

        """
        
        return customization
    
    async def process(self, state) -> Dict[str, Any]:
        """Méthode requise par BaseAgent - traite une requête de génération de document"""
        try:
            # Utiliser la langue détectée par le workflow ou détecter si pas disponible
            detected_language = getattr(state, 'detected_language', None)
            if not detected_language:
                detected_language = "fr"  # Défaut français
            
            # Analyse du type de demande de document
            message_lower = state.current_message.lower()
            
            if any(word in message_lower for word in ["devis", "prix", "estimation", "tarif"]):
                result = self._generate_quote_document("devis standard")
            elif any(word in message_lower for word in ["rapport", "étude", "technique", "analyse"]):
                result = self._create_technical_report("étude complète")
            elif any(word in message_lower for word in ["contrat", "engagement", "signature"]):
                result = self._generate_contract("contrat standard")
            elif any(word in message_lower for word in ["attestation", "certificat", "conformité"]):
                result = self._create_certificate("attestation installation")
            elif any(word in message_lower for word in ["fiche", "technique", "spécifications"]):
                result = self._generate_technical_sheet("fiche équipement")
            elif any(word in message_lower for word in ["personnaliser", "adapter", "modifier"]):
                result = self._customize_template("template personnalisé")
            else:
                # Génération de devis par défaut
                result = self._generate_quote_document("devis standard")
            
            # Génération de la réponse dans la langue détectée
            response = self._generate_document_response(result, detected_language)
            
            return {
                "response": response,
                "agent_used": "document_generator",
                "confidence": 0.9,
                "detected_language": detected_language,
                "sources": ["Solar Nasih Document Database"]
            }
            
        except Exception as e:
            logger.error(f"Erreur dans le générateur de documents: {e}")
            return {
                "response": f"Erreur lors de la génération de document: {str(e)}",
                "agent_used": "document_generator",
                "confidence": 0.3,
                "error": str(e),
                "sources": ["Solar Nasih Document Database"]
            }
    
    def _generate_document_response(self, result: str, language: str) -> str:
        """Génère une réponse de document dans la langue appropriée"""
        # Pour l'instant, retourner le résultat tel quel
        # En production, on pourrait ajouter des traductions
        return result
    
    def can_handle(self, user_input: str, context: Dict[str, Any] = None) -> float:
        doc_keywords = [
            "document", "rapport", "devis", "contrat", "attestation",
            "certificat", "fiche", "générer", "créer", "éditer", "pdf",
            "template", "modèle", "personnaliser", "imprimer"
        ]
        matches = sum(1 for kw in doc_keywords if kw in user_input.lower())
        return min(matches * 0.2, 1.0)
