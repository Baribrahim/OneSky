"""
Embedding Helper
Utilities for generating and comparing embeddings using OpenAI
"""
import json
import numpy as np
from openai import OpenAI
import os


class EmbeddingHelper:
    """Helper class for generating and comparing embeddings"""
    
    def __init__(self, api_key):
        """Initialize with OpenAI API key"""
        if not api_key:
            raise ValueError("API key is required for embeddings")
        self.client = OpenAI(api_key=api_key)
        self.model = "text-embedding-3-small" 
    
    def generate_embedding(self, text):
        """
        Generate embedding for a single text string
        
        Args:
            text (str): Text to embed
            
        Returns:
            list: Embedding vector (list of floats)
        """
        if not text or not text.strip():
            return None
            
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text.strip()
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def cosine_similarity(self, vec1, vec2):
        """
        Calculate cosine similarity between two embedding vectors
        
        Args:
            vec1 (list): First embedding vector
            vec2 (list): Second embedding vector
            
        Returns:
            float: Cosine similarity score (0-1, higher = more similar)
        """
        if not vec1 or not vec2:
            return 0.0
            
        vec1_array = np.array(vec1)
        vec2_array = np.array(vec2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1_array, vec2_array)
        norm1 = np.linalg.norm(vec1_array)
        norm2 = np.linalg.norm(vec2_array)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)
    
    def embedding_to_json(self, embedding):
        """Convert embedding list to JSON string for database storage"""
        if not embedding:
            return None
        return json.dumps(embedding)
    
    def json_to_embedding(self, json_str):
        """Convert JSON string from database back to embedding list"""
        if not json_str:
            return None
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            return None
