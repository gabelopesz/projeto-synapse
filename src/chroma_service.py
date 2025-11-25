"""
Módulo ChromaDB - Synapse
Gerencia o armazenamento vetorial para busca semântica
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Tuple
import os


class ChromaDBService:
    """Serviço para gerenciar embeddings no ChromaDB"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Inicializa conexão com ChromaDB
        
        Args:
            persist_directory: Diretório para persistência dos dados
        """
        self.persist_directory = persist_directory
        
        # Cria diretório se não existir
        os.makedirs(persist_directory, exist_ok=True)
        
        # Inicializa cliente ChromaDB
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Cria ou recupera coleção com distância de cosseno
        self.collection = self.client.get_or_create_collection(
            name="synapse_notes",
            metadata={"description": "Anotações de estudo do Synapse",
                     "hnsw:space": "cosine"}  # Usa similaridade de cosseno
        )
    
    def add_note(self, note_id: str, embedding: List[float], 
                 metadata: Dict = None) -> bool:
        """
        Adiciona uma anotação ao banco vetorial
        
        Args:
            note_id: ID único da anotação
            embedding: Vetor representando o conteúdo
            metadata: Metadados adicionais (título, tags, etc)
            
        Returns:
            True se sucesso
        """
        try:
            self.collection.add(
                ids=[note_id],
                embeddings=[embedding],
                metadatas=[metadata or {}]
            )
            return True
        except Exception as e:
            print(f"❌ Erro ao adicionar no ChromaDB: {e}")
            return False
    
    def search(self, query_embedding: List[float], 
               n_results: int = 5) -> Tuple[List[str], List[float]]:
        """
        Busca anotações similares ao vetor de consulta
        
        Args:
            query_embedding: Vetor da consulta
            n_results: Número de resultados a retornar
            
        Returns:
            Tupla com (lista de IDs, lista de scores de similaridade)
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Extrai IDs e distâncias
        ids = results['ids'][0] if results['ids'] else []
        distances = results['distances'][0] if results['distances'] else []
        
        # Com similaridade de cosseno, a distância varia de 0 (idêntico) a 2 (oposto)
        # Converte para score de 0 a 1
        similarities = []
        for dist in distances:
            # Cosseno: 0 = idêntico, 2 = oposto
            # Converte para: 1 = idêntico, 0 = oposto
            similarity = max(0.0, min(1.0, 1.0 - (dist / 2.0)))
            similarities.append(similarity)
        
        return ids, similarities
    
    def delete_note(self, note_id: str) -> bool:
        """
        Remove uma anotação do banco vetorial
        
        Args:
            note_id: ID da anotação
            
        Returns:
            True se sucesso
        """
        try:
            self.collection.delete(ids=[note_id])
            return True
        except Exception as e:
            print(f"❌ Erro ao deletar do ChromaDB: {e}")
            return False
    
    def get_count(self) -> int:
        """
        Retorna número total de anotações armazenadas
        
        Returns:
            Número de documentos
        """
        return self.collection.count()
    
    def clear_all(self) -> bool:
        """
        Remove todas as anotações (usar com cuidado!)
        
        Returns:
            True se sucesso
        """
        try:
            # Deleta a coleção e recria
            self.client.delete_collection("synapse_notes")
            self.collection = self.client.get_or_create_collection(
                name="synapse_notes",
                metadata={"description": "Anotações de estudo do Synapse"}
            )
            return True
        except Exception as e:
            print(f"❌ Erro ao limpar ChromaDB: {e}")
            return False


# Função helper para criar instância do serviço
def get_chroma_service() -> ChromaDBService:
    """Cria instância do serviço ChromaDB usando variáveis de ambiente"""
    persist_dir = os.getenv('CHROMA_PERSIST_DIR', './chroma_db')
    return ChromaDBService(persist_directory=persist_dir)
