import os
import PyPDF2
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import markdown
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from chromadb.config import Settings
import warnings

# Usage
document_directory = "/home/abba/codeprojects/chromadb/startrek"
chroma_db_path = "/home/abba/codeprojects/chromadb/chromadb"
collection_name = "startrek"

#supress an annoying warning
warnings.filterwarnings("ignore", category=UserWarning, module="ebooklib.epub")
warnings.filterwarnings("ignore", category=FutureWarning, module="ebooklib.epub")


def extract_text_from_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error processing PDF {file_path}: {str(e)}")
        return None

def extract_text_from_epub(file_path):
    try:
        book = epub.read_epub(file_path)
        text = ''
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                text += soup.get_text()
        return text
    except Exception as e:
        print(f"Error processing EPUB {file_path}: {str(e)}")
        return None

def extract_text_from_markdown(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            md_text = file.read()
        html = markdown.markdown(md_text)
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text()
    except Exception as e:
        print(f"Error processing Markdown {file_path}: {str(e)}")
        return None

def extract_text_from_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error processing TXT {file_path}: {str(e)}")
        return None

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

    # Get all existing document IDs in the collection
    existing_ids = set(collection.get()["ids"])

    # Process each file in the directory
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        # Check if the file has already been imported
        if f"{filename}chunk0" in existing_ids:
            print(f"Skipping {filename} as it has already been imported.")
            continue

        print(f"Processing {filename}")

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

        # If text extraction failed, continue to the next file
        if text is None:
            continue

        print('Chunking text')

        # Chunk the text
        chunks = chunk_text(text)

        print('Inserting chunks into DB')

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