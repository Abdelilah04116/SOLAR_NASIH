from typing import Dict, Any, List
from langchain.tools import Tool
from agents.base_agent import BaseAgent
from models.schemas import AgentType
import json
import math

class EnergySimulatorAgent(BaseAgent):
    """
    Agent Simulateur Énergétique - Calculs et simulations énergétiques
    """
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.ENERGY_SIMULATOR,
            description="Simulateur énergétique pour installations photovoltaïques"
        )
        
        # Données météorologiques simplifiées par région
        self.irradiation_data = {
            "paris": 1100,
            "lyon": 1300,
            "marseille": 1600,
            "toulouse": 1350,
            "nice": 1550,
            "nantes": 1150,
            "montpellier": 1500,
            "bordeaux": 1250,
            "default": 1200
        }
        
        # Coefficients d'orientation et d'inclinaison
        self.orientation_coefficients = {
            "sud": 1.0,
            "sud-est": 0.95,
            "sud-ouest": 0.95,
            "est": 0.85,
            "ouest": 0.85,
            "nord": 0.6
        }
        
        self.inclination_coefficients = {
            30: 1.0,
            35: 0.99,
            40: 0.98,
            45: 0.96,
            0: 0.85,  # horizontal
            90: 0.7   # vertical
        }
    
    def _init_tools(self) -> List[Tool]:
        """Initialise les outils du simulateur énergétique"""
        return [
            Tool(
                name="calculate_production",
                description="Calcule la production énergétique",
                func=self._calculate_production
            ),
            Tool(
                name="estimate_savings",
                description="Estime les économies",
                func=self._estimate_savings
            ),
            Tool(
                name="calculate_payback",
                description="Calcule le temps de retour sur investissement",
                func=self._calculate_payback
            ),
            Tool(
                name="size_installation",
                description="Dimensionne l'installation",
                func=self._size_installation
            ),
            Tool(
                name="environmental_impact",
                description="Calcule l'impact environnemental",
                func=self._environmental_impact
            )
        ]
    
    def _get_system_prompt(self) -> str:
        """Prompt système pour le simulateur énergétique"""
        return """
        Tu es l'Agent Simulateur Énergétique du système Solar Nasih.
        
        Tu es spécialisé dans :
        
        **Calculs énergétiques :**
        - Production photovoltaïque selon localisation
        - Impact de l'orientation et inclinaison
        - Dimensionnement optimal des installations
        - Calculs de rentabilité et ROI
        - Estimations d'économies
        
        **Facteurs pris en compte :**
        - Irradiation solaire régionale
        - Coefficients d'orientation (Sud = 100%)
        - Coefficients d'inclinaison (30° = optimal)
        - Ombrage et masques
        - Consommation électrique
        - Tarifs électriques
        
        **Méthodes :**
        1. Analyse des paramètres d'entrée
        2. Calculs basés sur données météorologiques
        3. Optimisation technico-économique
        4. Projections financières
        5. Impact environnemental
        
        Fournis des résultats précis avec explications des calculs.
        Réponds en français avec des données chiffrées claires.
        """
    
    def _calculate_production(self, parameters: str) -> str:
        """Calcule la production énergétique annuelle"""
        try:
            # Parsing des paramètres (simulation)
            params = self._parse_parameters(parameters)
            
            # Récupération des données
            location = params.get("location", "default").lower()
            power_kwc = float(params.get("power", 6))
            orientation = params.get("orientation", "sud").lower()
            inclination = int(params.get("inclination", 30))
            
            # Calcul de base
            base_irradiation = self.irradiation_data.get(location, self.irradiation_data["default"])
            
            # Application des coefficients
            orientation_coef = self.orientation_coefficients.get(orientation, 0.9)
            inclination_coef = self._get_inclination_coefficient(inclination)
            
            # Production annuelle
            annual_production = power_kwc * base_irradiation * orientation_coef * inclination_coef
            
            return f"""
Calcul de production énergétique:
- Puissance installée: {power_kwc} kWc
- Localisation: {location.title()}
- Irradiation: {base_irradiation} kWh/m²/an
- Orientation: {orientation.title()} (coef: {orientation_coef})
- Inclinaison: {inclination}° (coef: {inclination_coef:.2f})

Production annuelle estimée: {annual_production:.0f} kWh/an
Production mensuelle moyenne: {annual_production/12:.0f} kWh/mois
            """
            
        except Exception as e:
            return f"Erreur dans le calcul de production: {str(e)}"
    
    def _estimate_savings(self, parameters: str) -> str:
        """Estime les économies annuelles"""
        try:
            params = self._parse_parameters(parameters)
            
            annual_production = float(params.get("production", 7000))
            electricity_price = float(params.get("price", 0.18))  # €/kWh
            self_consumption_rate = float(params.get("self_consumption", 0.7))
            injection_price = float(params.get("injection_price", 0.10))  # €/kWh
            
            # Calcul des économies
            self_consumed = annual_production * self_consumption_rate
            injected = annual_production * (1 - self_consumption_rate)
            
            savings_self_consumption = self_consumed * electricity_price
            revenue_injection = injected * injection_price
            
            total_savings = savings_self_consumption + revenue_injection
            
            return f"""
Estimation des économies annuelles:
- Production: {annual_production:.0f} kWh/an
- Taux d'autoconsommation: {self_consumption_rate*100:.0f}%
- Prix électricité: {electricity_price:.2f} €/kWh

Autoconsommation: {self_consumed:.0f} kWh → {savings_self_consumption:.0f} € économisés
Injection réseau: {injected:.0f} kWh → {revenue_injection:.0f} € de revenus

Total économies annuelles: {total_savings:.0f} €/an
            """
            
        except Exception as e:
            return f"Erreur dans le calcul d'économies: {str(e)}"
    
    def _calculate_payback(self, parameters: str) -> str:
        """Calcule le temps de retour sur investissement"""
        try:
            params = self._parse_parameters(parameters)
            
            installation_cost = float(params.get("cost", 12000))  # €
            annual_savings = float(params.get("savings", 1200))  # €/an
            
            payback_years = installation_cost / annual_savings
            
            return f"""
Calcul du retour sur investissement:
- Coût d'installation: {installation_cost:.0f} €
- Économies annuelles: {annual_savings:.0f} €/an

Temps de retour: {payback_years:.1f} ans
            """
            
        except Exception as e:
            # Fallback explicatif
            return (
                "Pour calculer le ROI (retour sur investissement) d'une installation solaire :\n"
                "1. Estimez le coût total de l'installation (ex: 12 000€).\n"
                "2. Calculez les économies annuelles sur la facture d'électricité (ex: 1 200€/an).\n"
                "3. ROI = coût / économies annuelles (ex: 12 000 / 1 200 = 10 ans).\n"
                "Le ROI correspond au nombre d'années nécessaires pour rentabiliser l'investissement."
            )
    
    def _size_installation(self, parameters: str) -> str:
        """Dimensionne l'installation selon les besoins"""
        try:
            params = self._parse_parameters(parameters)
            
            annual_consumption = float(params.get("consumption", 4000))  # kWh/an
            roof_area = float(params.get("roof_area", 50))  # m²
            budget = float(params.get("budget", 15000))  # €
            
            # Calcul de la puissance optimale
            # Hypothèse: 1 kWc ≈ 6 m² et produit 1200 kWh/an
            max_power_area = roof_area / 6  # kWc
            max_power_budget = budget / 2000  # Hypothèse: 2000€/kWc
            optimal_power = min(annual_consumption / 1200, max_power_area, max_power_budget)
            
            nb_panels = math.ceil(optimal_power / 0.4)  # Panneaux 400W
            
            return f"""
Dimensionnement optimal:
- Consommation annuelle: {annual_consumption:.0f} kWh
- Surface toit disponible: {roof_area} m²
- Budget: {budget:.0f} €

Puissance recommandée: {optimal_power:.1f} kWc
Nombre de panneaux: {nb_panels} x 400W
Surface nécessaire: {optimal_power * 6:.0f} m²
Coût estimé: {optimal_power * 2000:.0f} €
Production attendue: {optimal_power * 1200:.0f} kWh/an
            """
            
        except Exception as e:
            return f"Erreur dans le dimensionnement: {str(e)}"
    
    def _environmental_impact(self, parameters: str) -> str:
        """Calcule l'impact environnemental"""
        try:
            params = self._parse_parameters(parameters)
            
            annual_production = float(params.get("production", 7000))  # kWh/an
            
            # Facteurs d'émission
            co2_avoided_per_kwh = 0.057  # kg CO2/kWh (mix électrique français)
            
            # Calculs environnementaux
            co2_saved_annually = annual_production * co2_avoided_per_kwh
            co2_saved_20_years = co2_saved_annually * 20
            
            # Équivalences
            trees_equivalent = co2_saved_20_years / 22  # 1 arbre absorbe ~22kg CO2/an
            
            return f"""
Impact environnemental:
- Production annuelle: {annual_production:.0f} kWh
- CO2 évité par an: {co2_saved_annually:.0f} kg
- CO2 évité sur 20 ans: {co2_saved_20_years:.0f} kg
- Équivalent: {trees_equivalent:.0f} arbres plantés

Contribution positive à la transition énergétique !
            """
            
        except Exception as e:
            return f"Erreur dans le calcul d'impact environnemental: {str(e)}"
    
    def _parse_parameters(self, parameters: str) -> Dict[str, Any]:
        """Parse les paramètres d'entrée"""
        # Simulation simple de parsing
        params = {}
        
        # Extraction basique (à améliorer avec regex)
        if "kWc" in parameters:
            try:
                power = float(parameters.split("kWc")[0].split()[-1])
                params["power"] = power
            except:
                pass
        
        if "kWh" in parameters:
            try:
                consumption = float(parameters.split("kWh")[0].split()[-1])
                params["consumption"] = consumption
            except:
                pass
        
        return params
    
    def _get_inclination_coefficient(self, inclination: int) -> float:
        """Calcule le coefficient d'inclinaison"""
        # Interpolation simple
        if inclination in self.inclination_coefficients:
            return self.inclination_coefficients[inclination]
        
        # Courbe optimale autour de 30°
        if 25 <= inclination <= 35:
            return 1.0
        elif inclination < 25:
            return 0.95 + (inclination - 0) * 0.05 / 25
        else:
            return max(0.7, 1.0 - (inclination - 35) * 0.01)
    
    def can_handle(self, user_input: str, context: Dict[str, Any] = None) -> float:
        """Évalue si l'agent peut traiter la requête de simulation"""
        simulation_keywords = [
            "simulation", "calcul", "estimation", "production", "économie",
            "rentabilité", "amortissement", "rendement", "dimensionnement",
            "kWh", "kWc", "€", "retour sur investissement", "ROI"
        ]
        
        user_input_lower = user_input.lower()
        matches = sum(1 for keyword in simulation_keywords if keyword in user_input_lower)
        
        return min(matches * 0.15, 1.0)