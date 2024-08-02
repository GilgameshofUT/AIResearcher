import os
import chromadb
from chromadb.config import Settings

# Usage
chroma_db_path = "/path/to/chromadb"
collection_name = "collection"


# Initialize ChromaDB
client = chromadb.PersistentClient(path=chroma_db_path)

#DELETE!!!!
client.delete_collection(name=collection_name)

print(f"Collection {collection_name} has been deleted.")
