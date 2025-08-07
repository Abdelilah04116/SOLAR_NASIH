#!/usr/bin/env python3
"""
🚀 SOLAR NASIH - Serveur Principal pour Render
Ce script démarre un serveur FastAPI sur le port de Render et les autres services en arrière-plan
"""

import os
import sys
import subprocess
import threading
import time
import signal
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
import httpx

# Configuration des ports
PORT = os.getenv('PORT', '10000')
SMA_PORT = os.getenv('SMA_PORT', '8000')
RAG_PORT = os.getenv('RAG_PORT', '8001')
FRONTEND_PORT = os.getenv('FRONTEND_PORT', '3000')

# Variables globales pour les processus
processes = []
running = True

# Créer l'application FastAPI
app = FastAPI(title="SolarNasih Unified", version="1.0.0")

@app.get("/")
async def root():
    """Page d'accueil avec liens vers tous les services"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SolarNasih - Services Unifiés</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 40px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.1);
                padding: 30px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }
            .service { 
                margin: 20px 0; 
                padding: 20px; 
                border: 1px solid rgba(255, 255, 255, 0.3); 
                border-radius: 10px; 
                background: rgba(255, 255, 255, 0.1);
            }
            .service h3 { 
                margin: 0 0 15px 0; 
                color: #fff; 
                font-size: 1.3em;
            }
            .service a { 
                color: #ffd700; 
                text-decoration: none; 
                font-weight: bold;
                margin-right: 15px;
            }
            .service a:hover { 
                text-decoration: underline; 
                color: #fff;
            }
            h1 {
                text-align: center;
                margin-bottom: 30px;
                font-size: 2.5em;
            }
            .status {
                text-align: center;
                margin: 20px 0;
                padding: 10px;
                background: rgba(0, 255, 0, 0.2);
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 SolarNasih - Services Unifiés</h1>
            
            <div class="status">
                <h3>✅ Tous les services sont opérationnels</h3>
            </div>
            
            <div class="service">
                <h3>🌐 Frontend (Interface principale)</h3>
                <p>Interface utilisateur React/TypeScript</p>
                <a href="/frontend" target="_blank">Accéder au Frontend</a>
            </div>
            
            <div class="service">
                <h3>🚀 SMA API (Solar Management Assistant)</h3>
                <p>API pour l'assistant de gestion solaire</p>
                <a href="/sma/docs" target="_blank">Documentation SMA API</a>
                <a href="/sma" target="_blank">Accéder à SMA API</a>
            </div>
            
            <div class="service">
                <h3>🤖 RAG API (Retrieval-Augmented Generation)</h3>
                <p>API pour la génération augmentée par récupération</p>
                <a href="/rag/docs" target="_blank">Documentation RAG API</a>
                <a href="/rag" target="_blank">Accéder à RAG API</a>
            </div>
            
            <div class="service">
                <h3>📊 Informations Techniques</h3>
                <p><strong>Port principal:</strong> """ + PORT + """</p>
                <p><strong>Port SMA:</strong> """ + SMA_PORT + """</p>
                <p><strong>Port RAG:</strong> """ + RAG_PORT + """</p>
                <p><strong>Port Frontend:</strong> """ + FRONTEND_PORT + """</p>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/sma/{path:path}")
async def sma_proxy(request: Request, path: str = ""):
    """Proxy pour SMA API"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"http://localhost:{SMA_PORT}/{path}"
            if request.query_params:
                url += "?" + str(request.query_params)
            
            if request.method == "GET":
                response = await client.get(url)
            elif request.method == "POST":
                response = await client.post(url, json=await request.json())
            else:
                response = await client.request(request.method, url)
            
            return response
    except Exception as e:
        return {"error": f"SMA service not available: {str(e)}"}

