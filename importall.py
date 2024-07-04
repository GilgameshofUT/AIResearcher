import os
import PyPDF2
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import markdown
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from chromadb.config import Settings

# Usage
document_directory = "/path/to/input/files"
chroma_db_path = "/path/to/chromadb"
collection_name = "collection"

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_epub(file_path):
    book = epub.read_epub(file_path)
    text = ''
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text += soup.get_text()
    return text

def extract_text_from_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        md_text = file.read()
    html = markdown.markdown(md_text)
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()

def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def chunk_text(text, chunk_size=1000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def process_documents_to_chroma(directory_path, db_path):
    # Initialize ChromaDB
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(collection_name)

    # Process each file in the directory
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        #feedback
        print(f"processing {filename}\n")

        # Extract text based on file type
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        elif filename.endswith('.epub'):
            text = extract_text_from_epub(file_path)
        elif filename.endswith('.md'):
            text = extract_text_from_markdown(file_path)
        elif filename.endswith('.txt'):
            text = extract_text_from_txt(file_path)
        else:
            print(f"Unsupported file type: {filename}")
            continue

        #Feedback
        print('Chunking text\n')

        # Chunk the text
        chunks = chunk_text(text)

        #feedback
        print('Inserting chunks into DB\n')

        # Insert chunks into ChromaDB
        for i, chunk in enumerate(chunks):
            collection.add(
                documents=[chunk],
                metadatas=[{"source": filename, "chunk": i}],
                ids=[f"{filename}chunk{i}"]
            )

        print(f"Processed {filename}")

    print("All documents have been processed and inserted into ChromaDB.")

process_documents_to_chroma(document_directory, chroma_db_path)
