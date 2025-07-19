import logging
from pathlib import Path
from sentence_transformers import SentenceTransformer
import clip
import whisper

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_text_models():
    """Download and save text embedding models."""
    logger.info("📘 Downloading text embedding models...")
    models = [
        "all-MiniLM-L6-v2",
        "all-mpnet-base-v2"
    ]

    for model_name in models:
        try:
            logger.info(f"⬇️ Downloading {model_name}...")
            model = SentenceTransformer(model_name)

            # Save model
            save_path = Path("models/embeddings/text") / model_name.replace("/", "_")
            save_path.mkdir(parents=True, exist_ok=True)
            model.save(str(save_path))

            logger.info(f"✅ {model_name} downloaded and saved to {save_path}")
        except Exception as e:
            logger.error(f"❌ Failed to download {model_name}: {str(e)}")

def download_image_models():
    """Download CLIP image model."""
    logger.info("🖼️ Downloading image models...")

    try:
        logger.info("⬇️ Downloading CLIP ViT-B/32...")
        model, preprocess = clip.load("ViT-B/32")
        logger.info("✅ CLIP ViT-B/32 model downloaded successfully")
    except Exception as e:
        logger.error(f"❌ Failed to download CLIP: {str(e)}")

def download_audio_models():
    """Download Whisper audio models."""
    logger.info("🔊 Downloading audio models...")
    models = ["base", "small"]

    for model_size in models:
        try:
            logger.info(f"⬇️ Downloading Whisper {model_size}...")
            model = whisper.load_model(model_size)
            logger.info(f"✅ Whisper {model_size} downloaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to download Whisper {model_size}: {str(e)}")

def main():
    """Main entry point for downloading all models."""
    logger.info("🚀 Starting model downloads...")

    # Create base model directory
    Path("models").mkdir(exist_ok=True)

    download_text_models()
    download_image_models()
    download_audio_models()

    logger.info("🏁 All models downloaded successfully.")

if __name__ == "__main__":
    main()
