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
        """Génère un document de devis détaillé personnalisé"""
        # Extraire les paramètres du message original si disponible
        import re
        
        # Valeurs par défaut
        puissance = "6 kWc"
        nb_panneaux = "18"
        puissance_panneau = "333Wc"  # 6000W / 18 panneaux
        
        # Essayer d'extraire les informations du quote_data ou du contexte
        quote_lower = quote_data.lower()
        
        # Extraire la puissance
        import re
        puissance_match = re.search(r'(\d+(?:\.\d+)?)\s*kw?c?', quote_lower)
        if puissance_match:
            puissance_num = float(puissance_match.group(1))
            puissance = f"{puissance_num} kWc"
        
        # Extraire le nombre de panneaux
        panneaux_match = re.search(r'(\d+)\s*panneaux?', quote_lower)
        if panneaux_match:
            nb_panneaux_num = int(panneaux_match.group(1))
            nb_panneaux = str(nb_panneaux_num)
            puissance_panneau_num = puissance_num * 1000 / nb_panneaux_num
            puissance_panneau = f"{puissance_panneau_num:.0f}Wc"
        
        # Calculs basés sur les paramètres
        puissance_num = 6.0  # kWc
        nb_panneaux_num = 18
        puissance_panneau_num = puissance_num * 1000 / nb_panneaux_num  # Wc
        
        # Calculs financiers
        prix_panneaux = nb_panneaux_num * puissance_panneau_num * 0.8  # ~0.8€/Wc
        prix_onduleur = puissance_num * 200  # ~200€/kWc
        prix_structure = puissance_num * 125  # ~125€/kWc
        prix_cablage = puissance_num * 67  # ~67€/kWc
        prix_installation = puissance_num * 400  # ~400€/kWc
        
        total_ht = prix_panneaux + prix_onduleur + prix_structure + prix_cablage + prix_installation
        tva = total_ht * 0.20
        total_ttc = total_ht + tva
        prime_autoconsommation = puissance_num * 230  # ~230€/kWc pour 6kWc
        prix_net = total_ttc - prime_autoconsommation
        
        # Production estimée
        production_annuelle = puissance_num * 1200  # ~1200 kWh/kWc/an
        economie_annuelle = production_annuelle * 0.15  # ~0.15€/kWh
        retour_investissement = prix_net / economie_annuelle
        
        quote_document = f"""
📄 DEVIS PHOTOVOLTAÏQUE DÉTAILLÉ

═══════════════════════════════════════════════════════
                    ENTREPRISE SOLAR PRO
              123 Avenue du Soleil, 69000 Lyon
                 Tél: 04.XX.XX.XX.XX
               Email: contact@solarpro.fr
                   RGE Qualibat 5911
═══════════════════════════════════════════════════════

📅 DEVIS N°: DEV-2024-001                 Date: 15/01/2024
👤 CLIENT: [À personnaliser]
🏠 ADRESSE: [À personnaliser]

═══════════════════════════════════════════════════════
                      OBJET DU DEVIS
═══════════════════════════════════════════════════════

Installation photovoltaïque {puissance} avec {nb_panneaux} panneaux
Autoconsommation avec revente du surplus

═══════════════════════════════════════════════════════
                    DÉTAIL DE L'OFFRE
═══════════════════════════════════════════════════════

📦 MATÉRIEL FOURNI:
• {nb_panneaux} panneaux photovoltaïques {puissance_panneau}        {prix_panneaux:,.0f}.00€
  (Monocristallins, garantie 25 ans)
• 1 onduleur string {puissance} avec monitoring        {prix_onduleur:,.0f}.00€
  (Garantie fabricant 10 ans)
• Structure de fixation aluminium               {prix_structure:,.0f}.00€
• Câblage DC et protections                     {prix_cablage:,.0f}.00€
• Coffret de protection AC                      {prix_cablage/2:,.0f}.00€
• Compteur de production                        {prix_cablage/4:,.0f}.00€
                                    Sous-total: {prix_panneaux + prix_onduleur + prix_structure + prix_cablage + prix_cablage/2 + prix_cablage/4:,.0f}.00€

🔧 INSTALLATION ET SERVICES:
• Main d'œuvre pose et raccordement          {prix_installation:,.0f}.00€
• Démarches administratives complètes          {prix_installation/5:,.0f}.00€
• Mise en service et formation                  {prix_installation/10:,.0f}.00€
• Garantie main d'œuvre 10 ans                   0.00€
                                    Sous-total: {prix_installation + prix_installation/5 + prix_installation/10:,.0f}.00€

═══════════════════════════════════════════════════════
                      RÉCAPITULATIF
═══════════════════════════════════════════════════════

💰 Total HT:                                {total_ht:,.0f}.00€
🧾 TVA 20%:                                 {tva:,.0f}.00€
💸 Total TTC:                              {total_ttc:,.0f}.00€

🎁 AIDES DÉDUITES:
• Prime autoconsommation {puissance}               -{prime_autoconsommation:,.0f}.00€
💳 PRIX NET À PAYER:                        {prix_net:,.0f}.00€

═══════════════════════════════════════════════════════
              PERFORMANCE ET RENTABILITÉ
═══════════════════════════════════════════════════════

📈 Production annuelle estimée: {production_annuelle:,.0f} kWh
💡 Taux d'autoconsommation: 70%
💰 Économies annuelles: {economie_annuelle:,.0f}€
⏱️ Retour sur investissement: {retour_investissement:.1f} ans
🌍 CO2 évité: {production_annuelle * 0.0003:.1f} tonnes/an

═══════════════════════════════════════════════════════
                    CONDITIONS
═══════════════════════════════════════════════════════

• Devis valable 30 jours à compter de ce jour
• Acompte de 30% à la signature
• Solde à la réception des travaux
• Délai d'exécution: 4-6 semaines
• Garantie décennale incluse

═══════════════════════════════════════════════════════
                    CARACTÉRISTIQUES TECHNIQUES
═══════════════════════════════════════════════════════

⚡ PUISSANCE INSTALLÉE: {puissance}
📦 NOMBRE DE PANNEAUX: {nb_panneaux}
🔌 TYPE ONDULEUR: String {puissance}
🏠 TYPE INSTALLATION: Surimposition toiture
📊 MONITORING: Application mobile incluse
🔋 STOCKAGE: Non inclus (optionnel)

═══════════════════════════════════════════════════════
                    GARANTIES
═══════════════════════════════════════════════════════

🛡️ GARANTIES INCLUSES:
• Panneaux: 25 ans produit + 25 ans performance
• Onduleur: 10 ans fabricant
• Installation: 10 ans main d'œuvre
• Décennale: Dommages solidité/étanchéité

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
    
    def _generate_maintenance_guide(self, guide_data: str) -> str:
        """Génère un guide de maintenance préventive"""
        maintenance_guide = """
