import chromadb
import importlib
import sys
import os
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import google.generativeai as genai
from datetime import datetime


def load_config(config_file):
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add the script directory to sys.path
    sys.path.insert(0, script_dir)
    
    # Remove the .py extension if present
    if config_file.endswith('.py'):
        config_file = config_file[:-3]
    
    # Import the config module dynamically
    config = importlib.import_module(config_file)
    
    # Remove the script directory from sys.path
    sys.path.pop(0)
    
    return config

def setup_chroma_client(db_path, collection_name):
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_collection(collection_name)
    return collection

def query_chroma(collection, query, n_results):
    embedding_func = embedding_functions.DefaultEmbeddingFunction()
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    
    return results

def setup_gemini(model_name, system_instruction, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name=model_name, safety_settings=None, system_instruction=system_instruction)    
    return model

def query_gemini(model, context, question):
    prompt = f"""Context: \n{context}\n\nQuestion: \n{question}"""

    response = model.generate_content(prompt)
    return response.text

def log_full_query(query, context, metadata, query_file):
    with open(query_file, 'a') as f:
        f.write(f"--- Query at {datetime.now()} ---\n")
        f.write(f"Question:\n{query}\n\n------------------------------\n")
        f.write(f"Context:\n{context}\n\n")
        f.write("\nMetadata of sources:\n")
        for i, meta in enumerate(metadata, 1):
            f.write(f"Source {i}:")
            for key, value in meta.items():
                f.write(f"  {key}: {value}")

def log_conversation(question, answer, metadata, distances, conversation_file):
    with open(conversation_file, 'a') as f:
        f.write(f"\n---\n## Query at {datetime.now()}\n---\n")
        f.write(f"> [!Question]\n{question}\n\n")
        f.write(f"### Answer\n\n{answer}\n\n")
        f.write("\n```\nMetadata of sources:\n")
        for i, (meta, dist) in enumerate(zip(metadata, distances), 1):
            f.write(f"  Source {i}:")
            for key, value in meta.items():
                f.write(f"    {key}: {value}\n")
            f.write(f"    Distance: {dist:.4f}\n")
        f.write("```\n\n")


def read_last_lines(filename, n_lines):
    try:
        with open(filename, 'r') as file:
            all_lines = file.readlines()
            last_lines = all_lines[-n_lines:]
            history = '\n\n**Conversation History**\n\n'.join(last_lines)
            return history
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def main(config):
    history = ''
    collection = setup_chroma_client(config.DB_PATH, config.CHROMA_COLLECTION)
    gemini_model = setup_gemini(config.MODEL_NAME, config.SYSTEM_INSTRUCTION, config.GOOGLE_API_KEY)
    
    while True:
        query = input("\nWhat now? (or 'quit' or 'forget'): ")
        if query.lower() == 'quit':
            break
        if query.lower() == 'forget':
            history = ''
            continue

        # Query ChromaDB
        results = query_chroma(collection, query, config.N_RESULTS)
        
        # Prepare context, metadata, and distances from ChromaDB results
        context = "\n\n".join([doc for doc in results['documents'][0]])
        metadata = results['metadatas'][0]
        distances = results['distances'][0]
        
        # Log the full query with context, metadata, and distances
        log_full_query(query, context, metadata, config.QUERY_FILE)

        # Query Gemini
        answer = query_gemini(gemini_model, context, query)
        
        # Log the conversation
        log_conversation(query, answer, metadata, distances, config.CONVERSATION_FILE)

        # Append query and answer to history
        history += '\n' + query + '\n' + answer
        
        # Print Gemini's answer and metadata to the terminal
        print("\nGemini's answer:")
        print(answer)
        print("\nMetadata of sources:")
        for i, (meta, dist) in enumerate(zip(metadata, distances), 1):
            print(f"Source {i}:")
            for key, value in meta.items():
                print(f"  {key}: {value}")
                print(f"  Distance: {dist:.4f}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 research-main.py <config_file>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    config = load_config(config_file)
    main(config)