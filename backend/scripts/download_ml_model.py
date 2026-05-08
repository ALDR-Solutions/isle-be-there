#!/usr/bin/env python3
"""Pre-download ML model for sentence-transformers.

Run this script once before deploying to cache the model locally:
    python backend/scripts/download_ml_model.py
"""

from sentence_transformers import SentenceTransformer

if __name__ == "__main__":
    print("Downloading all-MiniLM-L6-v2 model...")
    print("This may take a few minutes depending on your connection.")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("Model downloaded and cached successfully!")
    print(f"Cache location: {model.tokenizer.name_or_path}")