🔧 GUIDE DE MAINTENANCE PRÉVENTIVE
    Installation Solaire Résidentielle

═══════════════════════════════════════════════════════
                    INTRODUCTION
═══════════════════════════════════════════════════════

Ce guide détaille les opérations de maintenance préventive
nécessaires pour garantir le bon fonctionnement et la
longévité de votre installation photovoltaïque.

⚠️ IMPORTANT: La maintenance préventive est essentielle
pour maintenir les performances et la garantie.

═══════════════════════════════════════════════════════
                    MAINTENANCE QUOTIDIENNE
═══════════════════════════════════════════════════════

📊 SURVEILLANCE PRODUCTION:
• Vérifier la production quotidienne sur l'écran/mobile
• Noter les anomalies (production nulle, erreurs)
• Contrôler les indicateurs de fonctionnement

🌤️ CONDITIONS MÉTÉO:
• Surveiller l'impact des conditions météo
• Noter les baisses de production normales (nuages, pluie)
• Identifier les ombrages saisonniers

═══════════════════════════════════════════════════════
                   MAINTENANCE HEBDOMADAIRE
═══════════════════════════════════════════════════════

📈 ANALYSE PERFORMANCES:
• Comparer production avec prévisions
• Calculer le rendement moyen de la semaine
• Identifier les tendances de performance

🔍 INSPECTION VISUELLE (depuis le sol):
• Vérifier l'état général des panneaux
• Contrôler l'absence de débris ou feuilles
• Observer les fixations et câblage

═══════════════════════════════════════════════════════
                  MAINTENANCE MENSUELLE
═══════════════════════════════════════════════════════

🧹 NETTOYAGE LÉGER:
• Nettoyer les panneaux avec eau claire (si accessible)
• Retirer les feuilles et débris légers
• Vérifier l'état des joints d'étanchéité

⚡ CONTRÔLE ÉLECTRIQUE:
• Vérifier les voyants de l'onduleur
• Contrôler l'absence de bruits anormaux
• Tester les boutons de l'interface

📱 MISE À JOUR LOGICIEL:
• Vérifier les mises à jour du monitoring
• Sauvegarder les données de production
• Contrôler la connexion internet

═══════════════════════════════════════════════════════
                  MAINTENANCE TRIMESTRIELLE
