# Padrões do Sistema: Blind Style Model
*Versão: 1.0*
*Criado: 2025-10-01*
*Última Atualização: 2025-10-01*

## Visão Geral da Arquitetura

O **Blind Style Model** utiliza uma arquitetura modular baseada em pipeline de processamento, onde cada módulo tem uma responsabilidade específica e bem definida. A arquitetura segue o padrão de **feature engineering** para sistemas de recomendação, combinando extração de características via LLM, embeddings vetoriais e busca por similaridade.

```
┌─────────────────┐
│   Imagens       │
│   de Roupas     │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│ FeatureExtractor    │ ← Gemini API
│ (LLM Vision)        │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   JSON Responses    │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   JsonCleaner       │
│ (Error Handling)    │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   OutfitFilter      │
│ (Validation)        │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ EmbeddingGenerator  │
│ (Hash-based)        │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   VectorDB          │ ← ChromaDB
│ (Similarity Search) │
└─────────────────────┘
```

## Componentes Chave

### 1. **FeatureExtractor** (`modules/feature_extractor.py`)
- **Propósito**: Extrair características estruturadas de imagens de roupas usando LLM
- **Responsabilidades**:
  - Processar imagens em lote de diretórios
  - Enviar imagens para Gemini API com prompt estruturado
  - Salvar respostas JSON com metadados extraídos
- **Inputs**: Imagens de roupas (`archive/images/`)
- **Outputs**: Arquivos JSON com features (`responses/`)

### 2. **JsonCleaner** (`modules/json_cleaner.py`)
- **Propósito**: Validar e limpar respostas do LLM
- **Responsabilidades**:
  - Identificar respostas com erros ou formato inválido
  - Remover JSONs malformados
  - Garantir qualidade dos dados para processamento posterior
- **Inputs**: JSONs de respostas (`responses/`)
- **Outputs**: JSONs validados (mantidos em `responses/`)

### 3. **OutfitFilter** (`modules/outfit_filter.py`)
- **Propósito**: Filtrar e validar outfits completos
- **Responsabilidades**:
  - Validar estrutura de outfits (máximo 5 peças)
  - Verificar categorias válidas (tops, bottoms, shoes, others)
  - Garantir presença de atributos obrigatórios
  - Salvar outfits validados
- **Inputs**: JSONs de respostas (`responses/`)
- **Outputs**: Outfits filtrados (`filtered_outfits/`)

### 4. **EmbeddingGenerator** (`modules/embeddings.py`)
- **Propósito**: Gerar embeddings determinísticos para peças de roupa
- **Responsabilidades**:
  - Criar embeddings de 96 dimensões (6 atributos × 16 dim)
  - Usar hash MD5 para garantir reprodutibilidade
  - Normalizar vetores (L2 norm)
  - Processar outfits e extrair peças individuais
- **Inputs**: Outfits filtrados (`filtered_outfits/`)
- **Outputs**: Embeddings armazenados no VectorDB

### 5. **VectorDB** (`modules/vector_db.py`)
- **Propósito**: Gerenciar armazenamento e busca de embeddings
- **Responsabilidades**:
  - Interface com ChromaDB
  - Criar/gerenciar coleções de peças
  - Adicionar embeddings com IDs e metadados
  - Realizar buscas por similaridade cosine
  - Recuperar embeddings por ID
- **Backend**: ChromaDB persistente (`chroma_db/`)

### 6. **Config** (`modules/config.py`)
- **Propósito**: Centralizar configurações do sistema
- **Responsabilidades**:
  - Definir caminhos de diretórios
  - Manter constantes de categorias válidas
  - Configurar dimensões de embeddings
  - Armazenar prompt de extração de features
  - Gerenciar API keys

## Padrões de Design em Uso

### 1. **Pipeline Pattern**
- **Contexto**: Processamento sequencial de dados através de múltiplos estágios
- **Implementação**: Extração → Limpeza → Filtragem → Embedding → Armazenamento
- **Benefício**: Separação clara de responsabilidades, fácil debugging

