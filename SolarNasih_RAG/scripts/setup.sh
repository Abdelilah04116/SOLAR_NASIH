# RAG Multimodal System Setup Script

echo "🚀 Setting up RAG Multimodal System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/{raw,processed,cache}
mkdir -p data/raw/{documents,images,audio,video}
mkdir -p data/processed/{chunks,embeddings,metadata}
mkdir -p models/{embeddings,llm}
mkdir -p models/embeddings/{text,image,audio}
mkdir -p models/llm/local_models
mkdir -p logs

# Copy environment file
echo "⚙️ Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys"
fi

# Install system dependencies
echo "🔧 Installing system dependencies..."

# For Ubuntu/Debian
if command -v apt-get &> /dev/null; then
    echo "Installing dependencies for Ubuntu/Debian..."
    sudo apt-get update
    sudo apt-get install -y ffmpeg tesseract-ocr poppler-utils
fi

# For macOS
if command -v brew &> /dev/null; then
    echo "Installing dependencies for macOS..."
    brew install ffmpeg tesseract poppler
fi

# Download models
echo "🤖 Downloading models..."
python scripts/install_models.py

# Initialize database
echo "🗄️ Initializing database..."
python scripts/migrate_db.py

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Start the services: docker-compose up -d"
echo "3. Run the API: python src/api/main.py"
echo "4. Run the frontend: streamlit run frontend/app.py"
