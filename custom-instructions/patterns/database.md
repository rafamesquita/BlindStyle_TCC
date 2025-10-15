description: MUST BE APPLIED WHEN working on database code including ChromaDB operations, embeddings storage, vector search, and data access patterns.
applyTo: "**/vector_db.py,**/embeddings.py,**/chroma_db/**/*,**/database/**/*"
alwaysApply: false

# Database Development Guidelines: Blind Style Model

## Database Philosophy

**Database**: ChromaDB 1.1.1 (Vector Database)
**Storage**: Local persistent storage (`chroma_db/`)
**Query Method**: Cosine similarity search (HNSW index)

### Core Principles
- **Persistência Local**: Dados armazenados em disco local (sem cloud)
- **Reprodutibilidade**: Embeddings determinísticos garantem consistência
- **Performance**: Busca vetorial eficiente com índice HNSW
- **Simplicidade**: Interface limpa e direta
- **Escalabilidade**: Suporta milhares de embeddings

## ChromaDB Architecture

### Collections Design
```python
# Estrutura de coleção "pieces"
{
    "name": "pieces",
    "metadata": {"hnsw:space": "cosine"},  # Cosine similarity
    "embeddings": List[List[float]],       # Vetores 96D
    "ids": List[str],                      # "outfit_id/piece_id.jpg"
    "metadatas": Optional[List[Dict]]      # Atributos da peça
}
```

### ID Convention
```python
# Formato padrão de IDs
id = f"{outfit_id}/{piece_id}.jpg"

# Exemplos:
# "193875024/1.jpg"
# "158304930/3.jpg"
# "210443298/5.jpg"
```

## Vector Database Operations

### Connection Management
```python
from pathlib import Path
import chromadb
from chromadb.config import Settings

class VectorDB:
    def __init__(self):
        """Inicializa conexão persistente com ChromaDB"""
        self.client = chromadb.PersistentClient(
            path=str(VECTOR_DB_DIR),  # Local disk storage
            settings=Settings(
                anonymized_telemetry=False  # Privacy
            )
        )
```

### Collection Management
```python
def get_or_create_collection(self, name: str, metadata: Optional[Dict] = None) -> Any:
    """Obtém ou cria coleção (idempotente)"""
    try:
        return self.get_collection(name)
    except:
        return self.create_collection(name, metadata)

def create_collection(self, name: str, metadata: Optional[Dict] = None) -> Any:
    """Cria nova coleção com metadados"""
    return self.client.create_collection(
        name=name,
        metadata=metadata or {"hnsw:space": "cosine"}
    )

def delete_collection(self, name: str) -> None:
    """Deleta coleção (uso cuidadoso)"""
    self.client.delete_collection(name)

def list_collections(self) -> List[str]:
    """Lista todas as coleções existentes"""
    return [col.name for col in self.client.list_collections()]
```

## Embedding Storage

### Batch Insert (Preferred)
```python
def add_items(
    self,
    collection_name: str,
    embeddings: List[List[float]],
    ids: List[str],
    metadatas: Optional[List[Dict]] = None
) -> None:
    """Adiciona múltiplos embeddings em batch (eficiente)"""
    collection = self.get_collection(collection_name)
    collection.add(
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

# Usage
embeddings = [[0.1, 0.2, ...], [0.3, 0.4, ...]]
ids = ["outfit1/1.jpg", "outfit1/2.jpg"]
metadatas = [
    {"category": "tops", "color": "blue"},
    {"category": "bottoms", "color": "black"}
]

vector_db.add_items("pieces", embeddings, ids, metadatas)
```

### Single Insert (Upsert)
```python
def add_item(
    self,
    collection_name: str,
    embedding: List[float],
    id: str,
    metadata: Optional[Dict] = None
) -> None:
    """Adiciona/atualiza um embedding (upsert)"""
    collection = self.get_collection(collection_name)
    collection.upsert(
        embeddings=[embedding],
        metadatas=[metadata] if metadata else None,
        ids=[id]
    )
```

## Vector Search

### Similarity Search
```python
def search_similar(
    self,
    collection_name: str,
    query_embedding: List[float],
    n_results: int = 5,
    filter: Optional[Dict] = None
) -> List[Dict[str, Any]]:
    """Busca top-k embeddings similares
    
    Args:
        collection_name: Nome da coleção
        query_embedding: Vetor de consulta (96D)
        n_results: Número de resultados (default: 5)
        filter: Filtros de metadata (opcional)
    
    Returns:
        Lista de resultados com IDs, distâncias e metadatas
    """
    collection = self.get_collection(collection_name)
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=filter  # Ex: {"category": "tops"}
    )
    
    # Formatar resultados
    formatted_results = []
    for i in range(len(results['ids'][0])):
        formatted_results.append({
            'id': results['ids'][0][i],
            'distance': results['distances'][0][i],
            'metadata': results['metadatas'][0][i] if results['metadatas'] else None
        })
    
    return formatted_results
```

### Search with Filters
```python
# Buscar apenas tops azuis
results = vector_db.search_similar(
    collection_name="pieces",
    query_embedding=query_emb,
    n_results=10,
    filter={"category": "tops", "primary_color": "blue"}
)
```