═══════════════════════════════════════════════════════

🔧 INSPECTION TECHNIQUE:
• Contrôler le serrage des connexions
• Vérifier l'état des câbles et protections
• Inspecter les boîtes de jonction

🌡️ MESURES DE PERFORMANCE:
• Mesurer la température des panneaux
• Contrôler la tension et courant
• Vérifier le rendement de l'onduleur

📊 RAPPORT DE MAINTENANCE:
• Documenter toutes les observations
• Noter les anomalies détectées
• Planifier les interventions nécessaires

═══════════════════════════════════════════════════════
                   MAINTENANCE SEMESTRIELLE
═══════════════════════════════════════════════════════

🧽 NETTOYAGE APPROFONDI:
• Nettoyage professionnel des panneaux
• Vérification de l'état de surface
• Contrôle de l'absence de microfissures

🔍 INSPECTION DÉTAILLÉE:
• Contrôle complet de la structure
• Vérification des fixations mécaniques
• Inspection des joints d'étanchéité

⚡ TESTS ÉLECTRIQUES:
• Mesure de l'isolement
• Contrôle des protections
• Test de fonctionnement complet

═══════════════════════════════════════════════════════
                   MAINTENANCE ANNUELLE
═══════════════════════════════════════════════════════

🏢 INTERVENTION PROFESSIONNELLE:
• Inspection complète par technicien qualifié
• Nettoyage professionnel complet
• Vérification de la conformité

📋 RAPPORT ANNUEL:
• Analyse complète des performances
• Comparaison avec les prévisions
• Recommandations d'optimisation

🔧 MAINTENANCE PRÉVENTIVE:
• Remplacement des pièces d'usure
• Mise à jour du système de monitoring
• Optimisation des paramètres

═══════════════════════════════════════════════════════
                    POINTS D'ATTENTION
═══════════════════════════════════════════════════════

⚠️ SÉCURITÉ:
• Ne jamais monter sur le toit sans équipement
• Éviter les interventions par temps humide
• Respecter les consignes de sécurité

🔌 ÉLECTRIQUE:
• L'installation reste sous tension en journée
• Ne pas toucher aux connexions électriques
• Contacter un professionnel en cas de problème

🌦️ MÉTÉO:
• Éviter les interventions par mauvais temps
• Tenir compte des conditions de vent
• Respecter les consignes de sécurité

═══════════════════════════════════════════════════════
                    CONTACTS ET SUPPORT
═══════════════════════════════════════════════════════

📞 SERVICE APRÈS-VENTE:
• Téléphone: 04.XX.XX.XX.XX
• Email: sav@solarpro.fr
• Intervention sous 48h

🏢 ENTREPRISE:
• SOLAR PRO SARL
• RGE Qualibat 5911
• Assurance décennale

📱 MONITORING:
• Application mobile: Solar Pro
• Interface web: www.solarpro.fr/monitoring
• Support technique 7j/7

═══════════════════════════════════════════════════════
Ce guide doit être conservé avec votre documentation
d'installation et consulté régulièrement.
═══════════════════════════════════════════════════════

        """
        
        return maintenance_guide
    
    def _generate_training_document(self, training_data: str) -> str:
        """Génère un document de formation"""
        training_doc = """
📚 PLAN DE FORMATION - ÉNERGIE SOLAIRE
    Formation Générale - 60 minutes

═══════════════════════════════════════════════════════
                    INFORMATIONS GÉNÉRALES
═══════════════════════════════════════════════════════

📅 DURÉE: 60 minutes
👥 PUBLIC: Général (particuliers, professionnels)
🎯 NIVEAU: Débutant à intermédiaire
📋 FORMAT: Présentation interactive + Q&A

═══════════════════════════════════════════════════════
                    OBJECTIFS PÉDAGOGIQUES
═══════════════════════════════════════════════════════

🎯 OBJECTIFS GÉNÉRAUX:
• Comprendre les principes de l'énergie solaire
• Connaître les technologies photovoltaïques
• Maîtriser les aspects économiques et réglementaires
• Appliquer les concepts à des projets concrets

📊 OBJECTIFS SPÉCIFIQUES:
• Expliquer le fonctionnement d'un panneau solaire
• Calculer la production d'une installation
• Évaluer la rentabilité d'un projet
• Identifier les démarches administratives

═══════════════════════════════════════════════════════
                    PROGRAMME DÉTAILLÉ
═══════════════════════════════════════════════════════

⏰ SÉQUENCE 1: INTRODUCTION (10 min)
• Présentation du formateur et des participants
• Définition de l'énergie solaire photovoltaïque
• Contexte énergétique et enjeux environnementaux
• Questions et échanges

