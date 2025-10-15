description: MUST BE APPLIED WHEN working on any code within Blind Style Model. Covers general development patterns including naming conventions, project structure, code organization, and project-specific standards.
applyTo: "**/*"
alwaysApply: false

# General Development Guidelines: Blind Style Model

## Project Context
**Project**: Blind Style Model
**Primary Language**: Python 3.13+
**Main Framework**: ChromaDB (Vector Database), Google Gemini API
**Architecture**: Modular Pipeline Architecture

### Overview
Sistema de recomendação de roupas baseado em busca por similaridade vetorial, desenvolvido para auxiliar pessoas que buscam aprimorar suas maneiras de vestir e, especialmente, pessoas cegas e com deficiência visual. O sistema permite extrair características de peças de roupa, avaliá-las, buscar combinações similares e gerenciar um acervo de peças através de embeddings semânticos.

## Development Philosophy

### Core Principles
- **Acessibilidade em Primeiro Lugar**: Todo código deve considerar o impacto na experiência de pessoas com deficiência visual
- **Reprodutibilidade Garantida**: Embeddings e processamento devem ser determinísticos (seed baseada em hash MD5)
- **Modularidade**: Componentes independentes e bem definidos
- **Pipeline Claro**: Fluxo de dados sequencial e previsível (Extração → Limpeza → Filtragem → Embedding → Armazenamento)
- **Execução Local**: Sistema projetado para rodar completamente offline
- **Qualidade dos Dados**: Validação rigorosa em cada etapa do pipeline

### Design Decisions
- Hash-based embeddings para garantir reprodutibilidade
- ChromaDB para persistência local sem necessidade de cloud
- Gemini API para extração de características visuais
- Atributos estruturados e vocabulário controlado

## Naming Conventions
**Detected from existing codebase:**
- **Modules**: snake_case (`feature_extractor.py`, `vector_db.py`, `embeddings.py`)
- **Classes**: PascalCase (`FeatureExtractor`, `VectorDB`, `EmbeddingGenerator`, `JsonCleaner`, `OutfitFilter`)
- **Methods/Functions**: snake_case (`process_all_folders`, `add_items`, `search_similar`, `_hash_embedding`, `_process_outfit`)
- **Variables**: snake_case (`outfit_data`, `piece_embedding`, `collection_name`, `query_embedding`)
- **Constants**: UPPER_SNAKE_CASE (`VALID_CATEGORIES`, `ATTR_DIM`, `PIECE_DIM`, `GEMINI_API_KEY`, `MAX_ITEMS_PER_OUTFIT`)
- **Private Methods**: Prefixo underscore `_` (`_hash_embedding`, `_generate_piece_embedding`, `_process_outfit`)
- **Files/Directories**: snake_case (`filtered_outfits/`, `chroma_db/`, `responses/`)

## Project Structure
```
blindstylemodel/
├── archive/
│   └── images/              # Imagens de peças de roupa (input)
├── responses/               # Respostas do LLM em JSON (etapa 1)
├── filtered_outfits/        # Outfits validados (etapa 3)
├── chroma_db/              # Banco vetorial persistente (ChromaDB)
├── modules/                # Módulos do sistema
│   ├── __init__.py
│   ├── config.py           # Configurações centralizadas
│   ├── embeddings.py       # Geração de embeddings determinísticos
│   ├── feature_extractor.py # Extração via Gemini API
│   ├── json_cleaner.py     # Limpeza de JSONs
│   ├── outfit_filter.py    # Filtragem de outfits
│   └── vector_db.py        # Interface ChromaDB
├── memory-bank/            # Documentação do projeto (RIPER Framework)
├── custom-instructions/    # Instruções do GitHub Copilot
├── main.py                 # Ponto de entrada e orquestração
├── requirements.txt        # Dependências Python
├── .env                    # Variáveis de ambiente (GEMINI_KEY)
└── README.md              # Setup e documentação básica
```

## Code Organization Patterns

