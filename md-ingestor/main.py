import re
import glob
import os
import hashlib
import logging

from chromadb import HttpClient as ChromaHttpClient
from chromadb.utils.embedding_functions.ollama_embedding_function import OllamaEmbeddingFunction

from pathlib import Path
from typing import Any

MD_REPO = os.getenv("MD_REPO", "../mount/md")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434") # http://ollama:11434
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "mxbai-embed-large")
CHROMA_HOST = os.getenv("CHROMA_HOST", "http://localhost:8000") # http://chroma:8000

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_collection(collection_name: str) -> list:
    chroma_host, chroma_port = CHROMA_HOST.replace("http://", "").split(':', 1)
    chroma_client = ChromaHttpClient(
        host=chroma_host,
        port=chroma_port,
        ssl=False
    )
    chroma_client.heartbeat()

    embedding_function = OllamaEmbeddingFunction(
        url=OLLAMA_HOST,
        model_name=OLLAMA_EMBED_MODEL
    )
    logger.debug(f"Creating collection {collection_name}")
    return chroma_client.create_collection(name=collection_name, embedding_function=embedding_function)

def hash_string_utf8(string: str) -> str:
    hasher = hashlib.sha256()
    hasher.update(string.encode('utf-8'))
    return hasher.hexdigest()

def iterate_and_read(path: str) -> Any:
    for file_path in glob.iglob(path, recursive=True):
        with open(file_path, "r") as f:
            yield file_path, f.read()

def chunk_hierarchical_text(document: str, max_tokens: int = 1800) -> Any:
    # Original implementation: https://danielkliewer.com/blog/2025-03-28-ollama-chunking

    # First level: Split by major section headers
    sections = re.split(r'# [A-Za-z\s]+\n', document)
    
    # Second level: For each section, split by sub-headers
    subsections = []
    for section in sections:
        if not section.strip():
            continue
        subsecs = re.split(r'## [A-Za-z\s]+\n', section)
        subsections.extend([s for s in subsecs if s.strip()])
    
    # Final level: Split subsections into token-sized chunks
    n = 0
    for subsection in subsections:
        words = subsection.split()
        logger.debug(f"Number of words: {len(words)}")
        for i in range(0, len(words), max_tokens):
            chunk = ' '.join(words[i:i + max_tokens])
            if chunk.strip():
                yield n, chunk
                n += 1

def main():
    notes_collection = create_collection("notes")

    logger.info(f"Iterating through {MD_REPO}")
    
    n_files = 0
    for file_path, file_content in iterate_and_read(f"{MD_REPO}/**/*.md"):
        logging.debug(f"Processing {file_path}")

        path_hex = hash_string_utf8(file_path) # create a unique hash for specific file
        
        data = [[], [], []]
        for i, chunk in chunk_hierarchical_text(file_content):
            identifier = f"{path_hex}-{i}"

            data[0].append(identifier)
            data[1].append(chunk)
            data[2].append({ "source": file_path, "revision": i, "title": Path(file_path).stem })

        notes_collection.add(
            documents=data[1],
            metadatas=data[2],
            ids=data[0],
        )

        n_files += 1
    
    logger.info(f"Proccessed {n_files} files")


if __name__ == "__main__":
    main()
