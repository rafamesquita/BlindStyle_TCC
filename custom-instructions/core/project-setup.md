description: MUST BE APPLIED WHEN setting up project, configuring environments, or managing dependencies.
applyTo: "**/requirements.txt,**/.env*,**/README.md,**/config/**/*,**/*.ini,**/*.cfg"
alwaysApply: false

# Project Setup Guidelines: Blind Style Model

## Project Overview

**Project**: Sistema de recomendação de roupas baseado em busca por similaridade vetorial
**Purpose**: Auxiliar pessoas (especialmente com deficiência visual) a escolher e combinar roupas
**Technology Stack**: Python 3.13+, ChromaDB, Google Gemini API, NumPy
**Architecture**: Modular pipeline (Extração → Limpeza → Filtragem → Embedding → Armazenamento)

## Environment Setup

### Prerequisites
- **Python**: 3.13 ou superior
- **Sistema Operacional**: Windows, Linux, macOS
- **Memória**: Mínimo 8GB RAM (recomendado 16GB)
- **Espaço em Disco**: 10GB+ para imagens e embeddings
- **Rede**: Acesso à internet para API do Gemini

### Installation Guide


#### 1. Criar Ambiente Virtual
```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### 2. Instalar Dependências
```powershell
pip install -r requirements.txt
```

#### 3. Configurar Variáveis de Ambiente
```powershell
# Criar arquivo .env na raiz do projeto
New-Item -Path .env -ItemType File

# Adicionar chave da API Gemini
"GEMINI_KEY=sua_chave_api_aqui" | Out-File -FilePath .env -Encoding UTF8
```

#### 4. Verificar Instalação
```powershell
python -c "import modules; print('Setup completo!')"
```

## Configuration Management

### Environment Variables
```env
# .env (NUNCA COMMITAR)
GEMINI_KEY=your_actual_api_key_here
```

### Configuration Files
- **`modules/config.py`**: Configurações centralizadas
  - Paths de diretórios
  - Dimensões de embeddings
  - Categorias válidas
  - Prompts do LLM
  
### Key Configurations
```python
# config.py principais configurações
GEMINI_API_KEY = os.getenv('GEMINI_KEY')
LLM_MODEL = "gemini-2.5-pro"

# Dimensões de embeddings
ATTR_DIM = 16
PIECE_DIM = 96  # 6 atributos × 16 dimensões

# Limites de processamento
MAX_ITEMS_PER_OUTFIT = 5

# Categorias válidas
VALID_CATEGORIES = ["tops", "bottoms", "shoes", "others"]
VALID_USAGE = ["casual", "formal", "business", "sportswear", ...]
VALID_TEXTURE = ["cotton", "denim", "leather", "polyester", ...]
VALID_PRINT = ["striped", "animal", "floral", "plaid", "plain", ...]
```

## Directory Structure

### Project Layout
```
blindstylemodel/
├── archive/
│   └── images/              # INPUT: Imagens de roupas
├── responses/               # OUTPUT: Respostas do LLM (JSON)
├── filtered_outfits/        # OUTPUT: Outfits validados
├── chroma_db/              # OUTPUT: Banco vetorial (ChromaDB)
├── modules/                # Código principal
│   ├── __init__.py
│   ├── config.py           # Configurações
│   ├── embeddings.py       # Geração de embeddings
│   ├── feature_extractor.py # Extração via LLM
│   ├── json_cleaner.py     # Limpeza de JSONs
│   ├── outfit_filter.py    # Filtragem
│   └── vector_db.py        # Interface ChromaDB
├── memory-bank/            # Documentação RIPER
├── custom-instructions/    # GitHub Copilot instructions
├── main.py                 # Ponto de entrada
├── requirements.txt        # Dependências Python
├── .env                    # Variáveis de ambiente (não commitado)
├── .gitignore
└── README.md
```

### Directory Permissions
```powershell
# Criar diretórios necessários se não existirem
mkdir -p archive/images responses filtered_outfits chroma_db
```

## Dependency Management

### Core Dependencies
```txt
# requirements.txt (principais)
google-generativeai==0.8.5   # Gemini API
chromadb==1.1.1              # Vector database
numpy==2.3.3                 # Operações numéricas
Pillow                       # Processamento de imagens
python-dotenv                # Variáveis de ambiente
```

### Installing New Dependencies
```powershell
# Adicionar nova dependência
pip install <package_name>