@app.get("/rag/{path:path}")
async def rag_proxy(request: Request, path: str = ""):
    """Proxy pour RAG API"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"http://localhost:{RAG_PORT}/{path}"
            if request.query_params:
                url += "?" + str(request.query_params)
            
            if request.method == "GET":
                response = await client.get(url)
            elif request.method == "POST":
                response = await client.post(url, json=await request.json())
            else:
                response = await client.request(request.method, url)
            
            return response
    except Exception as e:
        return {"error": f"RAG service not available: {str(e)}"}

@app.get("/frontend/{path:path}")
async def frontend_proxy(request: Request, path: str = ""):
    """Proxy pour Frontend"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"http://localhost:{FRONTEND_PORT}/{path}"
            if request.query_params:
                url += "?" + str(request.query_params)
            
            response = await client.get(url)
            return response
    except Exception as e:
        return {"error": f"Frontend service not available: {str(e)}"}

def start_sma_service():
    """Démarre le service SMA"""
    print(f"🚀 Démarrage du service SMA sur le port {SMA_PORT}...")
    
    try:
        os.chdir('SolarNasih_SMA')
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app", 
            "--host", "0.0.0.0", "--port", SMA_PORT
        ])
        os.chdir('..')
        processes.append(("SMA", process))
        print(f"✅ Service SMA démarré sur http://localhost:{SMA_PORT}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors du démarrage de SMA: {e}")
        return False

def start_rag_service():
    """Démarre le service RAG"""
    print(f"🤖 Démarrage du service RAG sur le port {RAG_PORT}...")
    
    try:
        os.chdir('SolarNasih_RAG')
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "api_simple:app", 
            "--host", "0.0.0.0", "--port", RAG_PORT
        ])
        os.chdir('..')
        processes.append(("RAG", process))
        print(f"✅ Service RAG démarré sur http://localhost:{RAG_PORT}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors du démarrage de RAG: {e}")
        return False

def start_frontend_service():
    """Démarre le service Frontend"""
    print(f"🌐 Démarrage du service Frontend sur le port {FRONTEND_PORT}...")
    
    try:
        os.chdir('SolarNasih_Template')
        
        # Vérifier si node_modules existe
        if not os.path.exists('node_modules'):
            print("📦 Installation des dépendances Node.js...")
            subprocess.run(['npm', 'install'], check=True)
        
        process = subprocess.Popen([
            'npm', 'run', 'preview', '--', '--host', '0.0.0.0', '--port', FRONTEND_PORT
        ])
        os.chdir('..')
        processes.append(("Frontend", process))
        print(f"✅ Service Frontend démarré sur http://localhost:{FRONTEND_PORT}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors du démarrage du Frontend: {e}")
        return False

def start_background_services():
    """Démarre tous les services en arrière-plan"""
    print("============================================================")
    print("🚀 SOLAR NASIH - Démarrage des Services en Arrière-plan")
    print("============================================================")
    
    # Démarrer les services en parallèle
    services = [start_sma_service, start_rag_service, start_frontend_service]
    
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

def stop_all_services():
    """Arrête tous les services"""
    print("\n🛑 Arrêt de tous les services...")
    
    for name, process in processes:
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

def signal_handler(signum, frame):
    """Gestionnaire de signal pour arrêt propre"""
    print("\n🛑 Signal d'arrêt reçu...")
    global running
    running = False
    stop_all_services()
    sys.exit(0)

if __name__ == "__main__":
    # Configurer les gestionnaires de signal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Démarrer les services en arrière-plan
    background_thread = threading.Thread(target=start_background_services)
    background_thread.daemon = True
    background_thread.start()
    
    print("============================================================")
    print("🎉 SERVEUR PRINCIPAL DÉMARRÉ !")
    print("============================================================")
    print(f"📊 Service principal: http://0.0.0.0:{PORT}")
    print(f"📚 Documentation: http://0.0.0.0:{PORT}/docs")
    print("============================================================")
    
    # Démarrer le serveur FastAPI
    uvicorn.run(app, host="0.0.0.0", port=int(PORT))
