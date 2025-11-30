# BlindStyle Front

O BlindStyle é uma aplicação pensada para auxiliar pessoas com deficiência visual na identificação e na combinação de roupas a partir de imagens.

## Visão geral

A versão web do sistema permite que o usuário capture ou suba imagens de roupas. Essas imagens são enviadas a um backend (desenvolvido em FastAPI) que analisa a peça, retorna uma descrição textual, categorias/atributos detectados e sugestões de combinação.

Principais objetivos:
- Acessibilidade: suporte a leitura por voz (text-to-speech).
- Agilidade: envio de imagem e retorno de resultados com sugestões.
- Histórico: salvar e recuperar análises anteriores.

## Principais funcionalidades

- Captura de imagens pela câmera do dispositivo ou seleção do 'Explorador de arquivos'
- Envio da imagem a um backend que extrai descrições e sugestões
- Histórico de peças analisadas
- Integração com serviços de TTS (text-to-speech)

## Tecnologias e bibliotecas

- Framework principal: Angular
- Tipagem estática: TypeScript
- Assinaturas reativas: RxJS
- Formulários reativos: Angular Forms

## Requisitos

- Node.js (versão recomendada: 18+)
- NPM (instalado junto com o Node)
- Angular CLI

## Configuração rápida (Desenvolvimento)

1) Instale dependências:

```powershell
npm install
```

2) Rodar o Servidor de Desenvolvimento:

```powershell
ng serve
```

3) Acesse no navegador:

- http://localhost:4200/

## Estrutura do projeto

Formato resumido da pasta `src/`:

```
src/
├── app/
│   ├── components/                 # Componentes reutilizáveis
│   │   ├── footer/                 # Rodapé da aplicação
│   │   ├── header/                 # Cabeçalho e navegação superior
│   │   ├── menu/                   # Menu lateral
│   │   ├── modal-roupa/            # Modal com detalhes das roupas detectadas
│   │   └── roupa-hist/             # Componente para itens do histórico
│   │
│   ├── environments/
│   │   └── environment.ts          # Variáveis de ambiente (URL da API)
│   │
│   ├── pages/                      # Telas principais (views)
│   │   ├── cadastro/               # Tela de registro do usuário
│   │   ├── foto/                   # Tela de captura/upload de imagens
│   │   ├── historico/              # Tela de histórico de compatibilidades
│   │   └── login/                  # Tela de login/autenticação
│   │
│   ├── services/                   # Serviços (lógica, API, autenticação, TTS)
│   │   ├── auth/                   # Autenticação (login, registro, sessão)
│   │   │   ├── auth.module.ts
│   │   │   └── auth.service.ts
│   │   ├── text-speech/            # Integração com Text-to-Speech
│   │   │   └── text-to-speech.service.ts
│   │   └── api.services.ts         # Comunicação com backend (requisições HTTP)
│   │
│   ├── app.component.*             # Componente raiz da aplicação
│   ├── app.config.ts               # Configurações gerais (providers, imports)
│   └── app.routes.ts               # Definição das rotas da aplicação
│
├── assets/                         # Imagens, ícones, arquivos estáticos
│
...
```