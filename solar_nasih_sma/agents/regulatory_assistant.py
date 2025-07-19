from typing import Dict, Any, List
from langchain.tools import BaseTool, tool
from agents.base_agent import BaseAgent
from models.schemas import AgentType, Language
from services.gemini_service import GeminiService
from services.tavily_service import TavilyService
import logging

logger = logging.getLogger(__name__)

class RegulatoryAssistantAgent(BaseAgent):
    """Agent Assistant Réglementaire - Informations réglementaires, aides et exonérations fiscales"""
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.REGULATORY_ASSISTANT,
            description="Fournit des informations réglementaires à jour sur les aides, douanes, et exonérations fiscales"
        )
        self.gemini_service = GeminiService()
        self.tavily_service = TavilyService()
    
    def _init_tools(self) -> List[BaseTool]:
        return [
            self.get_solar_incentives_tool,
            self.get_tax_benefits_tool,
            self.get_regulations_tool,
            self.get_customs_info_tool,
            self.calculate_ma_prime_renov_tool,
            self.get_autoconsumption_bonus_tool,
            self.check_eligibility_tool
        ]
    
    def _get_system_prompt(self) -> str:
        """Prompt système de l'assistant réglementaire"""
        return """
        Vous êtes l'Agent Assistant Réglementaire pour Solar Nasih, expert en réglementation française de l'énergie solaire.
        
        Vos responsabilités incluent:
        1. Fournir des informations actualisées sur les aides publiques
        2. Expliquer les exonérations fiscales et crédits d'impôt
        3. Détailler les procédures administratives
        4. Informer sur les réglementations de raccordement
        5. Calculer les montants d'aides éligibles
        6. Donner les informations douanières pour l'importation
        
        Sources prioritaires: Service-public.fr, ADEME, ANAH, Légifrance, DGCCRF
        Toujours préciser la date de validité des informations et recommander de vérifier sur les sites officiels.
        """
    
    @tool
    def get_solar_incentives_tool(self, location: str = "France", installation_type: str = "residential") -> Dict[str, Any]:
        """Récupère les aides disponibles pour l'installation solaire"""
        try:
            # Recherche avec Tavily pour informations actualisées
            search_results = self.tavily_service.search_solar_incentives(location)
            
            # Aides nationales 2024 (données de référence)
            national_incentives = {
                "prime_autoconsommation": {
                    "description": "Prime à l'autoconsommation photovoltaïque",
                    "montant_par_kwc": {
                        "<=3kWc": 300,
                        "<=9kWc": 230, 
                        "<=36kWc": 200,
                        "<=100kWc": 100
                    },
                    "conditions": [
                        "Installation en autoconsommation avec vente du surplus",
                        "Installateur RGE obligatoire",
                        "Puissance ≤ 100 kWc"
                    ],
                    "versement": "Sur 5 ans",
                    "valide_jusqu": "2024-12-31"
                },
                "tva_reduite": {
                    "description": "TVA réduite à 10%",
                    "taux": "10% au lieu de 20%",
                    "conditions": [
                        "Installation ≤ 3 kWc",
                        "Logement de plus de 2 ans",
                        "Installation par professionnel"
                    ],
                    "economies": "Environ 10% du coût total"
                },
                "ma_prime_renov": {
                    "description": "MaPrimeRénov' pour panneaux solaires thermiques uniquement",
                    "note": "Photovoltaïque non éligible depuis 2024",
                    "alternative": "Prime autoconsommation disponible"
                }
            }
            
            # Aides régionales communes
            regional_incentives = {
                "ile_de_france": {
                    "aide_region": "Jusqu'à 1500€ selon revenus",
                    "conditions": "Résidence principale, RGE"
                },
                "occitanie": {
                    "aide_region": "300€/kWc max 2000€",
                    "conditions": "Autoconsommation, installateur local"
                },
                "nouvelle_aquitaine": {
                    "aide_region": "200€/kWc max 1500€", 
                    "conditions": "Résidence principale"
                }
            }
            
            return {
                "location": location,
                "installation_type": installation_type,
                "national_incentives": national_incentives,
                "regional_incentives": regional_incentives.get(location.lower().replace(" ", "_"), {}),
                "search_results": search_results[:3],  # Top 3 résultats Tavily
                "last_update": "2024-01-01",
                "disclaimer": "Informations indicatives. Vérifiez sur les sites officiels."
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération aides: {e}")
            return {"error": str(e)}
    
    @tool
    def get_tax_benefits_tool(self, income_level: str = "moyen") -> Dict[str, Any]:
        """Informations sur les avantages fiscaux"""
        try:
            tax_benefits = {
                "credit_impot": {
                    "status": "Supprimé depuis 2021",
                    "remplacement": "Prime à l'autoconsommation",
                    "note": "Le CITE ne s'applique plus au photovoltaïque"
                },
                "exoneration_taxe_fonciere": {
                    "description": "Exonération possible de taxe foncière",
                    "duree": "Jusqu'à 3 ans selon communes",
                    "conditions": [
                        "Décision communale",
                        "Installation ≥ 3 kWc généralement",
                        "Résidence principale"
                    ],
                    "demarche": "Demande en mairie"
                },
                "revenus_vente": {
                    "seuil_exoneration": "70 000 kWh/an",
                    "regime_micro_ba": {
                        "description": "Régime micro-BA si > 70 000 kWh/an",
                        "abattement": "87% sur les revenus",
                        "conditions": "Exploitation agricole"
                    },
                    "particuliers": {
                        "seuil": "< 70 000 kWh/an généralement exonéré",
                        "declaration": "À déclarer si revenus significatifs"
                    }
                },
                "tva_sur_vente": {
                    "seuil": "Franchise TVA si CA < 85 800€",
                    "note": "Rarement atteint pour particuliers"
                }
            }
            
            return {
                "income_level": income_level,
                "tax_benefits": tax_benefits,
                "recommendation": self._get_tax_recommendation(income_level),
                "sources": [
                    "Code général des impôts",
                    "BOFIP (Bulletin officiel des finances publiques)",
                    "Service-public.fr"
                ]
            }
            
        except Exception as e:
            logger.error(f"Erreur avantages fiscaux: {e}")
            return {"error": str(e)}
    
    @tool
    def get_regulations_tool(self, regulation_type: str = "raccordement") -> Dict[str, Any]:
        """Informations sur les réglementations spécifiques"""
        try:
            regulations = {
                "raccordement": {
                    "procedure": "CONSUEL + convention autoconsommation",
                    "delais": "2-6 mois selon gestionnaire réseau",
                    "couts": {
                        "consuel": "~160€",
                        "raccordement": "161€ (≤36kVA)",
                        "mise_en_service": "~50€"
                    },
                    "documents": [
                        "Attestation CONSUEL",
                        "Convention d'autoconsommation",
                        "Certificat de conformité",
                        "Assurance RC"
                    ]
                },
                "urbanisme": {
                    "declaration_prealable": "Obligatoire sauf exceptions",
                    "exceptions": [
                        "Au sol < 1.8m et < 20m²",
                        "Toiture plate invisible rue"
                    ],
                    "delai_instruction": "1 mois",
                    "pieces": [
                        "Plan de situation",
                        "Plan de masse", 
                        "Photos",
                        "Notice descriptive"
                    ]
                },
                "securite": {
                    "normes": ["NF C 15-100", "NF EN 61215", "NF EN 61730"],
                    "obligations": [
                        "Installateur RGE",
                        "Matériel certifié",
                        "Mise à la terre",
                        "Protection contre la foudre"
                    ]
                },
                "assurance": {
                    "obligatoire": [
                        "RC installateur",
                        "Assurance dommages-ouvrage",
                        "Garantie décennale"
                    ],
                    "recommandee": [
                        "Assurance tous risques installation",
                        "Assurance perte d'exploitation"
                    ]
                }
            }
            
            return {
                "regulation_type": regulation_type,
                "details": regulations.get(regulation_type, {}),
                "all_regulations": list(regulations.keys()),
                "contacts": {
                    "consuel": "08 21 20 32 62",
                    "enedis": "09 70 83 19 70",
                    "service_public": "3939"
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur réglementations: {e}")
            return {"error": str(e)}
    
    @tool
    def get_customs_info_tool(self, product_type: str = "panneaux") -> Dict[str, Any]:
        """Informations douanières pour importation d'équipements solaires"""
        try:
            customs_info = {
                "panneaux": {
                    "code_douane": "8541 40 90",
                    "taux_droit": "0% (origine UE/pays accords)",
                    "tva_import": "20%",
                    "documents": [
                        "Facture commerciale",
                        "Document de transport",
                        "Certificat d'origine",
                        "Déclaration conformité CE"
                    ]
                },
                "onduleurs": {
                    "code_douane": "8504 40 82", 
                    "taux_droit": "0-2.7% selon origine",
                    "tva_import": "20%",
                    "normes": ["EN 50178", "EN 61000"]
                },
                "batteries": {
                    "code_douane": "8507 60 00",
                    "taux_droit": "0-6% selon type",
                    "tva_import": "20%",
                    "restrictions": "Transport matières dangereuses",
                    "certifications": ["UN38.3", "IEC 62619"]
                },
                "supports": {
                    "code_douane": "7308 90 99",
                    "taux_droit": "0-6.4% selon matériau",
                    "tva_import": "20%"
                }
            }
            
            general_procedures = {
                "seuils": {
                    "declaration_simple": "< 1 000€",
                    "declaration_detaillee": "> 1 000€",
                    "dedouanement_pro": "Usage professionnel"
                },
                "delais": {
                    "dedouanement": "24-48h",
                    "controle_physique": "+2-5 jours si sélectionné"
                },
                "conseils": [
                    "Vérifier accords commerciaux",
                    "Prévoir certificats conformité",
                    "Budgeter frais transitaire",
                    "Anticiper contrôles qualité"
                ]
            }
            
            return {
                "product_type": product_type,
                "customs_details": customs_info.get(product_type, {}),
                "general_procedures": general_procedures,
                "all_products": list(customs_info.keys())
            }
            
        except Exception as e:
            logger.error(f"Erreur informations douanières: {e}")
            return {"error": str(e)}
    
    @tool
    def calculate_ma_prime_renov_tool(self, household_income: int, household_size: int, region: str = "ile_de_france") -> Dict[str, Any]:
        """Calcule l'éligibilité MaPrimeRénov' (pour solaire thermique uniquement)"""
        try:
            # Plafonds de revenus 2024 (Île-de-France)
            income_thresholds_idf = {
                1: {"blue": 23541, "yellow": 28657, "purple": 40018, "pink": 40019},
                2: {"blue": 34551, "yellow": 42058, "purple": 58827, "pink": 58828},
                3: {"blue": 41493, "yellow": 50513, "purple": 70382, "pink": 70383},
                4: {"blue": 48447, "yellow": 58981, "purple": 82839, "pink": 82840},
                5: {"blue": 55427, "yellow": 67473, "purple": 94844, "pink": 94845}
            }
            
            # Plafonds autres régions (20% moins élevés)
            income_thresholds_other = {
                1: {"blue": 17009, "yellow": 21805, "purple": 30549, "pink": 30550},
                2: {"blue": 24875, "yellow": 31889, "purple": 44907, "pink": 44908},
                3: {"blue": 29917, "yellow": 38349, "purple": 54071, "pink": 54072},
                4: {"blue": 34948, "yellow": 44802, "purple": 63235, "pink": 63236},
                5: {"blue": 40002, "yellow": 51281, "purple": 72400, "pink": 72401}
            }
            
            # Sélection des seuils selon la région
            thresholds = income_thresholds_idf if region.lower() in ["ile_de_france", "idf", "paris"] else income_thresholds_other
            
            # Détermination de la catégorie
            household_thresholds = thresholds.get(min(household_size, 5), thresholds[5])
            
            category = "pink"  # Par défaut (non éligible)
            if household_income <= household_thresholds["blue"]:
                category = "blue"
            elif household_income <= household_thresholds["yellow"]:
                category = "yellow"
            elif household_income <= household_thresholds["purple"]:
                category = "purple"
            
            # Montants pour solaire thermique (photovoltaïque non éligible)
            prime_amounts = {
                "blue": {
                    "chauffe_eau_solaire": 4000,
                    "systeme_solaire_combine": 10000,
                    "note": "Montants maximum pour ménages très modestes"
                },
                "yellow": {
                    "chauffe_eau_solaire": 3000,
                    "systeme_solaire_combine": 8000,
                    "note": "Montants pour ménages modestes"
                },
                "purple": {
                    "chauffe_eau_solaire": 2000,
                    "systeme_solaire_combine": 4000,
                    "note": "Montants pour ménages intermédiaires"
                },
                "pink": {
                    "chauffe_eau_solaire": 0,
                    "systeme_solaire_combine": 0,
                    "note": "Non éligible - revenus trop élevés"
                }
            }
            
            return {
                "household_income": household_income,
                "household_size": household_size,
                "region": region,
                "category": category,
                "eligible": category != "pink",
                "prime_amounts": prime_amounts[category],
                "important_note": "⚠️ MaPrimeRénov' ne concerne PAS le photovoltaïque, uniquement le solaire thermique",
                "alternative": "Pour le photovoltaïque, voir la prime à l'autoconsommation",
                "thresholds_used": household_thresholds
            }
            
        except Exception as e:
            logger.error(f"Erreur calcul MaPrimeRénov': {e}")
            return {"error": str(e)}
    
    @tool
    def get_autoconsumption_bonus_tool(self, power_kwc: float) -> Dict[str, Any]:
        """Calcule la prime à l'autoconsommation"""
        try:
            # Tarifs 2024 T4 (octobre-décembre)
            bonus_rates = [
                {"min_power": 0, "max_power": 3, "rate": 300},
                {"min_power": 3, "max_power": 9, "rate": 230},
                {"min_power": 9, "max_power": 36, "rate": 200},
                {"min_power": 36, "max_power": 100, "rate": 100}
            ]
            
            # Détermination du taux applicable
            applicable_rate = 0
            for rate_bracket in bonus_rates:
                if rate_bracket["min_power"] <= power_kwc <= rate_bracket["max_power"]:
                    applicable_rate = rate_bracket["rate"]
                    break
            
            if applicable_rate == 0:
                return {
                    "power_kwc": power_kwc,
                    "eligible": False,
                    "reason": "Puissance > 100 kWc non éligible",
                    "max_eligible_power": 100
                }
            
            # Calcul de la prime totale
            total_bonus = power_kwc * applicable_rate
            annual_payment = total_bonus / 5  # Versée sur 5 ans
            
            # Tarif de rachat du surplus
            surplus_rates = {
                "<=9kwc": 0.1301,  # €/kWh T4 2024
                "<=100kwc": 0.0781
            }
            
            surplus_rate = surplus_rates["<=9kwc"] if power_kwc <= 9 else surplus_rates["<=100kwc"]
            
            return {
                "power_kwc": power_kwc,
                "eligible": True,
                "rate_per_kwc": applicable_rate,
                "total_bonus": round(total_bonus, 2),
                "annual_payment": round(annual_payment, 2),
                "payment_duration": "5 ans",
                "surplus_buyback_rate": surplus_rate,
                "conditions": [
                    "Installation en autoconsommation avec vente du surplus",
                    "Installateur certifié RGE",
                    "Respect des normes en vigueur",
                    "Demande avant mise en service"
                ],
                "procedure": [
                    "1. Faire appel à un installateur RGE",
                    "2. Demander le raccordement à Enedis/ELD",
                    "3. Signer la convention d'autoconsommation",
                    "4. La prime est versée automatiquement"
                ],
                "tarif_period": "T4 2024 (octobre-décembre)",
                "next_update": "Janvier 2025"
            }
            
        except Exception as e:
            logger.error(f"Erreur calcul prime autoconsommation: {e}")
            return {"error": str(e)}
    
    @tool
    def check_eligibility_tool(self, installation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Vérifie l'éligibilité aux différentes aides"""
        try:
            power = installation_data.get("power_kwc", 0)
            building_age = installation_data.get("building_age_years", 0)
            installer_rge = installation_data.get("installer_rge", False)
            installation_type = installation_data.get("type", "roof")  # roof, ground, facade
            
            eligibility_check = {
                "prime_autoconsommation": {
                    "eligible": power <= 100 and installer_rge,
                    "conditions_met": {
                        "power_limit": power <= 100,
                        "installer_rge": installer_rge,
                        "autoconsumption": True  # Supposé par défaut
                    },
                    "missing_requirements": []
                },
                "tva_reduite": {
                    "eligible": power <= 3 and building_age >= 2,
                    "conditions_met": {
                        "power_limit": power <= 3,
                        "building_age": building_age >= 2
                    },
                    "missing_requirements": []
                },
                "exoneration_taxe_fonciere": {
                    "eligible": "Dépend de la commune",
                    "note": "Vérifier auprès de la mairie locale"
                }
            }
            
            # Ajout des exigences manquantes
            if not eligibility_check["prime_autoconsommation"]["eligible"]:
                missing = eligibility_check["prime_autoconsommation"]["missing_requirements"]
                if power > 100:
                    missing.append("Puissance > 100 kWc")
                if not installer_rge:
                    missing.append("Installateur RGE requis")
            
            if not eligibility_check["tva_reduite"]["eligible"]:
                missing = eligibility_check["tva_reduite"]["missing_requirements"]
                if power > 3:
                    missing.append("Puissance > 3 kWc")
                if building_age < 2:
                    missing.append("Bâtiment trop récent (< 2 ans)")
            
            # Calcul des montants éligibles
            eligible_amounts = {}
            if eligibility_check["prime_autoconsommation"]["eligible"]:
                bonus_result = self.get_autoconsumption_bonus_tool(power)
                eligible_amounts["prime_autoconsommation"] = bonus_result.get("total_bonus", 0)
            
            if eligibility_check["tva_reduite"]["eligible"]:
                estimated_cost = power * 2500  # Estimation 2500€/kWc
                eligible_amounts["tva_savings"] = estimated_cost * 0.1  # Économie de 10%
            
            return {
                "installation_data": installation_data,
                "eligibility_summary": eligibility_check,
                "eligible_amounts": eligible_amounts,
                "total_potential_aid": sum(eligible_amounts.values()),
                "recommendations": self._generate_eligibility_recommendations(eligibility_check, installation_data)
            }
            
        except Exception as e:
            logger.error(f"Erreur vérification éligibilité: {e}")
            return {"error": str(e)}
    
    def _get_tax_recommendation(self, income_level: str) -> str:
        """Génère une recommandation fiscale personnalisée"""
        recommendations = {
            "faible": "Concentrez-vous sur les aides directes (prime autoconsommation). Les avantages fiscaux auront peu d'impact.",
            "moyen": "Vérifiez l'exonération de taxe foncière dans votre commune. Déclarez les revenus de vente si significatifs.",
            "eleve": "Optimisez la fiscalité : vérifiez l'exonération taxe foncière, considérez le régime fiscal des revenus de vente."
        }
        return recommendations.get(income_level, "Consultez un conseiller fiscal pour optimiser votre situation.")
    
    def _generate_eligibility_recommendations(self, eligibility: Dict[str, Any], installation_data: Dict[str, Any]) -> List[str]:
        """Génère des recommandations basées sur l'éligibilité"""
        recommendations = []
        
        if not eligibility["prime_autoconsommation"]["eligible"]:
            if not installation_data.get("installer_rge", False):
                recommendations.append("🔧 Choisissez impérativement un installateur certifié RGE")
            if installation_data.get("power_kwc", 0) > 100:
                recommendations.append("⚡ Réduisez la puissance à ≤100 kWc pour être éligible à la prime")
        
        if not eligibility["tva_reduite"]["eligible"]:
            if installation_data.get("power_kwc", 0) > 3:
                recommendations.append("💰 Pour bénéficier de la TVA réduite, limitez à 3 kWc")
            if installation_data.get("building_age_years", 0) < 2:
                recommendations.append("🏠 TVA réduite non applicable (logement trop récent)")
        
        recommendations.extend([
            "📋 Vérifiez l'exonération de taxe foncière auprès de votre mairie",
            "📄 Conservez tous les justificatifs pour les démarches administratives",
            "🕐 Déposez les demandes avant le début des travaux"
        ])
        
        return recommendations
    
    async def process(self, user_input: str, context: Dict[str, Any], language: Language = Language.FRENCH) -> Any:
        """Traitement spécialisé pour les questions réglementaires"""
        try:
            # Analyser le type de demande réglementaire
            regulatory_type = self._classify_regulatory_request(user_input)
            
            # Traitement selon le type
            if regulatory_type == "aides":
                location = self._extract_location(user_input, context)
                result = self.get_solar_incentives_tool(location)
                
            elif regulatory_type == "fiscalite":
                income_level = self._extract_income_level(user_input, context)
                result = self.get_tax_benefits_tool(income_level)
                
            elif regulatory_type == "reglementation":
                reg_type = self._extract_regulation_type(user_input)
                result = self.get_regulations_tool(reg_type)
                
            elif regulatory_type == "douanes":
                product_type = self._extract_product_type(user_input)
                result = self.get_customs_info_tool(product_type)
                
            elif regulatory_type == "eligibilite":
                installation_data = self._extract_installation_data(user_input, context)
                result = self.check_eligibility_tool(installation_data)
                
            else:
                # Analyse générale
                result = {
                    "message": "Je peux vous aider avec les aspects réglementaires du solaire",
                    "topics": ["aides", "fiscalité", "réglementation", "douanes", "éligibilité"]
                }
            
            # Générer une réponse structurée
            response = await self._generate_regulatory_response(result, regulatory_type, language)
            return response
            
        except Exception as e:
            logger.error(f"Erreur traitement réglementaire: {e}")
            return f"Erreur lors du traitement réglementaire: {str(e)}"
    
    def _classify_regulatory_request(self, user_input: str) -> str:
        """Classifie le type de demande réglementaire"""
        text = user_input.lower()
        
        if any(word in text for word in ["aide", "subvention", "prime", "maprimerénov", "bonus"]):
            return "aides"
        elif any(word in text for word in ["impôt", "fiscal", "taxe", "crédit", "exonération"]):
            return "fiscalite"
        elif any(word in text for word in ["réglementation", "norme", "raccordement", "consuel", "urbanisme"]):
            return "reglementation"
        elif any(word in text for word in ["douane", "import", "export", "customs"]):
            return "douanes"
        elif any(word in text for word in ["éligible", "éligibilité", "conditions", "critères"]):
            return "eligibilite"
        else:
            return "general"
    
    def _extract_location(self, user_input: str, context: Dict[str, Any]) -> str:
        """Extrait la localisation de la demande"""
        # Recherche de régions françaises dans le texte
        regions = [
            "ile-de-france", "paris", "occitanie", "toulouse", "nouvelle-aquitaine", 
            "bordeaux", "lyon", "marseille", "nice", "lille", "strasbourg"
        ]
        
        text = user_input.lower()
        for region in regions:
            if region in text:
                return region
        
        return context.get("location", "France")
    
    def _extract_income_level(self, user_input: str, context: Dict[str, Any]) -> str:
        """Extrait le niveau de revenus"""
        text = user_input.lower()
        
        if any(word in text for word in ["modeste", "faible", "bas"]):
            return "faible"
        elif any(word in text for word in ["élevé", "haut", "aisé"]):
            return "eleve"
        else:
            return "moyen"
    
    def _extract_regulation_type(self, user_input: str) -> str:
        """Extrait le type de réglementation demandé"""
        text = user_input.lower()
        
        if any(word in text for word in ["raccordement", "consuel", "enedis"]):
            return "raccordement"
        elif any(word in text for word in ["urbanisme", "déclaration", "permis"]):
            return "urbanisme"
        elif any(word in text for word in ["sécurité", "norme", "protection"]):
            return "securite"
        elif any(word in text for word in ["assurance", "garantie", "responsabilité"]):
            return "assurance"
        else:
            return "raccordement"
    
    def _extract_product_type(self, user_input: str) -> str:
        """Extrait le type de produit pour les douanes"""
        text = user_input.lower()
        
        if any(word in text for word in ["panneau", "module", "photovoltaïque"]):
            return "panneaux"
        elif any(word in text for word in ["onduleur", "convertisseur"]):
            return "onduleurs"
        elif any(word in text for word in ["batterie", "stockage", "accumulateur"]):
            return "batteries"
        elif any(word in text for word in ["support", "fixation", "structure"]):
            return "supports"
        else:
            return "panneaux"
    
    def _extract_installation_data(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extrait les données d'installation pour vérification d'éligibilité"""
        # Extraction basique - à améliorer avec NLP
        import re
        
        # Recherche de puissance
        power_match = re.search(r'(\d+(?:\.\d+)?)\s*kw', user_input.lower())
        power = float(power_match.group(1)) if power_match else 6.0
        
        return {
            "power_kwc": power,
            "building_age_years": context.get("building_age", 10),
            "installer_rge": True,  # Supposé par défaut
            "type": "roof"
        }
    
    async def _generate_regulatory_response(self, result: Dict[str, Any], regulatory_type: str, language: Language) -> str:
        """Génère une réponse réglementaire structurée"""
        prompt = f"""
        Générez une réponse réglementaire claire et structurée basée sur:
        
        Type de demande: {regulatory_type}
        Données: {result}
        Langue: {language.value}
        
        La réponse doit:
        1. Être précise et factuelle
        2. Inclure les montants et conditions exactes
        3. Mentionner les sources officielles
        4. Donner des étapes concrètes
        5. Avertir de vérifier sur les sites officiels
        
        Format professionnel avec émojis pour la lisibilité.
        """
        
        return await self.gemini_service.generate_response(prompt)
    
    def can_handle(self, user_input: str, context: Dict[str, Any]) -> bool:
        """Détermine si l'agent peut traiter cette requête"""
        regulatory_keywords = [
            "aide", "subvention", "prime", "crédit", "impôt", "taxe", "fiscal",
            "réglementation", "norme", "loi", "décret", "obligation", "autorisation",
            "douane", "import", "export", "éligible", "conditions", "procédure",
            "maprimerénov", "consuel", "enedis", "urbanisme", "raccordement"
        ]
        
        return any(keyword in user_input.lower() for keyword in regulatory_keywords)

# Instance globale
regulatory_assistant_agent = RegulatoryAssistantAgent()