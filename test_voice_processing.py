#!/usr/bin/env python3
"""
Test du traitement vocal
"""

import requests
import os
import wave
import numpy as np

def create_test_audio():
    """Créer un fichier audio de test simple"""
    
    # Paramètres audio
    sample_rate = 16000
    duration = 3  # secondes
    frequency = 440  # Hz (note La)
    
    # Générer un signal sinusoïdal simple
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = np.sin(2 * np.pi * frequency * t) * 0.3
    
    # Convertir en 16-bit PCM
    audio_data = (audio_data * 32767).astype(np.int16)
    
    # Sauvegarder en WAV
    with wave.open("test_audio.wav", "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    return "test_audio.wav"

def test_voice_processing():
    """Test du traitement vocal"""
    
    try:
        print("🎤 Test du traitement vocal...")
        
        # Créer un fichier audio de test
        audio_file = create_test_audio()
        
        # Upload via SMA
        with open(audio_file, "rb") as f:
            files = {"audio_file": ("test_audio.wav", f, "audio/wav")}
            response = requests.post("http://localhost:8000/voice-chat", files=files)
        
        print(f"📊 Statut: {response.status_code}")
        print(f"📄 Réponse: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Traitement vocal réussi!")
            print(f"📝 Transcription: {result.get('transcription', 'N/A')}")
            print(f"🎯 Confiance: {result.get('confidence', 'N/A')}")
            return True
        else:
            print("❌ Traitement vocal échoué")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    finally:
        # Nettoyer
        if os.path.exists("test_audio.wav"):
            os.remove("test_audio.wav")

if __name__ == "__main__":
    test_voice_processing() 