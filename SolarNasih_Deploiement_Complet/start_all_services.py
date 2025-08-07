#!/usr/bin/env python3
"""
🚀 SOLAR NASIH - Démarrage Unifié de Tous les Services
Script pour démarrer SMA + RAG + Frontend + Services avec une seule commande
"""

import os
import sys
import subprocess
import threading
import time
import signal
import platform
from pathlib import Path

class ServiceManager:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def check_prerequisites(self):
        """Vérifie les prérequis"""
        print("🔍 Vérification des prérequis...")
        
        required_dirs = ['SolarNasih_SMA', 'SolarNasih_RAG', 'SolarNasih_Template']
        for dir_name in required_dirs:
            if not os.path.exists(dir_name):
                print(f"❌ Erreur: Répertoire {dir_name} non trouvé")
                return False
        
        print("✅ Tous les composants trouvés")
        return True
    
    def install_dependencies(self):
        """Installe les dépendances unifiées"""
        print("📦 Installation des dépendances unifiées...")
        
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", 
                "SolarNasih_Deploiement_Complet/requirements_unified.txt"
            ], check=True)
            print("✅ Dépendances installées")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de l'installation: {e}")
            return False
    
    def start_sma_service(self):
        """Démarre le service SMA"""
        print("🚀 Démarrage du service SMA...")
        
        try:
            # Changer vers le répertoire SMA
            os.chdir('SolarNasih_SMA')
            
            # Démarrer SMA
            process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "main:app", 
                "--host", "0.0.0.0", "--port", "8000", "--reload"
            ])
            
            # Revenir au répertoire racine
            os.chdir('..')
            
            self.processes.append(("SMA", process))
            print("✅ Service SMA démarré sur http://localhost:8000")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du démarrage de SMA: {e}")
            return False
    
    def start_rag_service(self):
        """Démarre le service RAG"""
        print("🤖 Démarrage du service RAG...")
        
        try:
            # Changer vers le répertoire RAG
            os.chdir('SolarNasih_RAG')
            
            # Démarrer RAG
            process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "api_simple:app", 
                "--host", "0.0.0.0", "--port", "8001", "--reload"
            ])
            
            # Revenir au répertoire racine
            os.chdir('..')
            
            self.processes.append(("RAG", process))
            print("✅ Service RAG démarré sur http://localhost:8001")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du démarrage de RAG: {e}")
            return False
    
    def start_frontend_service(self):
        """Démarre le service Frontend"""
        print("🌐 Démarrage du service Frontend...")
        
        try:
            # Changer vers le répertoire Template
            os.chdir('SolarNasih_Template')
            
            # Vérifier si node_modules existe
            if not os.path.exists('node_modules'):
                print("📦 Installation des dépendances Node.js...")
                subprocess.run(['npm', 'install'], check=True)
            
            # Démarrer le frontend
            process = subprocess.Popen([
                'npm', 'run', 'dev'
            ])
            
            # Revenir au répertoire racine
            os.chdir('..')
            
            self.processes.append(("Frontend", process))
            print("✅ Service Frontend démarré sur http://localhost:5173")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du démarrage du Frontend: {e}")
            return False
    
    def start_redis_service(self):
        """Démarre Redis (si disponible)"""
        print("🗄️ Vérification de Redis...")
        
        try:
            # Essayer de démarrer Redis avec Docker
            process = subprocess.Popen([
                'docker', 'run', '--name', 'solar-nasih-redis', 
                '-p', '6379:6379', '-d', 'redis:alpine'
            ])
            
            self.processes.append(("Redis", process))
            print("✅ Redis démarré avec Docker sur localhost:6379")
            return True
            
        except Exception as e:
            print("⚠️ Redis non disponible (Docker requis)")
            return False
    
    def start_qdrant_service(self):
        """Démarre Qdrant (si disponible)"""
        print("🔍 Vérification de Qdrant...")
        
        try:
            # Essayer de démarrer Qdrant avec Docker
            process = subprocess.Popen([
                'docker', 'run', '--name', 'solar-nasih-qdrant',
                '-p', '6333:6333', '-p', '6334:6334', '-d', 'qdrant/qdrant:latest'
            ])
            
            self.processes.append(("Qdrant", process))
            print("✅ Qdrant démarré avec Docker sur localhost:6333")
            return True
            
        except Exception as e:
            print("⚠️ Qdrant non disponible (Docker requis)")
            return False
    
    def start_all_services(self):
        """Démarre tous les services"""
        print("============================================================")
        print("🚀 SOLAR NASIH - Démarrage de Tous les Services")
        print("============================================================")
        
        # Vérifier les prérequis
        if not self.check_prerequisites():
            return False
        
        # Installer les dépendances
        if not self.install_dependencies():
            return False
        
        # Démarrer les services en parallèle
        services = [
            self.start_redis_service,
            self.start_qdrant_service,
            self.start_sma_service,
            self.start_rag_service,
            self.start_frontend_service
        ]
        
        threads = []
        for service in services:
            thread = threading.Thread(target=service)
            thread.daemon = True
            thread.start()
            threads.append(thread)
            time.sleep(2)  # Délai entre les démarrages
        
        # Attendre que tous les threads se terminent
        for thread in threads:
            thread.join()
        
        return True
    
    def stop_all_services(self):
        """Arrête tous les services"""
        print("\n🛑 Arrêt de tous les services...")
        
        for name, process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} arrêté")
            except:
                try:
                    process.kill()
                    print(f"🔪 {name} forcé à s'arrêter")
                except:
                    pass
        
        # Nettoyer les conteneurs Docker
        try:
            subprocess.run(['docker', 'stop', 'solar-nasih-redis'], check=False)
            subprocess.run(['docker', 'rm', 'solar-nasih-redis'], check=False)
            subprocess.run(['docker', 'stop', 'solar-nasih-qdrant'], check=False)
            subprocess.run(['docker', 'rm', 'solar-nasih-qdrant'], check=False)
        except:
            pass
    
    def signal_handler(self, signum, frame):
        """Gestionnaire de signal pour arrêt propre"""
        print("\n🛑 Signal d'arrêt reçu...")
        self.running = False
        self.stop_all_services()
        sys.exit(0)

def main():
    """Fonction principale"""
    
    # Créer le gestionnaire de services
    manager = ServiceManager()
    
    # Configurer les gestionnaires de signal
    signal.signal(signal.SIGINT, manager.signal_handler)
    signal.signal(signal.SIGTERM, manager.signal_handler)
    
    # Démarrer tous les services
    if manager.start_all_services():
        print("\n============================================================")
        print("🎉 TOUS LES SERVICES SONT DÉMARRÉS !")
        print("============================================================")
        print("")
        print("📊 Services disponibles:")
        print("   • SMA API: http://localhost:8000")
        print("   • RAG API: http://localhost:8001")
        print("   • Frontend: http://localhost:5173")
        print("   • Redis: localhost:6379")
        print("   • Qdrant: localhost:6333")
        print("")
        print("📚 Documentation:")
        print("   • SMA API Docs: http://localhost:8000/docs")
        print("   • RAG API Docs: http://localhost:8001/docs")
        print("")
        print("🛑 Appuyez sur Ctrl+C pour arrêter tous les services")
        print("============================================================")
        
        # Maintenir le script en vie
        try:
            while manager.running:
                time.sleep(1)
        except KeyboardInterrupt:
            manager.signal_handler(signal.SIGINT, None)
    else:
        print("❌ Erreur lors du démarrage des services")
        sys.exit(1)

if __name__ == "__main__":
    main()
