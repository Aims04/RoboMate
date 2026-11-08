import json
import os
import numpy as np
from fastembed import TextEmbedding
from typing import Optional, List

COLLEGE_FOLDER = "college"

class CollegeHandler:
    def __init__(self):
        print("Initializing semantic search engine with FastEmbed...")
        
        # FastEmbed uses ONNX by default - much faster!
        self.model = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        self.data = []
        self.embeddings = None
        self.load_all_data()
        self.create_embeddings()

    def load_all_data(self):
        """Load all JSON files from college folder."""
        for file in os.listdir(COLLEGE_FOLDER):
            if file.endswith(".json"):
                path = os.path.join(COLLEGE_FOLDER, file)
                with open(path, "r", encoding="utf-8") as f:
                    entries = json.load(f)
                    self.data.extend(entries)
        
        print(f" Loaded {len(self.data)} college data entries")

    def create_embeddings(self):
        """
        Create semantic embeddings for all entries.
        Enhanced version that gives more weight to keywords.
        """
        texts = []
        
        for entry in self.data:
            keywords_text = ' '.join(entry['keywords'])
            # Triple the keywords for more weight (same as your original!)
            combined_text = f"{entry['title']}. {keywords_text}. {keywords_text}. {entry['content']}"
            texts.append(combined_text)
        
        print("Creating semantic embeddings (one-time process, ~2-3 seconds)...")
        
        # FastEmbed returns generator, convert to numpy array
        embeddings_generator = self.model.embed(texts)
        self.embeddings = np.array(list(embeddings_generator))
        
        print(f" Semantic search ready! ({self.embeddings.shape[0]} embeddings)")

    def cosine_similarity(self, query_vec, doc_vecs):
        """Calculate cosine similarity between query and all documents."""
        # Normalize vectors
        query_norm = query_vec / np.linalg.norm(query_vec)
        doc_norms = doc_vecs / np.linalg.norm(doc_vecs, axis=1, keepdims=True)
        
        # Compute similarities
        similarities = np.dot(doc_norms, query_norm)
        return similarities

    def retrieve(self, query: str, threshold: float = 0.30) -> Optional[str]:
        """
        Retrieve most relevant college information using semantic similarity.
        
        Args:
            query: User's question in natural language
            threshold: Minimum similarity score (0-1)
        
        Returns:
            Content string if good match found, None otherwise
        """
        if not query or len(query.strip()) < 3:
            return None

        # Get query embedding
        query_embedding = list(self.model.embed([query]))[0]
        
        # Calculate similarities
        similarities = self.cosine_similarity(query_embedding, self.embeddings)
        
        best_idx = np.argmax(similarities)
        best_score = similarities[best_idx]
        
        matched_entry = self.data[best_idx]
        
        print(f" Query: '{query}'")
        print(f" Best match: '{matched_entry['title']}' (similarity: {best_score:.3f})")
        
        if best_score >= threshold:
            return matched_entry['content']
        
        print(f" No match above threshold ({threshold})")
        return None

    def get_suggestions(self, query: str, n: int = 3, min_score: float = 0.15) -> List[str]:
        """
        Get top N topic suggestions when query doesn't match well.
        
        Args:
            query: User's question
            n: Number of suggestions to return
            min_score: Minimum similarity to be considered a suggestion
        
        Returns:
            List of suggested topic titles
        """
        if not query or len(query.strip()) < 3:
            return []

        query_embedding = list(self.model.embed([query]))[0]
        similarities = self.cosine_similarity(query_embedding, self.embeddings)
        
        # Get top N indices
        top_indices = np.argsort(similarities)[::-1][:n]
        
        suggestions = []
        for idx in top_indices:
            score = similarities[idx]
            if score >= min_score:
                suggestions.append(self.data[idx]['title'])
        
        return suggestions

    def get_match_with_score(self, query: str, threshold: float = 0.30):
        """
        Return both content and match score for advanced handling.
        
        Returns:
            Tuple of (content, score, title) or (None, 0.0, None)
        """
        if not query or len(query.strip()) < 3:
            return None, 0.0, None

        query_embedding = list(self.model.embed([query]))[0]
        similarities = self.cosine_similarity(query_embedding, self.embeddings)
        
        best_idx = np.argmax(similarities)
        best_score = similarities[best_idx]
        matched_entry = self.data[best_idx]
        
        print(f" Query: '{query}'")
        print(f" Best match: '{matched_entry['title']}' (similarity: {best_score:.3f})")
        
        if best_score >= threshold:
            return matched_entry['content'], float(best_score), matched_entry['title']
        
        print(f" No match above threshold ({threshold})")
        return None, float(best_score), matched_entry['title']