⏰ SÉQUENCE 2: TECHNOLOGIES (15 min)
• Principe de fonctionnement des panneaux
• Types de cellules (mono/polycristallin, PERC)
• Composants d'une installation (onduleur, câblage)
• Évolutions technologiques récentes
• Démonstration interactive

⏰ SÉQUENCE 3: DIMENSIONNEMENT (15 min)
• Facteurs influençant la production
• Calcul de la puissance nécessaire
• Optimisation de l'orientation et inclinaison
• Outils de simulation disponibles
• Exercice pratique

⏰ SÉQUENCE 4: ASPECTS ÉCONOMIQUES (10 min)
• Coûts d'investissement et d'exploitation
• Aides et subventions disponibles
• Calcul de rentabilité et ROI
• Comparaison avec autres énergies
• Exemples concrets

⏰ SÉQUENCE 5: RÉGLEMENTATION (5 min)
• Cadre réglementaire français
• Démarches administratives
• Normes et certifications
• Garanties et assurances

⏰ SÉQUENCE 6: CONCLUSION (5 min)
• Synthèse des points clés
• Questions-réponses
• Ressources et contacts
• Évaluation de la formation

═══════════════════════════════════════════════════════
                    MÉTHODES PÉDAGOGIQUES
═══════════════════════════════════════════════════════

🎯 APPROCHE:
• Pédagogie active et participative
• Alternance théorie/pratique
• Exemples concrets et cas réels
• Support visuel et interactif

📊 OUTILS UTILISÉS:
• Présentation PowerPoint
• Simulateur en ligne
• Échantillons de matériel
• Documentation technique
• Quiz interactif

👥 INTERACTIONS:
• Questions-réponses continues
• Travaux pratiques en groupe
• Partage d'expériences
• Débats et échanges

═══════════════════════════════════════════════════════
                    SUPPORTS DE FORMATION
═══════════════════════════════════════════════════════

📋 DOCUMENTS FOURNIS:
• Support de cours complet
• Fiches techniques produits
• Guide des démarches administratives
• Liste des contacts utiles
• Ressources en ligne

🔗 RESSOURCES COMPLÉMENTAIRES:
• Sites web de référence
• Applications de simulation
• Documentation technique
• Vidéos explicatives
• Forums et communautés

═══════════════════════════════════════════════════════
                    ÉVALUATION ET SUIVI
═══════════════════════════════════════════════════════

📊 ÉVALUATION:
• Quiz de connaissances (10 questions)
• Évaluation de la satisfaction
• Suggestions d'amélioration
• Attestation de participation

📈 SUIVI POST-FORMATION:
• Support technique 30 jours
• Ressources en ligne accessibles
• Newsletter technique
• Sessions de perfectionnement

═══════════════════════════════════════════════════════
                    INFORMATIONS PRATIQUES
═══════════════════════════════════════════════════════

🏢 LIEU: Salle de formation Solar Pro
📍 ADRESSE: 123 Avenue du Soleil, 69000 Lyon
🚗 PARKING: Gratuit sur place
☕ PAUSE: Café et rafraîchissements inclus

📞 CONTACT: 04.XX.XX.XX.XX
📧 EMAIL: formation@solarpro.fr
🌐 WEB: www.solarpro.fr/formation

═══════════════════════════════════════════════════════
Cette formation s'inscrit dans notre démarche
d'accompagnement et de professionnalisation.
═══════════════════════════════════════════════════════

        """
        
        return training_doc
    
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
                # Extraire les paramètres du message original
                original_message = state.current_message
                result = self._generate_quote_document(original_message)
            elif any(word in message_lower for word in ["rapport", "étude", "technique", "analyse"]):
                result = self._create_technical_report("étude complète")
            elif any(word in message_lower for word in ["contrat", "engagement", "signature"]):
                result = self._generate_contract("contrat standard")
            elif any(word in message_lower for word in ["attestation", "certificat", "conformité"]):
                result = self._create_certificate("attestation installation")
            elif any(word in message_lower for word in ["fiche", "technique", "spécifications"]):
                result = self._generate_technical_sheet("fiche équipement")
            elif any(word in message_lower for word in ["maintenance", "entretien", "guide maintenance", "maintenance préventive"]):
                result = self._generate_maintenance_guide("guide maintenance préventive")
            elif any(word in message_lower for word in ["formation", "cours", "plan de cours"]) and "maintenance" not in message_lower:
                result = self._generate_training_document("formation générale")
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