### 2. **Repository Pattern**
- **Contexto**: VectorDB atua como repositório de embeddings
- **Implementação**: Interface limpa para operações CRUD no ChromaDB
- **Benefício**: Abstração da camada de persistência

### 3. **Strategy Pattern (Embeddings)**
- **Contexto**: Diferentes estratégias de encoding para atributos
- **Implementação**: Hash-based embeddings determinísticos
- **Benefício**: Flexibilidade para trocar estratégia de embedding

### 4. **Factory Pattern (Coleções)**
- **Contexto**: Criação de coleções no VectorDB
- **Implementação**: `get_or_create_collection()`
- **Benefício**: Gerenciamento transparente de recursos

### 5. **Singleton-like (Config)**
- **Contexto**: Configurações globais do sistema
- **Implementação**: Módulo de configuração importado
- **Benefício**: Configuração centralizada e consistente

## Fluxo de Dados

### Pipeline de Processamento Completo

```
┌──────────────────────────────────────────────────────────┐
│                    FASE 1: EXTRAÇÃO                       │
├──────────────────────────────────────────────────────────┤
│ 1. Ler imagens de archive/images/                        │
│ 2. Agrupar em batches (ex: 5 imagens por outfit)         │
│ 3. Enviar para Gemini API com prompt estruturado         │
│ 4. Receber JSON com features: {                          │
│      "1.jpg": {category, item_type, primary_color, ...}  │
│    }                                                      │
│ 5. Salvar em responses/[outfit_id].json                  │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│                    FASE 2: LIMPEZA                        │
├──────────────────────────────────────────────────────────┤
│ 1. Ler todos JSONs em responses/                         │
│ 2. Validar estrutura e presença de campos                │
│ 3. Remover JSONs com erros ou malformados                │
│ 4. Manter apenas respostas válidas                       │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│                   FASE 3: FILTRAGEM                       │
├──────────────────────────────────────────────────────────┤
│ 1. Validar categorias (tops, bottoms, shoes, others)     │
│ 2. Verificar número de peças (≤ MAX_ITEMS_PER_OUTFIT)    │
│ 3. Confirmar atributos obrigatórios presentes            │
│ 4. Salvar outfits válidos em filtered_outfits/           │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│                   FASE 4: EMBEDDING                       │
├──────────────────────────────────────────────────────────┤
│ 1. Ler outfits de filtered_outfits/                      │
│ 2. Para cada peça:                                        │
│    a) Gerar hash MD5 de "attr:value"                     │
│    b) Usar hash como seed para RNG                       │
│    c) Gerar vetor 16D normalizado por atributo           │
│    d) Concatenar 6 atributos = 96D                       │
│ 3. Criar ID único: "[outfit_id]/[piece_id].jpg"          │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│                 FASE 5: ARMAZENAMENTO                     │
├──────────────────────────────────────────────────────────┤
│ 1. Conectar ao ChromaDB (chroma_db/)                     │
│ 2. Criar/obter coleção "pieces"                          │
│ 3. Adicionar embeddings com:                             │
│    - ID: outfit_id/piece_id                              │
│    - Embedding: vetor 96D                                │
│    - Metadata: atributos originais (opcional)            │
│ 4. Persistir no disco                                    │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│                     FASE 6: BUSCA                         │
├──────────────────────────────────────────────────────────┤
│ 1. Gerar embedding de query (mesma lógica)               │
│ 2. Buscar top-k similares (cosine similarity)            │
│ 3. Retornar IDs e distâncias                             │
│ 4. Recuperar metadados se necessário                     │
└──────────────────────────────────────────────────────────┘
```

## Decisões Técnicas Chave

### 1. **Hash-based Embeddings (MD5 + RNG)**
- **Decisão**: Usar hash MD5 como seed para geração determinística de embeddings
- **Justificativa**:
  - ✅ Reprodutibilidade total (mesmo input → mesmo output)
  - ✅ Não requer treinamento de modelo
  - ✅ Rápido e eficiente
  - ✅ Independente de dados externos
