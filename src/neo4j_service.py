"""
Módulo Neo4j - Synapse
Gerencia a persistência em grafo das anotações
"""

from neo4j import GraphDatabase
from typing import Dict, List, Optional
from datetime import datetime
import os


class Neo4jService:
    """Serviço para gerenciar anotações no Neo4j"""
    
    def __init__(self, uri: str, user: str, password: str):
        """
        Inicializa conexão com Neo4j
        
        Args:
            uri: URI de conexão (ex: bolt://localhost:7687)
            user: Usuário do banco
            password: Senha do banco
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self._create_constraints()
    
    def _create_constraints(self):
        """Cria constraints e índices necessários"""
        with self.driver.session() as session:
            # Cria constraint de unicidade para o ID
            session.run("""
                CREATE CONSTRAINT note_id_unique IF NOT EXISTS
                FOR (n:Note) REQUIRE n.id IS UNIQUE
            """)
            
            # Cria índice para busca por título
            session.run("""
                CREATE INDEX note_title_index IF NOT EXISTS
                FOR (n:Note) ON (n.title)
            """)
    
    def create_note(self, note_id: str, title: str, content: str, 
                    tags: List[str] = None) -> Dict:
        """
        Cria uma nova anotação no grafo
        
        Args:
            note_id: ID único da anotação
            title: Título da anotação
            content: Conteúdo completo
            tags: Lista de tags (opcional)
            
        Returns:
            Dicionário com dados da anotação criada
        """
        with self.driver.session() as session:
            result = session.run("""
                CREATE (n:Note {
                    id: $note_id,
                    title: $title,
                    content: $content,
                    tags: $tags,
                    created_at: datetime(),
                    updated_at: datetime()
                })
                RETURN n
            """, note_id=note_id, title=title, content=content, 
               tags=tags or [])
            
            record = result.single()
            return self._node_to_dict(record['n'])
    
    def get_note(self, note_id: str) -> Optional[Dict]:
        """
        Recupera uma anotação por ID
        
        Args:
            note_id: ID da anotação
            
        Returns:
            Dicionário com dados da anotação ou None
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Note {id: $note_id})
                RETURN n
            """, note_id=note_id)
            
            record = result.single()
            if record:
                return self._node_to_dict(record['n'])
            return None
    
    def get_notes_by_ids(self, note_ids: List[str]) -> List[Dict]:
        """
        Recupera múltiplas anotações por IDs
        
        Args:
            note_ids: Lista de IDs
            
        Returns:
            Lista de anotações
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Note)
                WHERE n.id IN $note_ids
                RETURN n
            """, note_ids=note_ids)
            
            return [self._node_to_dict(record['n']) for record in result]
    
    def get_all_notes(self, limit: int = 100) -> List[Dict]:
        """
        Recupera todas as anotações
        
        Args:
            limit: Número máximo de resultados
            
        Returns:
            Lista de anotações
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Note)
                RETURN n
                ORDER BY n.created_at DESC
                LIMIT $limit
            """, limit=limit)
            
            return [self._node_to_dict(record['n']) for record in result]
    
    def create_relation(self, from_note_id: str, to_note_id: str, 
                       relation_type: str = "RELATED_TO") -> bool:
        """
        Cria relação entre duas anotações
        
        Args:
            from_note_id: ID da anotação de origem
            to_note_id: ID da anotação de destino
            relation_type: Tipo de relação
            
        Returns:
            True se sucesso
        """
        with self.driver.session() as session:
            session.run(f"""
                MATCH (a:Note {{id: $from_id}})
                MATCH (b:Note {{id: $to_id}})
                MERGE (a)-[r:{relation_type}]->(b)
                SET r.created_at = datetime()
            """, from_id=from_note_id, to_id=to_note_id)
            return True
    
    def delete_note(self, note_id: str) -> bool:
        """
        Deleta uma anotação e suas relações
        
        Args:
            note_id: ID da anotação
            
        Returns:
            True se sucesso
        """
        with self.driver.session() as session:
            session.run("""
                MATCH (n:Note {id: $note_id})
                DETACH DELETE n
            """, note_id=note_id)
            return True
    
    def get_related_notes(self, note_id: str) -> List[Dict]:
        """
        Busca anotações relacionadas
        
        Args:
            note_id: ID da anotação
            
        Returns:
            Lista de anotações relacionadas
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Note {id: $note_id})-[r]-(related:Note)
                RETURN related, type(r) as relation_type
            """, note_id=note_id)
            
            related = []
            for record in result:
                note = self._node_to_dict(record['related'])
                note['relation_type'] = record['relation_type']
                related.append(note)
            return related
    
    def _node_to_dict(self, node) -> Dict:
        """Converte nó do Neo4j para dicionário Python"""
        data = dict(node)
        # Converte datetime para string
        if 'created_at' in data:
            data['created_at'] = str(data['created_at'])
        if 'updated_at' in data:
            data['updated_at'] = str(data['updated_at'])
        return data
    
    def close(self):
        """Fecha conexão com o banco"""
        self.driver.close()


# Função helper para criar instância do serviço
def get_neo4j_service() -> Neo4jService:
    """Cria instância do serviço Neo4j usando variáveis de ambiente"""
    uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    user = os.getenv('NEO4J_USER', 'neo4j')
    password = os.getenv('NEO4J_PASSWORD', 'synapse123')
    
    return Neo4jService(uri, user, password)
