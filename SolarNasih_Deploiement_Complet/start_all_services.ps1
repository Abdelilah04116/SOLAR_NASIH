# 🚀 SOLAR NASIH - Démarrage Unifié (PowerShell)
# Script pour démarrer tous les services avec une seule commande

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🚀 SOLAR NASIH - Démarrage de Tous les Services" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

# Vérification des prérequis
Write-Host "🔍 Vérification des prérequis..." -ForegroundColor Yellow

if (-not (Test-Path "SolarNasih_SMA") -or -not (Test-Path "SolarNasih_RAG") -or -not (Test-Path "SolarNasih_Template")) {
    Write-Host "❌ Erreur: Composants manquants" -ForegroundColor Red
    Write-Host "   Assurez-vous d'être dans le répertoire racine du projet" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Tous les composants trouvés" -ForegroundColor Green

# Installation des dépendances Python
Write-Host "📦 Installation des dépendances unifiées..." -ForegroundColor Yellow
try {
    python -m pip install -r SolarNasih_Deploiement_Complet/requirements_unified.txt
    Write-Host "✅ Dépendances Python installées" -ForegroundColor Green
} catch {
    Write-Host "❌ Erreur lors de l'installation des dépendances Python" -ForegroundColor Red
    exit 1
}

# Installation des dépendances Node.js
Write-Host "📦 Installation des dépendances Node.js..." -ForegroundColor Yellow
try {
    Set-Location SolarNasih_Template
    if (-not (Test-Path "node_modules")) {
        npm install
    }
    Set-Location ..
    Write-Host "✅ Dépendances Node.js installées" -ForegroundColor Green
} catch {
    Write-Host "❌ Erreur lors de l'installation des dépendances Node.js" -ForegroundColor Red
    exit 1
}

# Démarrage des services
Write-Host "🚀 Démarrage de tous les services..." -ForegroundColor Yellow

# Démarrer Redis avec Docker (si disponible)
try {
    docker run --name solar-nasih-redis -p 6379:6379 -d redis:alpine
    Write-Host "✅ Redis démarré avec Docker" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Redis non disponible (Docker requis)" -ForegroundColor Yellow
}

# Démarrer Qdrant avec Docker (si disponible)
try {
    docker run --name solar-nasih-qdrant -p 6333:6333 -p 6334:6334 -d qdrant/qdrant:latest
    Write-Host "✅ Qdrant démarré avec Docker" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Qdrant non disponible (Docker requis)" -ForegroundColor Yellow
}

# Démarrer SMA
Write-Host "🚀 Démarrage du service SMA..." -ForegroundColor Yellow
$smaJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD\SolarNasih_SMA
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
}

# Démarrer RAG
Write-Host "🤖 Démarrage du service RAG..." -ForegroundColor Yellow
$ragJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD\SolarNasih_RAG
    python -m uvicorn api_simple:app --host 0.0.0.0 --port 8001 --reload
}

# Démarrer Frontend
Write-Host "🌐 Démarrage du service Frontend..." -ForegroundColor Yellow
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD\SolarNasih_Template
    npm run dev
}

# Attendre un peu pour que les services démarrent
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🎉 TOUS LES SERVICES SONT DÉMARRÉS !" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Services disponibles:" -ForegroundColor White
Write-Host "   • SMA API: http://localhost:8000" -ForegroundColor Gray
Write-Host "   • RAG API: http://localhost:8001" -ForegroundColor Gray
Write-Host "   • Frontend: http://localhost:5173" -ForegroundColor Gray
Write-Host "   • Redis: localhost:6379" -ForegroundColor Gray
Write-Host "   • Qdrant: localhost:6333" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor White
Write-Host "   • SMA API Docs: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "   • RAG API Docs: http://localhost:8001/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "🛑 Appuyez sur Ctrl+C pour arrêter tous les services" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan

# Fonction pour arrêter tous les services
function Stop-AllServices {
    Write-Host "🛑 Arrêt de tous les services..." -ForegroundColor Yellow
    
    # Arrêter les jobs PowerShell
    Stop-Job $smaJob -ErrorAction SilentlyContinue
    Stop-Job $ragJob -ErrorAction SilentlyContinue
    Stop-Job $frontendJob -ErrorAction SilentlyContinue
    
    Remove-Job $smaJob -ErrorAction SilentlyContinue
    Remove-Job $ragJob -ErrorAction SilentlyContinue
    Remove-Job $frontendJob -ErrorAction SilentlyContinue
    
    # Arrêter les conteneurs Docker
    try {
        docker stop solar-nasih-redis
        docker rm solar-nasih-redis
        docker stop solar-nasih-qdrant
        docker rm solar-nasih-qdrant
    } catch {
        # Ignorer les erreurs si Docker n'est pas disponible
    }
    
    Write-Host "✅ Tous les services arrêtés" -ForegroundColor Green
    exit 0
}

# Configurer le gestionnaire d'interruption
$null = Register-EngineEvent PowerShell.Exiting -Action { Stop-AllServices }

try {
    # Maintenir le script en vie
    while ($true) {
        Start-Sleep -Seconds 1
    }
} catch {
    Stop-AllServices
}