- **Trade-off**: Menos expressivo que embeddings aprendidos, mas suficiente para MVP

### 2. **ChromaDB como Vector Store**
- **Decisão**: Usar ChromaDB para armazenamento de embeddings
- **Justificativa**:
  - ✅ Persistência local (sem cloud)
  - ✅ Busca por similaridade eficiente (HNSW)
  - ✅ Interface Python simples
  - ✅ Leve e adequado para MVP
- **Alternativas consideradas**: Faiss (mais complexo), Milvus (overkill)

### 3. **Gemini para Extração de Features**
- **Decisão**: Usar Gemini 2.5 Pro para análise visual
- **Justificativa**:
  - ✅ API de visão computacional robusta
  - ✅ Capacidade de seguir prompts estruturados
  - ✅ Output JSON estruturado
  - ✅ Menor custo que treinar modelo próprio
- **Trade-off**: Dependência de API externa, mas aceitável para MVP

### 4. **Pipeline Modular**
- **Decisão**: Separar processamento em módulos independentes
- **Justificativa**:
  - ✅ Testabilidade individual
  - ✅ Debugging facilitado
  - ✅ Reusabilidade de componentes
  - ✅ Manutenção simplificada

### 5. **Atributos Estruturados**
- **Decisão**: Usar 6 atributos fixos (category, item_type, primary_color, usage, texture, print_category)
- **Justificativa**:
  - ✅ Cobertura suficiente para recomendação
  - ✅ Vocabulário controlado (enums)
  - ✅ Consistência nos embeddings
  - ✅ Facilita interpretabilidade

## Relacionamentos de Componentes

### Dependências Diretas
```
main.py
  ├── FeatureExtractor
  │     └── config (GEMINI_API_KEY, IMAGES_DIR, RESPONSES_DIR)
  ├── JsonCleaner
  │     └── config (RESPONSES_DIR)
  ├── OutfitFilter
  │     └── config (RESPONSES_DIR, FILTERED_DIR, VALID_*)
  ├── EmbeddingGenerator
  │     ├── config (FILTERED_DIR, ATTRIBUTES, ATTR_DIM)
  │     └── VectorDB
  └── VectorDB
        └── config (VECTOR_DB_DIR)
```

### Fluxo de Dados entre Módulos
1. **FeatureExtractor** → produz → `responses/*.json`
2. **JsonCleaner** → consome/limpa → `responses/*.json`
3. **OutfitFilter** → consome → `responses/*.json` → produz → `filtered_outfits/*.json`
4. **EmbeddingGenerator** → consome → `filtered_outfits/*.json` → produz → embeddings
5. **VectorDB** → persiste → embeddings em `chroma_db/`

### Interface de Busca
```python
# Buscar peças similares
results = vector_db.search_similar(
    collection_name="pieces",
    query_embedding=embedding_da_peca,
    n_results=5
)

# Recuperar por ID
piece = vector_db.get_by_id("pieces", "193875024/1.jpg")
```

## Padrões de Código

### Convenções de Nomenclatura
- **Módulos**: snake_case (`feature_extractor.py`)
- **Classes**: PascalCase (`FeatureExtractor`, `VectorDB`)
- **Métodos**: snake_case (`process_all_folders`, `add_items`)
- **Constantes**: UPPER_SNAKE_CASE (`VALID_CATEGORIES`, `ATTR_DIM`)
- **Privado**: prefixo `_` (`_hash_embedding`, `_process_outfit`)

### Estrutura de Métodos
- Métodos públicos: Interface clara e documentada
- Métodos privados: Lógica interna e auxiliar
- Type hints: Uso consistente (`List`, `Dict`, `Optional`, `Tuple`)
- Docstrings: Formato Google (Args, Returns, Raises)

### Tratamento de Erros
- Try-except em loops de processamento
- Logging de erros detalhados
- Continuidade de pipeline (não falhar tudo por um erro)

---

*Este documento captura a arquitetura do sistema e padrões de design usados no projeto.*
