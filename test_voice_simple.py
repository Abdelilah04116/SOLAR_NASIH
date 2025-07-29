#!/usr/bin/env python3
"""
Test simple du traitement vocal
"""

import requests
import os

def create_simple_audio():
    """Créer un fichier audio simple avec Python standard"""
    
    # Créer un fichier WAV simple avec des données silencieuses
    sample_rate = 16000
    duration = 2  # secondes
    num_samples = sample_rate * duration
    
    # Données silencieuses (16-bit PCM)
    audio_data = b'\x00\x00' * num_samples  # 2 bytes par sample
    
    # En-tête WAV
    wav_header = (
        b'RIFF' +  # Chunk ID
        (36 + len(audio_data)).to_bytes(4, 'little') +  # Chunk Size
        b'WAVE' +  # Format
        b'fmt ' +  # Subchunk1 ID
        (16).to_bytes(4, 'little') +  # Subchunk1 Size
        (1).to_bytes(2, 'little') +  # Audio Format (PCM)
        (1).to_bytes(2, 'little') +  # Num Channels (Mono)
        sample_rate.to_bytes(4, 'little') +  # Sample Rate
        (sample_rate * 2).to_bytes(4, 'little') +  # Byte Rate
        (2).to_bytes(2, 'little') +  # Block Align
        (16).to_bytes(2, 'little') +  # Bits Per Sample
        b'data' +  # Subchunk2 ID
        len(audio_data).to_bytes(4, 'little') +  # Subchunk2 Size
        audio_data  # Audio Data
    )
    
    with open("test_simple.wav", "wb") as f:
        f.write(wav_header)
    
    return "test_simple.wav"

def test_voice_processing():
    """Test du traitement vocal"""
    
    try:
        print("🎤 Test du traitement vocal...")
        
        # Créer un fichier audio de test
        audio_file = create_simple_audio()
        
        # Upload via SMA
        with open(audio_file, "rb") as f:
            files = {"audio_file": ("test_simple.wav", f, "audio/wav")}
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
        if os.path.exists("test_simple.wav"):
            os.remove("test_simple.wav")

if __name__ == "__main__":
    test_voice_processing() 