### Module Responsibilities
- **config.py**: Constantes, paths, enums, prompts, configurações globais
- **feature_extractor.py**: Extração de features de imagens via LLM
- **json_cleaner.py**: Validação e limpeza de respostas JSON
- **outfit_filter.py**: Filtragem de outfits por regras de negócio
- **embeddings.py**: Geração de embeddings determinísticos (hash-based)
- **vector_db.py**: Abstração do ChromaDB (CRUD de embeddings)

### File Organization
- Um módulo por responsabilidade (Single Responsibility Principle)
- Classes coesas com métodos privados auxiliares
- Configurações centralizadas em `config.py`
- Type hints obrigatórios em métodos públicos
- Docstrings em formato Google (Args, Returns, Raises)

### Import/Dependency Management
```python
# Ordem padrão de imports:
# 1. Standard library
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 2. Third-party libraries
import numpy as np
import chromadb
from chromadb.config import Settings

# 3. Local modules
from modules.config import FILTERED_DIR, ATTR_DIM, ATTRIBUTES
from .vector_db import VectorDB
```

## Technology Stack
- **Main Stack**: Python 3.13+, ChromaDB 1.1.1, Google Gemini 2.5 Pro, NumPy 2.3.3
- **Key Dependencies**: 
  - `google-generativeai==0.8.5` (Extração de features visuais)
  - `chromadb==1.1.1` (Banco vetorial)
  - `numpy==2.3.3` (Operações numéricas)
  - `Pillow` (Processamento de imagens)
  - `python-dotenv` (Gerenciamento de variáveis de ambiente)
- **Build Tools**: pip (gerenciamento de dependências)
- **Testing Framework**: pytest (a ser implementado)

## Code Examples - Well Structured

### Example 1: Hash-based Deterministic Embedding
```python
def _hash_embedding(self, text: str, dim: int = 16) -> np.ndarray:
    """Gera embedding determinístico baseado em hash MD5
    
    Args:
        text: String para gerar embedding (ex: "category:tops")
        dim: Dimensões do vetor resultante
        
    Returns:
        np.ndarray: Vetor normalizado (L2 norm)
    """
    # Create a deterministic seed from md5 hash
    md5 = hashlib.md5(text.encode("utf-8")).hexdigest()
    seed = int(md5[:8], 16)  # use first 8 hex digits as integer

    rng = np.random.default_rng(seed)
    vec = rng.standard_normal(dim)
    return vec / np.linalg.norm(vec)
```

### Example 2: VectorDB CRUD Operations
```python
def add_items(
    self,
    collection_name: str,
    embeddings: List[List[float]],
    ids: List[str],
    metadatas: Optional[List[Dict]] = None
) -> None:
    """Adiciona itens a uma coleção
    
    Args:
        collection_name: Nome da coleção
        embeddings: Lista de embeddings
        ids: Lista de IDs únicos
        metadatas: Lista de metadados (opcional)
    """
    collection = self.get_collection(collection_name)
    collection.add(
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
```

### Example 3: Processing Pipeline
```python
def main():
    # Inicializa componentes
    extractor = FeatureExtractor()
    cleaner = JsonCleaner()
    outfit_filter = OutfitFilter()
    vector_db = VectorDB()
    
    # Pipeline de processamento
    extractor.process_all_folders()    # 1. Extração
    cleaner.clean_error_responses()    # 2. Limpeza
    outfit_filter.process_responses()  # 3. Filtragem
    
    # Gera e armazena embeddings
    embedding_generator = EmbeddingGenerator(vector_db=vector_db)
    embedding_generator.process_and_store("pieces")
```

## Antipatterns to Avoid

### Project-Specific Antipatterns
1. **❌ Embeddings Não-Determinísticos**: Nunca use `random.random()` ou `np.random.rand()` sem seed fixa
   - ✅ Use `_hash_embedding()` para garantir reprodutibilidade

2. **❌ Hardcoded Paths**: Evite paths absolutos ou hardcoded
   - ✅ Use variáveis de `config.py` (BASE_DIR, IMAGES_DIR, etc.)

