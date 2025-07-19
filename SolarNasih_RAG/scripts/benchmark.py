#!/usr/bin/env python3
"""
Script de benchmark pour évaluer les performances du système RAG multimodal.
Mesure les temps de réponse, la précision, le recall et d'autres métriques.
"""

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any
import requests
import pandas as pd
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGBenchmark:
    """Classe pour effectuer des benchmarks du système RAG."""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.results = []
        
    def load_test_queries(self, queries_file: str) -> List[Dict[str, Any]]:
        """Charge les requêtes de test depuis un fichier JSON."""
        try:
            with open(queries_file, 'r', encoding='utf-8') as f:
                queries = json.load(f)
            logger.info(f"✅ Chargé {len(queries)} requêtes de test")
            return queries
        except FileNotFoundError:
            logger.error(f"❌ Fichier de requêtes non trouvé: {queries_file}")
            return []
        except json.JSONDecodeError:
            logger.error(f"❌ Erreur de format JSON dans: {queries_file}")
            return []
    
    def test_single_query(self, query: str, expected_answer: str = None) -> Dict[str, Any]:
        """Teste une requête unique et mesure les performances."""
        start_time = time.time()
        
        try:
            # Appel à l'API
            response = requests.post(
                f"{self.api_url}/search",
                json={"query": query},
                timeout=30
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "query": query,
                    "response_time": response_time,
                    "status": "success",
                    "response": result.get("response", ""),
                    "sources_count": len(result.get("sources", [])),
                    "expected_answer": expected_answer
                }
            else:
                return {
                    "query": query,
                    "response_time": response_time,
                    "status": "error",
                    "error": f"HTTP {response.status_code}",
                    "expected_answer": expected_answer
                }
                
        except requests.exceptions.RequestException as e:
            end_time = time.time()
            return {
                "query": query,
                "response_time": end_time - start_time,
                "status": "error",
                "error": str(e),
                "expected_answer": expected_answer
            }
    
    def run_benchmark(self, queries: List[Dict[str, Any]]) -> pd.DataFrame:
        """Exécute le benchmark complet."""
        logger.info(f"🚀 Démarrage du benchmark avec {len(queries)} requêtes")
        
        for i, query_data in enumerate(queries, 1):
            query = query_data.get("query", "")
            expected = query_data.get("expected_answer", "")
            
            logger.info(f"📝 Test {i}/{len(queries)}: {query[:50]}...")
            result = self.test_single_query(query, expected)
            self.results.append(result)
            
            # Pause entre les requêtes pour éviter la surcharge
            time.sleep(0.5)
        
        return pd.DataFrame(self.results)
    
    def calculate_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcule les métriques de performance."""
        successful_queries = df[df["status"] == "success"]
        
        metrics = {
            "total_queries": len(df),
            "successful_queries": len(successful_queries),
            "success_rate": len(successful_queries) / len(df) if len(df) > 0 else 0,
            "avg_response_time": successful_queries["response_time"].mean() if len(successful_queries) > 0 else 0,
            "min_response_time": successful_queries["response_time"].min() if len(successful_queries) > 0 else 0,
            "max_response_time": successful_queries["response_time"].max() if len(successful_queries) > 0 else 0,
            "avg_sources_count": successful_queries["sources_count"].mean() if len(successful_queries) > 0 else 0
        }
        
        return metrics
    
    def save_results(self, df: pd.DataFrame, metrics: Dict[str, Any], output_dir: str = "benchmark_results"):
        """Sauvegarde les résultats du benchmark."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sauvegarde des résultats détaillés
        results_file = output_path / f"benchmark_results_{timestamp}.csv"
        df.to_csv(results_file, index=False)
        
        # Sauvegarde des métriques
        metrics_file = output_path / f"benchmark_metrics_{timestamp}.json"
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Résultats sauvegardés dans {output_path}")
        return str(output_path)

def main():
    """Fonction principale du script de benchmark."""
    parser = argparse.ArgumentParser(description="Benchmark du système RAG multimodal")
    parser.add_argument("--queries", "-q", required=True, help="Fichier JSON contenant les requêtes de test")
    parser.add_argument("--api-url", "-u", default="http://localhost:8000", help="URL de l'API RAG")
    parser.add_argument("--output-dir", "-o", default="benchmark_results", help="Dossier de sortie pour les résultats")
    
    args = parser.parse_args()
    
    # Initialisation du benchmark
    benchmark = RAGBenchmark(args.api_url)
    
    # Chargement des requêtes
    queries = benchmark.load_test_queries(args.queries)
    if not queries:
        logger.error("❌ Aucune requête chargée. Arrêt du benchmark.")
        return
    
    # Exécution du benchmark
    results_df = benchmark.run_benchmark(queries)
    
    # Calcul des métriques
    metrics = benchmark.calculate_metrics(results_df)
    
    # Affichage des résultats
    print("\n" + "="*50)
    print("📊 RÉSULTATS DU BENCHMARK")
    print("="*50)
    print(f"Requêtes totales: {metrics['total_queries']}")
    print(f"Requêtes réussies: {metrics['successful_queries']}")
    print(f"Taux de succès: {metrics['success_rate']:.2%}")
    print(f"Temps de réponse moyen: {metrics['avg_response_time']:.2f}s")
    print(f"Temps de réponse min: {metrics['min_response_time']:.2f}s")
    print(f"Temps de réponse max: {metrics['max_response_time']:.2f}s")
    print(f"Nombre moyen de sources: {metrics['avg_sources_count']:.1f}")
    print("="*50)
    
    # Sauvegarde des résultats
    output_path = benchmark.save_results(results_df, metrics, args.output_dir)
    print(f"📁 Résultats sauvegardés dans: {output_path}")

if __name__ == "__main__":
    main()
