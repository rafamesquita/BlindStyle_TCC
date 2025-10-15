# Contexto Ativo: Blind Style Model
*Versão: 1.0*
*Criado: 2025-10-01*
*Última Atualização: 2025-10-01*
*Modo RIPER Atual: START*
*Fase do Projeto: INITIALIZING*

## Foco Atual
**Inicialização do Projeto** - Configurando o framework RIPER-Copilot e documentando a estrutura existente do Blind Style Model. O projeto já possui implementação base funcional com pipeline de processamento de roupas, extração de features via LLM, e sistema de embeddings vetoriais.

## Mudanças Recentes
- **2025-10-01**: Inicialização do framework RIPER-Copilot
- **2025-10-01**: Criação do memory-bank com documentação estruturada
- **2025-10-01**: Mapeamento da arquitetura e componentes existentes

## Decisões Ativas

### ✅ Decisões Tomadas
- **Embeddings Determinísticos**: Usar hash MD5 como seed para garantir reprodutibilidade
- **ChromaDB**: Adotado como banco vetorial local
- **Gemini API**: Selecionado para extração de características visuais
- **Pipeline Modular**: Arquitetura em etapas independentes (extração → limpeza → filtragem → embedding → armazenamento)
- **6 Atributos**: category, item_type, primary_color, usage, texture, print_category
- **96 Dimensões**: 6 atributos × 16 dimensões cada

### 🤔 Decisões Pendentes
- **Sistema de Recomendação**: Definir algoritmo para sugerir combinações de peças

## Próximos Passos

### Imediato (Fase START)
1. ✅ Criar memory-bank com documentação base
2. ✅ Gerar custom instructions para GitHub Copilot
3. ✅ Configurar estrutura de custom-instructions/
4. ✅ Transicionar para modo RESEARCH

### Curto Prazo
1. Implementar sistema de recomendação de outfits

## Desafios Atuais

### 🔴 Crítico
- **Nenhum identificado no momento**

### 🟡 Importante
- **Validação de Embeddings**: Garantir que embeddings capturem similaridade semântica adequadamente
- **Performance em Escala**: Testar com bases maiores de imagens
- **Reprodutibilidade**: Validar que seed determinística funciona consistentemente

### 🟢 Nice-to-Have
- **Exportação de Dados**: Permitir export de embeddings e metadados

## Progresso da Implementação

### ✅ Componentes Implementados
- [✓] **FeatureExtractor**: Extração de features via Gemini API
- [✓] **JsonCleaner**: Limpeza e validação de respostas JSON
- [✓] **OutfitFilter**: Filtragem de outfits válidos
- [✓] **EmbeddingGenerator**: Geração de embeddings determinísticos
- [✓] **VectorDB**: Interface com ChromaDB para armazenamento e busca
- [✓] **Config**: Centralização de configurações
- [✓] **Pipeline Base**: `main.py` com orquestração de componentes

### 🔄 Em Desenvolvimento
- [ ] **Sistema de Recomendação**: Algoritmo para sugerir combinações
- [✓] **Custom Instructions**: Geração automática para GitHub Copilot


## Estado do Código

### Estrutura de Diretórios
```
blindstylemodel/
├── archive/images/          # ✅ Base de imagens de roupas
├── responses/               # ✅ Respostas do LLM (JSON)
├── filtered_outfits/        # ✅ Outfits validados
├── chroma_db/              # ✅ Banco vetorial (ChromaDB)
├── modules/                # ✅ Módulos do sistema
│   ├── __init__.py
│   ├── config.py           # ✅ Configurações centralizadas
│   ├── embeddings.py       # ✅ Geração de embeddings
│   ├── feature_extractor.py # ✅ Extração via LLM
│   ├── json_cleaner.py     # ✅ Limpeza de JSONs
│   ├── outfit_filter.py    # ✅ Filtragem de outfits
│   └── vector_db.py        # ✅ Interface ChromaDB
├── memory-bank/            # 🔄 Documentação do projeto
│   ├── state.md            # ✅ Estado do framework
│   ├── projectbrief.md     # ✅ Requisitos e objetivos
│   ├── techContext.md      # ✅ Stack e configurações
│   ├── systemPatterns.md   # ✅ Arquitetura
│   └──  activeContext.md    # 🔄 Contexto atual (este arquivo)
├── main.py                 # ✅ Ponto de entrada
├── requirements.txt        # ✅ Dependências
└── README.md              # ✅ Setup básico
```

### Qualidade do Código
- ✅ **Modularidade**: Componentes bem separados
- ✅ **Type Hints**: Uso consistente de anotações de tipo
- ✅ **Configuração**: Centralizada em `config.py`
- ✅ **Tratamento de Erros**: Presente em loops críticos

## Ambiente de Desenvolvimento

### Configuração Atual
- **Python**: 3.13+
- **Ambiente Virtual**: `venv/`
- **Dependências**: Instaladas via `requirements.txt`
- **API Key**: Configurada via `.env` (GEMINI_KEY)

### Ferramentas Recomendadas
- **IDE**: VS Code com GitHub Copilot

## Notas Técnicas

### Pontos de Atenção
1. **Embeddings**: A função `_hash_embedding` usa MD5 + RNG para gerar vetores. Validar se captura similaridade adequadamente.
2. **IDs Únicos**: Formato `[outfit_id]/[piece_id].jpg` - garantir consistência.
3. **Coleções ChromaDB**: Atualmente usa apenas "pieces", considerar coleções adicionais para outfits completos.
4. **Main.py**: Muito código comentado - precisa limpar e organizar melhor.

---

*Este documento captura o estado atual do trabalho e próximos passos imediatos.*
