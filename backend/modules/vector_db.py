import chromadb
from chromadb.config import Settings
from typing import Dict, List, Optional, Any, Union
import numpy as np
from .config import VECTOR_DB_DIR

class VectorDB:
    def __init__(self):
        """Inicializa conexão com ChromaDB"""
        self.client = chromadb.PersistentClient(
            path=str(VECTOR_DB_DIR),
            settings=Settings(
                anonymized_telemetry=False
            )
        )
    
    def _normalize_embedding_to_float32(self, embedding: Union[np.ndarray, List[float]]) -> List[float]:
        """
        Garante que embedding é uma lista de float32
        
        Esta função previne problemas de precisão e busca no ChromaDB,
        garantindo que embeddings sejam consistentemente float32.
        
        Args:
            embedding: Embedding como np.ndarray ou list
        
        Returns:
            List[float]: Embedding normalizado para float32
        """
        if isinstance(embedding, np.ndarray):
            # Converte numpy array para float32 e depois para lista
            return embedding.astype(np.float32).tolist()
        else:
            # Já é lista, mas garante que valores são float
            return [float(x) for x in embedding]
        
    def create_collection(self, name: str, metadata: Optional[Dict] = None) -> Any:
        """
        Cria uma nova coleção
        
        Args:
            name: Nome da coleção
            metadata: Metadados da coleção (opcional)
        """
        return self.client.create_collection(
            name=name,
            metadata=metadata or {"hnsw:space": "cosine"}
        )
    
    def get_collection(self, name: str) -> Any:
        """Obtém uma coleção existente"""
        return self.client.get_collection(name)
    
    def get_or_create_collection(self, name: str, metadata: Optional[Dict] = None) -> Any:
        """Obtém ou cria uma coleção"""
        try:
            return self.get_collection(name)
        except:
            return self.create_collection(name, metadata)
    
    def delete_collection(self, name: str) -> None:
        """Deleta uma coleção"""
        self.client.delete_collection(name)
    
    def list_collections(self) -> List[str]:
        """Lista todas as coleções existentes"""
        return [col.name for col in self.client.list_collections()]
    
    def add_items(
        self,
        collection_name: str,
        embeddings: List[Union[List[float], np.ndarray]],
        ids: List[str],
        metadatas: Optional[List[Dict]] = None

    ) -> None:
        """
        Adiciona itens a uma coleção
        
        Args:
            collection_name: Nome da coleção
            embeddings: Lista de embeddings (aceita np.ndarray ou list)
            ids: Lista de IDs únicos
            metadatas: Lista de metadados (opcional)
        """
        # Normaliza todos embeddings para float32
        normalized_embeddings = [
            self._normalize_embedding_to_float32(emb) for emb in embeddings
        ]
        
        collection = self.get_collection(collection_name)
        collection.add(
            embeddings=normalized_embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
    def add_item(
        self,
        collection_name: str,
        embedding: Union[List[float], np.ndarray],
        id: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Adiciona um único item a uma coleção
        
        Args:
            collection_name: Nome da coleção
            embedding: Embedding (aceita np.ndarray ou list)
            id: ID único do item
            metadata: Metadados do item (opcional)
        """
        # Normaliza embedding para float32
        normalized_embedding = self._normalize_embedding_to_float32(embedding)
        
        collection = self.get_collection(collection_name)
        collection.upsert(
            embeddings=normalized_embedding,
            metadatas=metadata,
            ids=id
        )
    
    def search_similar(
        self,
        collection_name: str,
        query_embedding: Union[List[float], np.ndarray],
        n_results: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> Dict:
        """
        Busca itens similares em uma coleção
        
        Args:
            collection_name: Nome da coleção
            query_embedding: Embedding de consulta (aceita np.ndarray ou list)
            n_results: Número de resultados
            filter_dict: Filtros a aplicar
        """
        # Normaliza query embedding para float32
        normalized_query = self._normalize_embedding_to_float32(query_embedding)
        
        collection = self.get_collection(collection_name)
        return collection.query(
            query_embeddings=[normalized_query],
            n_results=n_results,
            where=filter_dict or None
        )
    
    def get_by_id(self, collection_name: str, key: str):
        """
        Fetch an item by its key (id) from the given collection.
        Returns the embedding, metadata, and id if found.
        """
        collection = self.get_collection(collection_name)
        res = collection.get(ids=[key], include=["embeddings"])
        if not res["ids"]:
            return None
        return {
            "id": res["ids"][0],
            "embedding": res["embeddings"][0],
        }
    
    def delete_items(self, collection_name: str, ids: List[str]) -> None:
        """Deleta itens de uma coleção por IDs"""
        collection = self.get_collection(collection_name)
        collection.delete(ids=ids)

    def get_pieces_by_outfit(self, collection_name: str, outfit_id: str) -> List[Dict]:
        """
        Obtém todas as peças de um outfit específico
        
        Args:
            collection_name: Nome da coleção
            outfit_id: ID do outfit
            
        Returns:
            Lista de dicionários com informações das peças
        """
        collection = self.get_collection(collection_name)
        # Busca apenas IDs que começam com o outfit_id específico
        # IDs têm formato: "outfit_id/piece_name.jpg"
        results = collection.get(include=['embeddings'])
        
        pieces = []
        for doc_id, embedding in zip(results['ids'], results['embeddings']):
            if doc_id.startswith(f"{outfit_id}/"):
                piece_name = doc_id.split('/')[1]
                pieces.append({
                    'piece_id': doc_id,
                    'piece_name': piece_name,
                    'embedding': embedding,
                    'outfit_id': outfit_id
                })
        
        return pieces
    
    def get_pieces_by_outfits_batch(self, collection_name: str, outfit_ids: List[str]) -> Dict[str, List[Dict]]:
        """
        Obtém todas as peças de múltiplos outfits em uma única query (OTIMIZADO)
        
        Args:
            collection_name: Nome da coleção
            outfit_ids: Lista de IDs dos outfits
            
        Returns:
            Dicionário mapeando outfit_id -> lista de peças
        """
        collection = self.get_collection(collection_name)
        
        # TODO: Filtros nativos ChromaDB quando metadata disponível
        # Atualmente, a collection não possui metadata (apenas IDs no formato "outfit_id/piece_name")
        # Para usar filtros nativos, seria necessário:
        #   results = collection.get(where={"outfit_id": {"$in": outfit_ids}}, include=['embeddings'])
        # Isso requer repopulação do ChromaDB com metadata estruturada.

        # Primeiro, busca só os IDs (sem embeddings) para descobrir quais existem
        all_ids = collection.get(limit=None)['ids']  # Get all IDs only (fast)
        

        outfit_ids_set = set(outfit_ids)
        relevant_ids = []
        
        for doc_id in all_ids:
            parts = doc_id.split('/')
            if len(parts) >= 2 and parts[0] in outfit_ids_set:
                relevant_ids.append(doc_id)
        
        if not relevant_ids:
            return {outfit_id: [] for outfit_id in outfit_ids}
        
        results = collection.get(ids=relevant_ids, include=['embeddings'])
        
        outfits_dict = {outfit_id: [] for outfit_id in outfit_ids}
        
        for doc_id, embedding in zip(results['ids'], results['embeddings']):
            parts = doc_id.split('/')
            outfit_id = parts[0]
            piece_name = parts[1]
            outfits_dict[outfit_id].append({
                'piece_id': doc_id,
                'piece_name': piece_name,
                'embedding': embedding,
                'outfit_id': outfit_id
            })
        
        return outfits_dict
    
    def search_similar_filtered(
        self,
        collection_name: str,
        query_embedding: List[float],
        n_results: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> Dict:
        """
        Busca itens similares em uma coleção, ignorando distâncias negativas
        """
        collection = self.get_collection(collection_name)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results * 2,  # Busca mais para compensar filtros
            where=filter_dict or None
        )
        
        # Filtrar resultados com distâncias negativas
        filtered_ids = []
        filtered_distances = []
        for i, dist in enumerate(results['distances'][0]):
            if dist >= 0:  # Ignora distâncias negativas
                filtered_ids.append(results['ids'][0][i])
                filtered_distances.append(dist)
                if len(filtered_ids) >= n_results:
                    break
        
        return {
            'ids': [filtered_ids],
            'distances': [filtered_distances],
            'metadatas': [results['metadatas'][0][:len(filtered_ids)]] if results.get('metadatas') else None,
            'documents': [results['documents'][0][:len(filtered_ids)]] if results.get('documents') else None
        }