# Atualizar requirements.txt
pip freeze > requirements.txt
```

### Updating Dependencies
```powershell
# Verificar dependências desatualizadas
pip list --outdated

# Atualizar pacote específico
pip install --upgrade <package_name>

# Atualizar todas (cuidado!)
pip install --upgrade -r requirements.txt
```

## Running the Application

### Basic Usage
```powershell
# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Executar pipeline completo
python main.py
```

### Pipeline Steps (Manual)
```python
# main.py - Executar etapas individualmente
from modules import FeatureExtractor, JsonCleaner, OutfitFilter, EmbeddingGenerator, VectorDB

# 1. Extrair features de imagens
extractor = FeatureExtractor()
extractor.process_all_folders()

# 2. Limpar respostas com erro
cleaner = JsonCleaner()
cleaner.clean_error_responses()

# 3. Filtrar outfits válidos
outfit_filter = OutfitFilter()
outfit_filter.process_responses()

# 4. Gerar e armazenar embeddings
vector_db = VectorDB()
embedding_generator = EmbeddingGenerator(vector_db=vector_db)
embedding_generator.process_and_store("pieces")

# 5. Buscar peças similares
query_embedding = embedding_generator._generate_piece_embedding(piece_data)
results = vector_db.search_similar("pieces", query_embedding, n_results=5)
```

## Troubleshooting

### Common Issues

#### Issue 1: GEMINI_KEY not found
```
ValueError: GEMINI_API_KEY não encontrada nas variáveis de ambiente
```
**Solution**: Crie arquivo `.env` com `GEMINI_KEY=sua_chave_aqui`

#### Issue 2: Module not found
```
ModuleNotFoundError: No module named 'chromadb'
```
**Solution**: `pip install -r requirements.txt`

#### Issue 3: Permission denied (chroma_db)
```
PermissionError: [Errno 13] Permission denied: 'chroma_db'
```
**Solution**: Verificar permissões da pasta ou executar com privilégios adequados

#### Issue 4: API Rate Limit
```
google.api_core.exceptions.ResourceExhausted: 429 Quota exceeded
```
**Solution**: Aguardar ou reduzir taxa de requisições (implementar backoff)

## Development Tools Setup

### Recommended IDE Extensions (VS Code)
- **Python** (ms-python.python): Suporte Python
- **Pylance** (ms-python.vscode-pylance): Type checking
- **GitHub Copilot** (GitHub.copilot): AI assistance
- **autoDocstring** (njpwerner.autodocstring): Docstring generator


## Performance Optimization

### Memory Management
- Processar imagens em batches (não todas de uma vez)
- Liberar memória após processamento de cada outfit
- Usar generators para processar grandes volumes


### Database Optimization
- Usar batch inserts (`add_items` ao invés de `add_item`)
- Limitar `n_results` em buscas (default: 5-10)
- Usar filtros de metadata para reduzir espaço de busca

## Security Best Practices

### API Key Protection
- ✅ Sempre usar `.env` para API keys
- ❌ Nunca commitar API keys no código
- ❌ Nunca logar API keys completas

### File System Security
- Validar todos os paths antes de usar
- Prevenir directory traversal attacks
- Sanitizar nomes de arquivos de input

## Backup and Recovery

### Backup Recommendations
```powershell
# Backup do banco vetorial
Copy-Item -Path chroma_db -Destination "chroma_db_backup_$(Get-Date -Format 'yyyyMMdd')" -Recurse

# Backup de outfits filtrados
Copy-Item -Path filtered_outfits -Destination "filtered_outfits_backup_$(Get-Date -Format 'yyyyMMdd')" -Recurse
```

### Recovery Process
```powershell
# Restaurar banco vetorial
Remove-Item -Path chroma_db -Recurse -Force
Copy-Item -Path chroma_db_backup_20251015 -Destination chroma_db -Recurse
```

---
*Project setup guidelines for Blind Style Model using GitHub Copilot*
