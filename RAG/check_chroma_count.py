from config import VectorStoreConfig
from vector_store import ChromaVectorStore

# Utilise la même config que ton pipeline
config = VectorStoreConfig()
store = ChromaVectorStore(config)
print(f"Nombre de chunks/documents dans la collection ChromaDB : {store.get_chunk_count()}")