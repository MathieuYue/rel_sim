import json
import numpy as np
import utils.llm_utils as llm_utils

def cosine_similarity(a, b):
        a = np.array(a)
        b = np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)

class Memory():
    def __init__(self, memory_path = None) -> None:
        self.memory_store = {}  # key: memory, value: embedding (list of floats)
        self.working_memory = []
        
        if memory_path is not None:
            with open(memory_path, "r", encoding="utf-8") as f:
                self.memory_store = json.load(f)

    def add_to_working_memory(self, text: str, emotion_embedding: list = None, inner_thoughts: str = None, memory_type: str = None, agent: str = None):
        """
        Store a memory (text), optional emotion_embedding, optional inner_thoughts, optional type, and optional agent to the working memory.
        """
        self.working_memory.append({
            "text": text,
            "emotion_embedding": emotion_embedding,
            "inner_thoughts": inner_thoughts,
            "type": memory_type,
            "agent": agent
        })

    def format_working_memory(self):
        """
        Returns the working memory as a single structured string for LLM input,
        omitting the emotion_embedding.
        Includes type and agent if they are not None.
        """
        formatted = []
        for i, mem in enumerate(self.working_memory, 1):
            entry = f"Event {i}:\n"
            entry += f"  Event: {mem.get('text', '')}\n"
            if mem.get('inner_thoughts'):
                entry += f"  Inner Thoughts: {mem['inner_thoughts']}\n"
            if mem.get('type') is not None:
                entry += f"  Type: {mem['type']}\n"
            if mem.get('agent') is not None:
                entry += f"  Agent: {mem['agent']}\n"
            formatted.append(entry.strip())
        return "\n\n".join(formatted)

    
    def store_working_memory_to_memory_store(self):
        """
        Store all entries in working_memory that have an emotion_embedding into the memory_store.
        Uses the text as the key and stores semantic_embedding, emotion_embedding, inner_thoughts, type, and agent.
        """
        for mem in self.working_memory:
            text = mem.get("text")
            emotion_embedding = mem.get("emotion_embedding")
            if text is not None and emotion_embedding is not None:
                semantic_embedding = llm_utils.get_text_embedding(text)
                self.memory_store[text] = {
                    "semantic_embedding": semantic_embedding,
                    "emotion_embedding": emotion_embedding,
                    "inner_thoughts": mem.get("inner_thoughts"),
                    "type": mem.get("type"),
                    "agent": mem.get("agent")
                }

    # joy, acceptance, fear, surprise, sadness, disgust, anger, and anticipation

    def load_memory_store(self, memory_path):
        """
        Load the memory store from a JSON file.
        """
        with open(memory_path, "r", encoding="utf-8") as f:
            self.memory_store = json.load(f)

    def save_memory_store(self, memory_path):
        """
        Save the current memory store to a JSON file.
        """
        with open(memory_path, "w", encoding="utf-8") as f:
            json.dump(self.memory_store, f, ensure_ascii=False, indent=2)

    def add_memory(self, text: str, emotion_embedding: list, inner_thoughts: str = None, memory_type: str = None, agent: str = None):
        semantic_embedding = llm_utils.get_text_embedding(text)
        self.memory_store[text] = {
            "semantic_embedding": semantic_embedding,
            "emotion_embedding": emotion_embedding,
            "inner_thoughts": inner_thoughts,
            "type": memory_type,
            "agent": agent
        }

    def get_top_memories(self, query_embedding, query_emotion_embedding=None, top_k=5, alpha=0.7):
        """
        Retrieve top_k memories based on a weighted combination of semantic and emotion similarity.
        alpha: weight for semantic similarity (0 <= alpha <= 1)
        query_emotion_embedding: 8-dim Plutchik vector for the query (required for emotion similarity)
        """
        similarities = []
        for text, data in self.memory_store.items():
            semantic_embedding = data.get("semantic_embedding", None)
            emotion_embedding = data.get("emotion_embedding", None)
            inner_thoughts = data.get("inner_thoughts", None)
            if semantic_embedding is not None and emotion_embedding is not None and query_emotion_embedding is not None:
                # Semantic similarity (cosine)
                semantic_sim = cosine_similarity(query_embedding, semantic_embedding)
                # Emotion similarity (1 - cosine distance)
                emotion_sim = 1 - cosine_similarity(query_emotion_embedding, emotion_embedding)
                # Combine
                final_score = alpha * semantic_sim + (1 - alpha) * emotion_sim
                similarities.append((final_score, text, inner_thoughts))
            elif semantic_embedding is not None:
                # Fallback: only semantic similarity
                semantic_sim = cosine_similarity(query_embedding, semantic_embedding)
                similarities.append((semantic_sim, text, inner_thoughts))
        # Sort by score descending
        similarities.sort(reverse=True)

        # returns tuple of (memory, inner_thoughts)
        return [(text, inner_thoughts) for _, text, inner_thoughts in similarities[:top_k]]

    def get_top_memories_from_text(self, query_text, query_emotion_embedding=None, top_k=5, alpha=0.7):
        """
        Given a query string, compute its embedding and return the top_k most similar memories,
        using the new get_top_memories method which supports emotion similarity.
        """
        query_embedding = llm_utils.get_text_embedding(query_text)
        return self.get_top_memories(
            query_embedding,
            query_emotion_embedding=query_emotion_embedding,
            top_k=top_k,
            alpha=alpha
        )

    