3. **❌ API Keys no Código**: Nunca commitar API keys
   - ✅ Use `.env` e `os.getenv()`

4. **❌ Processing Sem Validação**: Não processar dados sem validar estrutura
   - ✅ Valide schemas em cada etapa (JsonCleaner, OutfitFilter)


### Common Antipatterns
- ❌ Deep nesting (max 3-4 levels)
- ❌ Unclear or abbreviated variable names (`df`, `tmp`, `x`)
- ❌ Large functions (keep under 50 lines when possible)
- ❌ Mixed concerns (ex: extração + validação na mesma função)
- ❌ Hardcoded values - use configuration
- ❌ Missing type hints on public methods
- ❌ Lack of docstrings on classes and public methods

## Quality Guidelines
- **Documentation**: Docstrings obrigatórias em classes e métodos públicos (formato Google)
- **Performance**: Busca por similaridade < 10 segundos
- **Security**: API keys em `.env`, validação de inputs, sanitização de dados

## Error Handling

### Consistent Error Handling Patterns
```python
def process_outfit(self, outfit_data: Dict, file_name: str) -> Tuple[List[np.ndarray], List[str]]:
    """Processa um outfit gerando embeddings e metadados"""
    embeddings = []
    ids = []
    
    for piece_id, piece_data in outfit_data.items():
        try:
            # Gera embedding da peça
            piece_embedding = self._generate_piece_embedding(piece_data)
            embeddings.append(piece_embedding)
            ids.append(f"{outfit_name}/{piece_id}")
            
        except Exception as e:
            print(f"❌ Erro ao processar peça {piece_id}: {e}")
            continue  # Não falhar todo outfit por erro em uma peça
            
    return embeddings, ids
```

### Best Practices
- Use try-except em loops de processamento
- Log erros detalhados com contexto (file name, piece ID, etc.)
- Continue processamento quando possível (fail gracefully)
- Valide inputs em boundaries (início de funções públicas)
- Retorne tuplas ou None para indicar falhas

## Performance Considerations
- **Embeddings em Lote**: Processe múltiplos embeddings de uma vez (`add_items` vs `add_item`)
- **Cache**: ChromaDB já persiste embeddings, evite reprocessar
- **Normalização**: Vetores já normalizados (L2 norm) para busca cosine eficiente
- **Batch Size**: Processar imagens em batches (configurável via `limit` parameter)
- **Memory Management**: Não carregar toda base de imagens na memória de uma vez

### Optimization Guidelines
- Profile antes de otimizar (não otimização prematura)
- Use `np.ndarray` ao invés de listas Python para operações numéricas
- Minimize chamadas à API Gemini (custos e rate limits)
- ChromaDB usa HNSW index (eficiente para busca aproximada)

## Data Structures and Types

### Key Data Types
```python
# Embedding: vetor 96D (6 atributos × 16 dimensões)
embedding: np.ndarray  # shape: (96,)

# Piece data structure
piece_data: Dict[str, str] = {
    "category": "tops",
    "item_type": "tshirt",
    "primary_color": "blue",
    "usage": "casual",
    "texture": "cotton",
    "print_category": "graphic"
}

# Outfit data structure
outfit_data: Dict[str, Dict] = {
    "1.jpg": piece_data,
    "2.jpg": piece_data,
    ...
}

# Search results
results: List[Dict[str, Any]] = [
    {"id": "outfit_id/piece_id.jpg", "distance": 0.15},
    ...
]
```

## Configuration Management
- Todas as configurações em `modules/config.py`
- Variáveis de ambiente em `.env` (não commitado)
- Paths usando `pathlib.Path` para compatibilidade cross-platform
- Enums para valores válidos (VALID_CATEGORIES, VALID_USAGE, etc.)
- Dimensões de embeddings configuráveis (ATTR_DIM, PIECE_DIM)

---
*General development guidelines for Blind Style Model using GitHub Copilot*
