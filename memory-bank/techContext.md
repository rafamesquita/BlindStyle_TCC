# Contexto Técnico: Blind Style Model
*Versão: 1.0*
*Criado: 2025-10-01*
*Última Atualização: 2025-10-01*

## Stack de Tecnologia

### Backend
- **Linguagem**: Python 3.13+
- **LLM**: Google Gemini 2.5 Pro (para extração de características visuais)
- **Banco Vetorial**: ChromaDB 1.1.1 (busca por similaridade)
- **Computação Numérica**: NumPy 2.3.3

### Processamento de Imagens
- **Pillow**: Manipulação de imagens
- **Gemini Vision API**: Análise de conteúdo visual

### Armazenamento
- **ChromaDB**: Persistência local de embeddings vetoriais
- **JSON**: Armazenamento de metadados e respostas do LLM

### Infraestrutura
- **Execução**: Local (sem cloud)
- **Versionamento**: Git
- **Gerenciamento de Dependências**: pip + requirements.txt

## Configuração do Ambiente de Desenvolvimento

### Pré-requisitos
- Python 3.13 ou superior
- Chave de API do Google Gemini
- Mínimo 8GB RAM (recomendado 16GB para processamento em lote)
- 10GB+ espaço em disco para base de imagens e embeddings

### Setup Inicial

1. **Criar ambiente virtual**:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. **Instalar dependências**:
```powershell
pip install -r requirements.txt
```

3. **Configurar variáveis de ambiente**:
Criar arquivo `.env` na raiz:
```
GEMINI_KEY=sua_chave_api_aqui
```

4. **Estrutura de diretórios**:
```
blindstylemodel/
├── archive/
│   └── images/          # Imagens de peças de roupa
├── responses/           # Respostas do LLM (JSON)
├── filtered_outfits/    # Outfits validados
├── chroma_db/          # Banco vetorial persistente
├── modules/            # Módulos do sistema
└── memory-bank/        # Documentação do projeto
```

## Dependências Principais

### Core
- `google-generativeai==0.8.5`: API do Gemini para extração de features
- `chromadb==1.1.1`: Banco de dados vetorial
- `numpy==2.3.3`: Operações numéricas e embeddings
- `Pillow`: Processamento de imagens
- `python-dotenv`: Gerenciamento de variáveis de ambiente

### Auxiliares
- `coloredlogs==15.0.1`: Logs coloridos para melhor debugging
- `jsonschema==4.25.1`: Validação de estruturas JSON
- `httpx==0.28.1`: Cliente HTTP para APIs

## Restrições Técnicas

### Performance
- **Tempo de resposta**: < 10 segundos para buscas por similaridade
- **Batch processing**: Processar múltiplos outfits em lote
- **Caching**: Embeddings persistentes para evitar reprocessamento

### Reprodutibilidade
- **Seed determinística**: Hash MD5 para geração de embeddings consistentes
- **Versionamento**: Embeddings versionados por configuração
- **Logs**: Rastreamento completo do processamento

### Armazenamento
- **ChromaDB**: Persistência local em `chroma_db/`
- **JSON**: Metadados estruturados
- **Compressão**: Embeddings normalizados (L2 norm)

## Build e Deployment

### Processo de Build
Não há build tradicional, pois é Python interpretado. O "build" envolve:
1. Processar imagens e extrair features (FeatureExtractor)
2. Limpar respostas com erro (JsonCleaner)
3. Filtrar outfits válidos (OutfitFilter)
4. Gerar e armazenar embeddings (EmbeddingGenerator)

### Pipeline de Processamento
```python
# 1. Extração de features
extractor.process_all_folders()

# 2. Limpeza de erros
cleaner.clean_error_responses()

# 3. Filtragem de outfits
outfit_filter.process_responses()

# 4. Geração de embeddings
embedding_generator.process_and_store("pieces")
```

### Procedimento de Deployment
Sistema projetado para execução local:
1. Clonar repositório
2. Configurar ambiente virtual
3. Instalar dependências
4. Configurar `.env`
5. Executar `main.py`

### CI/CD
- **Atual**: Manual (execução local)
- **Futuro**: Testes automatizados com pytest

## Abordagem de Testes

### Testes Unitários
- **Framework**: pytest (a ser implementado)
- **Cobertura**: Funções de embedding, busca vetorial, validação de schema

### Testes de Integração
- **Pipeline end-to-end**: Extração → Limpeza → Filtragem → Embedding → Busca
- **Validação de API**: Testes com mock do Gemini

### Testes E2E
- **Cenários reais**: Processamento de outfits completos
- **Validação de resultados**: Precisão da busca por similaridade

## Configurações do Sistema

### Embeddings
- **Dimensões por atributo**: 16
- **Atributos**: category, item_type, primary_color, usage, texture, print_category
- **Dimensão total por peça**: 96 (6 atributos × 16 dimensões)
- **Normalização**: L2 norm

### Categorias e Valores Válidos
```python
VALID_CATEGORIES = ["tops", "bottoms", "shoes", "others"]
VALID_USAGE = ["casual", "formal", "business", "sportswear", "sleepwear", 
               "outerwear", "party", "workwear"]
VALID_TEXTURE = ["cotton", "denim", "leather", "polyester", "wool", "silk", 
                 "linen", "knit", "suede", "nylon", "fleece", "velvet", 
                 "mesh", "others"]
VALID_PRINT = ["striped", "animal", "floral", "plaid", "plain", 
               "abstract", "logo", "graphic"]
```

### ChromaDB
- **Métrica de similaridade**: Cosine similarity
- **Persistência**: Local (`chroma_db/`)
- **Coleções**: `pieces` (peças individuais)

## Modelos e APIs

### Google Gemini 2.5 Pro
- **Uso**: Extração de características visuais de roupas
- **Input**: Imagens de peças de roupa
- **Output**: JSON estruturado com atributos
- **Rate limiting**: Controlado via backoff

### Prompt Engineering
Prompt especializado para extração estruturada de features de roupas:
- Classificação de categoria
- Identificação de tipo, cor, uso, textura, estampa
- Output em JSON padronizado

---

*Este documento descreve as tecnologias usadas no projeto e como estão configuradas.*
