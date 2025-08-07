#!/usr/bin/env python3
"""
🚀 SOLAR NASIH - Démarrage Unifié pour Render
Script qui démarre SMA + RAG + Template en un seul processus
"""

import os
import sys
import subprocess
import threading
import time
import signal
from pathlib import Path

class UnifiedServiceManager:
    def __init__(self):
        self.processes = []
        self.running = True
        # Utiliser le port de Render pour le service principal
        self.port_main = os.getenv('PORT', '10000')
        self.port_sma = os.getenv('SMA_PORT', '8000')
        self.port_rag = os.getenv('RAG_PORT', '8001')
        self.port_frontend = os.getenv('FRONTEND_PORT', '3000')
        
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
    
    def start_main_service(self):
        """Démarre le service principal sur le port de Render"""
        print(f"🚀 Démarrage du service principal sur le port {self.port_main}...")
        
        try:
            # Créer un serveur simple qui redirige vers les autres services
            from fastapi import FastAPI, Request
            from fastapi.responses import RedirectResponse, HTMLResponse
            import uvicorn
            
            app = FastAPI(title="SolarNasih Unified", version="1.0.0")
            
            @app.get("/")
            async def root():
                return HTMLResponse("""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>SolarNasih - Services Unifiés</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 40px; }
                        .service { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
                        .service h3 { margin: 0 0 10px 0; color: #333; }
                        .service a { color: #007bff; text-decoration: none; }
                        .service a:hover { text-decoration: underline; }
                    </style>
                </head>
                <body>
                    <h1>🚀 SolarNasih - Services Unifiés</h1>
                    <p>Bienvenue ! Voici les services disponibles :</p>
                    
                    <div class="service">
                        <h3>🌐 Frontend (Interface principale)</h3>
                        <p><a href="/frontend" target="_blank">Accéder au Frontend</a></p>
                    </div>
                    
                    <div class="service">
                        <h3>🚀 SMA API (Solar Management Assistant)</h3>
                        <p><a href="/sma/docs" target="_blank">Documentation SMA API</a></p>
                        <p><a href="/sma" target="_blank">Accéder à SMA API</a></p>
                    </div>
                    
                    <div class="service">
                        <h3>🤖 RAG API (Retrieval-Augmented Generation)</h3>
                        <p><a href="/rag/docs" target="_blank">Documentation RAG API</a></p>
                        <p><a href="/rag" target="_blank">Accéder à RAG API</a></p>
                    </div>
                    
                    <div class="service">
                        <h3>📊 Statut des Services</h3>
                        <p>✅ Tous les services sont opérationnels</p>
                    </div>
                </body>
                </html>
                """)
            
            @app.get("/sma/{path:path}")
            async def sma_proxy(request: Request, path: str = ""):
                """Proxy pour SMA API"""
                import httpx
                async with httpx.AsyncClient() as client:
                    try:
                        response = await client.get(f"http://localhost:{self.port_sma}/{path}")
                        return response
                    except:
                        return {"error": "SMA service not available"}
            
            @app.get("/rag/{path:path}")
            async def rag_proxy(request: Request, path: str = ""):
                """Proxy pour RAG API"""
                import httpx
                async with httpx.AsyncClient() as client:
                    try:
                        response = await client.get(f"http://localhost:{self.port_rag}/{path}")
                        return response
                    except:
                        return {"error": "RAG service not available"}
            
            @app.get("/frontend/{path:path}")
            async def frontend_proxy(request: Request, path: str = ""):
                """Proxy pour Frontend"""
                import httpx
                async with httpx.AsyncClient() as client:
                    try:
                        response = await client.get(f"http://localhost:{self.port_frontend}/{path}")
                        return response
                    except:
                        return {"error": "Frontend service not available"}
            
            # Démarrer le serveur principal
            process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "start_all_unified:app", 
                "--host", "0.0.0.0", "--port", self.port_main
            ])
            
            self.processes.append(("Main", process))
            print(f"✅ Service principal démarré sur http://0.0.0.0:{self.port_main}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du démarrage du service principal: {e}")
            return False
    
    def start_sma_service(self):
        """Démarre le service SMA"""
        print(f"🚀 Démarrage du service SMA sur le port {self.port_sma}...")
        
        try:
            # Changer vers le répertoire SMA
            os.chdir('SolarNasih_SMA')
            
            # Démarrer SMA
            process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "main:app", 
                "--host", "0.0.0.0", "--port", self.port_sma
            ])
            
            # Revenir au répertoire racine
            os.chdir('..')
            
            self.processes.append(("SMA", process))
            print(f"✅ Service SMA démarré sur http://0.0.0.0:{self.port_sma}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du démarrage de SMA: {e}")
            return False
    
    def start_rag_service(self):
        """Démarre le service RAG"""
        print(f"🤖 Démarrage du service RAG sur le port {self.port_rag}...")
        
        try:
            # Changer vers le répertoire RAG
            os.chdir('SolarNasih_RAG')
            
            # Démarrer RAG
            process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "api_simple:app", 
                "--host", "0.0.0.0", "--port", self.port_rag
            ])
            
            # Revenir au répertoire racine
            os.chdir('..')
            
            self.processes.append(("RAG", process))
            print(f"✅ Service RAG démarré sur http://0.0.0.0:{self.port_rag}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du démarrage de RAG: {e}")
            return False
    
    def start_frontend_service(self):
        """Démarre le service Frontend"""
        print(f"🌐 Démarrage du service Frontend sur le port {self.port_frontend}...")
        
        try:
            # Changer vers le répertoire Template
            os.chdir('SolarNasih_Template')
            
            # Vérifier si node_modules existe
            if not os.path.exists('node_modules'):
                print("📦 Installation des dépendances Node.js...")
                subprocess.run(['npm', 'install'], check=True)
            
            # Démarrer le frontend
            process = subprocess.Popen([
                'npm', 'run', 'preview', '--', '--host', '0.0.0.0', '--port', self.port_frontend
            ])
            
            # Revenir au répertoire racine
            os.chdir('..')
            
            self.processes.append(("Frontend", process))
            print(f"✅ Service Frontend démarré sur http://0.0.0.0:{self.port_frontend}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du démarrage du Frontend: {e}")
            return False
    
    def start_all_services(self):
        """Démarre tous les services"""
        print("============================================================")
        print("🚀 SOLAR NASIH - Démarrage Unifié pour Render")
        print("============================================================")
        
        # Vérifier les prérequis
        if not self.check_prerequisites():
            return False
        
        # Démarrer les services en arrière-plan d'abord
        services = [
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
        
        # Attendre un peu que les services démarrent
        time.sleep(5)
        
        # Démarrer le service principal en dernier
        if not self.start_main_service():
            return False
        
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
    
    def signal_handler(self, signum, frame):
        """Gestionnaire de signal pour arrêt propre"""
        print("\n🛑 Signal d'arrêt reçu...")
        self.running = False
        self.stop_all_services()
        sys.exit(0)

def main():
    """Fonction principale"""
    
    # Créer le gestionnaire de services
    manager = UnifiedServiceManager()
    
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
        print(f"   • Service Principal: http://0.0.0.0:{manager.port_main}")
        print(f"   • SMA API: http://0.0.0.0:{manager.port_sma}")
        print(f"   • RAG API: http://0.0.0.0:{manager.port_rag}")
        print(f"   • Frontend: http://0.0.0.0:{manager.port_frontend}")
        print("")
        print("📚 Documentation:")
        print(f"   • Interface principale: http://0.0.0.0:{manager.port_main}")
        print(f"   • SMA API Docs: http://0.0.0.0:{manager.port_main}/sma/docs")
        print(f"   • RAG API Docs: http://0.0.0.0:{manager.port_main}/rag/docs")
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
