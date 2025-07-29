#!/usr/bin/env python3
"""
Test de conversion WebM vers WAV avec ffmpeg
"""

import os
import subprocess
import tempfile
import shutil

def test_ffmpeg_conversion():
    """Test de conversion WebM vers WAV"""
    print("🧪 Test de conversion WebM vers WAV")
    print("=" * 50)
    
    # Vérifier ffmpeg
    ffmpeg_path = shutil.which('ffmpeg') or 'ffmpeg.exe'
    if not os.path.exists(ffmpeg_path) and shutil.which('ffmpeg') is None:
        print("❌ ffmpeg non trouvé")
        return False
    
    print(f"✅ ffmpeg trouvé: {ffmpeg_path}")
    
    # Créer un fichier WebM de test (silencieux)
    with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_webm:
        temp_webm_path = temp_webm.name
        # Créer un fichier WebM minimal (juste pour le test)
        temp_webm.write(b'\x1a\x45\xdf\xa3')  # Signature WebM
    
    try:
        # Chemin de sortie WAV
        temp_wav_path = temp_webm_path.replace('.webm', '.wav')
        
        print(f"📁 Fichier WebM de test: {temp_webm_path}")
        print(f"📁 Fichier WAV de sortie: {temp_wav_path}")
        
        # Commande de conversion
        cmd = [
            ffmpeg_path, '-i', temp_webm_path,
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-ac', '1',
            temp_wav_path,
            '-y'
        ]
        
        print(f"🔄 Commande: {' '.join(cmd)}")
        
        # Exécuter la conversion
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Conversion réussie!")
            if os.path.exists(temp_wav_path):
                print(f"📁 Fichier WAV créé: {temp_wav_path}")
                print(f"📏 Taille: {os.path.getsize(temp_wav_path)} bytes")
                return True
            else:
                print("❌ Fichier WAV non créé")
                return False
        else:
            print(f"❌ Erreur de conversion: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    finally:
        # Nettoyer les fichiers temporaires
        for path in [temp_webm_path, temp_wav_path]:
            if os.path.exists(path):
                os.unlink(path)
                print(f"🗑️ Fichier supprimé: {path}")

def test_voice_service():
    """Test du service vocal"""
    print("\n🎤 Test du service vocal")
    print("=" * 50)
    
    try:
        # Importer le service vocal
        import sys
        sys.path.append('SolarNasih_SMA')
        
        from services.voice_service import VoiceService
        
        voice_service = VoiceService()
        print("✅ VoiceService importé avec succès")
        
        # Test de transcription avec un fichier silencieux
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
            temp_wav_path = temp_wav.name
            # Créer un fichier WAV minimal
            temp_wav.write(b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00')
        
        try:
            result = voice_service.transcribe_audio(temp_wav_path, language='fr-FR')
            print(f"✅ Transcription test: {result}")
            return True
        except Exception as e:
            print(f"❌ Erreur transcription: {e}")
            return False
        finally:
            if os.path.exists(temp_wav_path):
                os.unlink(temp_wav_path)
                
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
        return False

if __name__ == "__main__":
    print("🎬 Test complet de ffmpeg et VoiceService")
    print("=" * 60)
    
    # Test 1: Conversion ffmpeg
    test1 = test_ffmpeg_conversion()
    
    # Test 2: Service vocal
    test2 = test_voice_service()
    
    print("\n📊 Résultats des tests:")
    print(f"✅ Conversion ffmpeg: {'PASS' if test1 else 'FAIL'}")
    print(f"✅ Service vocal: {'PASS' if test2 else 'FAIL'}")
    
    if test1 and test2:
        print("\n🎉 Tous les tests sont passés! Le système vocal est prêt.")
    else:
        print("\n⚠️ Certains tests ont échoué. Vérifiez la configuration.") 