"""
Módulo de Embeddings - Synapse
Responsável por converter texto em vetores usando Sentence Transformers
"""

from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np


class EmbeddingService:
    """Serviço para geração de embeddings de texto"""
    
    def __init__(self, model_name: str = 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'):
        """
        Inicializa o serviço de embeddings
        
        Args:
            model_name: Nome do modelo pré-treinado a ser usado
                       (paraphrase-multilingual-mpnet-base-v2 suporta português)
        """
        print(f"🔄 Carregando modelo de embeddings: {model_name}")
        self.model = SentenceTransformer(model_name)
        print("✅ Modelo carregado com sucesso!")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Gera embedding para um único texto
        
        Args:
            text: Texto a ser convertido em vetor
            
        Returns:
            Lista de floats representando o vetor do texto
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Gera embeddings para múltiplos textos (mais eficiente)
        
        Args:
            texts: Lista de textos
            
        Returns:
            Lista de vetores
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calcula similaridade de cosseno entre dois vetores
        
        Args:
            embedding1: Primeiro vetor
            embedding2: Segundo vetor
            
        Returns:
            Score de similaridade (0 a 1)
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Similaridade de cosseno
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return float(similarity)


# Singleton para reuso do modelo
_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    """Retorna instância singleton do serviço de embeddings"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
