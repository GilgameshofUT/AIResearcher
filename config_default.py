import os

# ChromaDB Configuration
CHROMA_COLLECTION = 'collection'
DB_PATH = "/path/to/chromadb"  # Update this to your ChromaDB path

# Google AI Configuration
GOOGLE_API_KEY = '<APIKEYHERE>'
MODEL_NAME = 'gemini-1.5-pro'

# File Paths
QUERY_FILE = 'queries.txt' #Mostly just a log file
CONVERSATION_FILE = '/home/user/obsidian/vault/Research.md'

# Query Configuration
N_RESULTS = 20

# System Instruction, play with this a bit maybe customize it to your subject
SYSTEM_INSTRUCTION = """You are an experienced research assistant. You will answer with 
detailed, lengthy college level answers, using headings, bold, and bullet points as appropriate for clarity. Answer the question 
based on the provided context. If the context doesn't contain enough information to answer the question fully, say so and provide 
the best answer you can with the available information.
Always provide your answer in markdown."""

# Conversation History Configuration. Not sure this is really helpful.
N_HISTORY_LINES = 10  # Number of lines to read from the conversation history
