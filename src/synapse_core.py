"""
Módulo Principal - Synapse
Orquestra a interação entre Neo4j, ChromaDB e Embeddings
"""

from typing import List, Dict, Optional
import uuid
from .embeddings import get_embedding_service
from .neo4j_service import Neo4jService
from .chroma_service import ChromaDBService


class SynapseCore:
    """Classe principal que orquestra todas as operações do Synapse"""
    
    def __init__(self, neo4j_service: Neo4jService, chroma_service: ChromaDBService):
        """
        Inicializa o core do Synapse
        
        Args:
            neo4j_service: Instância do serviço Neo4j
            chroma_service: Instância do serviço ChromaDB
        """
        self.neo4j = neo4j_service
        self.chroma = chroma_service
        self.embeddings = get_embedding_service()
    
    def create_note(self, title: str, content: str, tags: List[str] = None) -> Dict:
        """
        Cria uma nova anotação no sistema
        
        Fluxo:
        1. Gera ID único
        2. Cria embedding do conteúdo
        3. Salva no Neo4j (grafo)
        4. Salva no ChromaDB (vetor)
        
        Args:
            title: Título da anotação
            content: Conteúdo textual
            tags: Tags para categorização
            
        Returns:
            Dicionário com dados da anotação criada
        """
        # Gera ID único
        note_id = str(uuid.uuid4())
        
        # Cria texto completo para embedding (título + conteúdo)
        full_text = f"{title}. {content}"
        
        # Gera embedding
        print("🔄 Gerando embedding...")
        embedding = self.embeddings.generate_embedding(full_text)
        
        # Salva no Neo4j
        print("🔄 Salvando no Neo4j...")
        note = self.neo4j.create_note(
            note_id=note_id,
            title=title,
            content=content,
            tags=tags
        )
        
        # Salva no ChromaDB
        print("🔄 Salvando no ChromaDB...")
        metadata = {
            "title": title,
            "tags": ",".join(tags) if tags else ""
        }
        self.chroma.add_note(note_id, embedding, metadata)
        
        print(f"✅ Anotação criada: {note_id}")
        return note
    
    def search_notes(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Busca anotações semanticamente similares à consulta
        
        Fluxo:
        1. Gera embedding da consulta
        2. Busca no ChromaDB os vetores mais similares
        3. Recupera dados completos do Neo4j
        4. Retorna resultados ordenados por relevância
        
        Args:
            query: Texto da consulta
            top_k: Número de resultados
            
        Returns:
            Lista de anotações com score de similaridade
        """
        print(f"🔍 Buscando por: '{query}'")
        
        # Gera embedding da consulta
        query_embedding = self.embeddings.generate_embedding(query)
        
        # Busca no ChromaDB
        note_ids, similarities = self.chroma.search(query_embedding, n_results=top_k)
        
        if not note_ids:
            print("❌ Nenhum resultado encontrado")
            return []
        
        # Recupera dados completos do Neo4j
        notes = self.neo4j.get_notes_by_ids(note_ids)
        
        # Adiciona score de similaridade e ordena
        results = []
        for note, similarity in zip(notes, similarities):
            note['similarity_score'] = similarity
            note['similarity_percentage'] = f"{similarity * 100:.1f}%"
            results.append(note)
        
        print(f"✅ Encontradas {len(results)} anotações")
        return results
    
    def get_note(self, note_id: str) -> Optional[Dict]:
        """
        Recupera uma anotação específica
        
        Args:
            note_id: ID da anotação
            
        Returns:
            Dados da anotação ou None
        """
        return self.neo4j.get_note(note_id)
    
    def get_all_notes(self, limit: int = 100) -> List[Dict]:
        """
        Lista todas as anotações
        
        Args:
            limit: Número máximo de resultados
            
        Returns:
            Lista de anotações
        """
        return self.neo4j.get_all_notes(limit)
    
    def delete_note(self, note_id: str) -> bool:
        """
        Deleta uma anotação de ambos os bancos
        
        Args:
            note_id: ID da anotação
            
        Returns:
            True se sucesso
        """
        print(f"🗑️  Deletando anotação: {note_id}")
        
        # Deleta do Neo4j
        self.neo4j.delete_note(note_id)
        
        # Deleta do ChromaDB
        self.chroma.delete_note(note_id)
        
        print("✅ Anotação deletada")
        return True
    
    def create_relation(self, from_note_id: str, to_note_id: str) -> bool:
        """
        Cria relação entre duas anotações
        
        Args:
            from_note_id: ID da anotação de origem
            to_note_id: ID da anotação relacionada
            
        Returns:
            True se sucesso
        """
        return self.neo4j.create_relation(from_note_id, to_note_id)
    
    def get_related_notes(self, note_id: str) -> List[Dict]:
        """
        Busca anotações relacionadas no grafo
        
        Args:
            note_id: ID da anotação
            
        Returns:
            Lista de anotações relacionadas
        """
        return self.neo4j.get_related_notes(note_id)
    
    def get_stats(self) -> Dict:
        """
        Retorna estatísticas do sistema
        
        Returns:
            Dicionário com estatísticas
        """
        return {
            "total_notes_neo4j": len(self.neo4j.get_all_notes(limit=10000)),
            "total_notes_chroma": self.chroma.get_count(),
            "embedding_model": "paraphrase-multilingual-mpnet-base-v2"
        }
