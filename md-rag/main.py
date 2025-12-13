import re
import glob
import os
import hashlib
import logging

from pathlib import Path
from typing import Any

MD_REPO = os.getenv("MD_REPO", "../mount/md")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        for i in range(0, len(words), max_tokens):
            chunk = ' '.join(words[i:i + max_tokens])
            if chunk.strip():
                yield n, chunk
                n += 1

def main():
    logger.info(f"Iterating through {MD_REPO}")
    
    n_files = 0
    for file_path, file_content in iterate_and_read(f"{MD_REPO}/**/*.md"):
        logging.info(f"Processing {file_path}")

        path_hex = hash_string_utf8(file_path) # create a unique hash for specific file
        
        data = [[], [], []]
        for i, chunk in chunk_hierarchical_text(file_content):
            identifier = f"{path_hex}-{i}"

            data[0].append(identifier)
            data[1].append(chunk)
            data[2].append({ "source": file_path, "revision": i, "title": Path(file_path).stem })

        n_files += 1
    
    logger.info(f"Proccessed {n_files} files")


if __name__ == "__main__":
    main()