### Retrieve by ID
```python
def get_by_id(self, collection_name: str, id: str) -> Optional[Dict]:
    """Recupera embedding por ID exato"""
    collection = self.get_collection(collection_name)
    
    try:
        result = collection.get(ids=[id], include=["embeddings", "metadatas"])
        
        if not result['ids']:
            return None
        
        return {
            'id': result['ids'][0],
            'embedding': result['embeddings'][0],
            'metadata': result['metadatas'][0] if result['metadatas'] else None
        }
    except Exception as e:
        logging.error(f"Erro ao buscar ID {id}: {e}")
        return None
```

## Data Modeling

### Embedding Structure
```python
# Embedding de uma peça: 96 dimensões
# 6 atributos × 16 dimensões cada
embedding_structure = {
    "category": 16,        # dims 0-15
    "item_type": 16,       # dims 16-31
    "primary_color": 16,   # dims 32-47
    "usage": 16,           # dims 48-63
    "texture": 16,         # dims 64-79
    "print_category": 16   # dims 80-95
}

# Total: 96 dimensions
# Normalized: L2 norm = 1.0
```

### Metadata Schema
```python
metadata_schema = {
    "category": str,        # "tops", "bottoms", "shoes", "others"
    "item_type": str,       # "tshirt", "jeans", "sneakers", etc.
    "primary_color": str,   # "blue", "black", "white", etc.
    "usage": str,           # "casual", "formal", etc.
    "texture": str,         # "cotton", "denim", "leather", etc.
    "print_category": str   # "plain", "striped", "graphic", etc.
}
```

## Query Optimization

### Indexing Strategy
ChromaDB usa **HNSW (Hierarchical Navigable Small World)** index automaticamente:
- ✅ Busca aproximada eficiente (O(log n))
- ✅ Alta precisão (recall > 95%)
- ✅ Escalável (milhares de vetores)

### Performance Best Practices
```python
# ✅ DO: Batch inserts
embeddings = [emb1, emb2, emb3, ...]
vector_db.add_items("pieces", embeddings, ids)

# ❌ DON'T: Loop de inserts individuais
for emb, id in zip(embeddings, ids):
    vector_db.add_item("pieces", emb, id)  # Lento

# ✅ DO: Filtrar antes de buscar
results = vector_db.search_similar(
    "pieces",
    query_emb,
    n_results=50,
    filter={"category": "tops"}  # Reduz espaço de busca
)

# ✅ DO: Limitar n_results
results = vector_db.search_similar("pieces", query_emb, n_results=10)  # Suficiente
```

### Pagination (Future)
```python
def search_with_pagination(
    self,
    collection_name: str,
    query_embedding: List[float],
    page: int = 1,
    page_size: int = 20
) -> Dict:
    """Busca com paginação (a implementar)"""
    offset = (page - 1) * page_size
    
    # ChromaDB não tem paginação nativa, implementar lógica
    all_results = self.search_similar(
        collection_name,
        query_embedding,
        n_results=page * page_size
    )
    
    paginated = all_results[offset:offset + page_size]
    
    return {
        "results": paginated,
        "page": page,
        "total": len(all_results),
        "has_next": len(all_results) > (offset + page_size)
    }
```

## Data Lifecycle Management

### Soft Deletes (Future)
```python
# Estratégia futura para soft deletes
def soft_delete(self, collection_name: str, id: str):
    """Marca item como deletado sem remover"""
    metadata = self.get_by_id(collection_name, id)['metadata']
    metadata['deleted'] = True
    metadata['deleted_at'] = datetime.now().isoformat()
    
    # Update metadata
    self.add_item(collection_name, embedding, id, metadata)
```

### Collection Backup
```python
def backup_collection(self, collection_name: str, backup_path: Path):
    """Faz backup de uma coleção"""
    collection = self.get_collection(collection_name)
    
    # Get all data
    all_data = collection.get(include=["embeddings", "metadatas"])
    
    # Save to disk
    backup_data = {
        "name": collection_name,
        "ids": all_data['ids'],
        "embeddings": all_data['embeddings'],
        "metadatas": all_data['metadatas']
    }
    
    with open(backup_path, 'w') as f:
        json.dump(backup_data, f)
```

## Error Handling

## Database Security

### Access Control
- ChromaDB roda localmente (sem rede)
- Acesso limitado ao sistema de arquivos
- Paths validados (prevenção de traversal)

### Data Encryption
```python
# Planejado para versões futuras
# ChromaDB não tem encriptação nativa at-rest
# Considerar encriptar diretório chroma_db/ com VeraCrypt ou similar
```

## Performance Monitoring

### Collection Statistics (Future)
```python
def get_collection_stats(self, collection_name: str) -> Dict:
    """Obtém estatísticas da coleção"""
    collection = self.get_collection(collection_name)
    
    # Get count
    all_data = collection.get()
    count = len(all_data['ids'])
    
    return {
        "name": collection_name,
        "count": count,
        "embedding_dim": len(all_data['embeddings'][0]) if count > 0 else 0
    }
```

### Query Performance (Future)
```python
import time

def benchmark_search(self, collection_name: str, query_embedding: List[float]):
    """Benchmark de performance de busca"""
    start = time.time()
    results = self.search_similar(collection_name, query_embedding, n_results=10)
    elapsed = time.time() - start
    
    logging.info(f"Busca completada em {elapsed:.3f}s, {len(results)} resultados")
    
    return elapsed
```

---
*Database guidelines for Blind Style Model using GitHub Copilot*
