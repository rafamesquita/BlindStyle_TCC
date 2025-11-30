# BlindStyle App

O BlindStyle é uma aplicação pensada para auxiliar pessoas com deficiência visual na identificação e na combinação de roupas a partir de imagens.

## Visão geral

O app permite que o usuário capture ou suba imagens de roupas. Essas imagens são enviadas a um backend (desenvolvido em FastAPI) que analisa a peça, retorna uma descrição textual, categorias/atributos detectados e sugestões de combinação.

Principais objetivos:
- Acessibilidade: contraste alto, ajuste de tamanho de fonte e suporte a leitura por voz (text-to-speech).
- Agilidade: envio de imagem e retorno de resultados com sugestões.
- Histórico: salvar e recuperar análises anteriores.

## Principais funcionalidades

- Captura de imagens pela câmera do dispositivo ou seleção da galeria
- Envio da imagem a um backend que extrai descrições e sugestões
- Histórico de peças analisadas
- Ajustes de acessibilidade (alto contraste, fonte maior)
- Integração com serviços de TTS (text-to-speech)

## Tecnologias e bibliotecas

- Flutter (Dart)
- State management: MobX + flutter_mobx
- Injeção de dependências: get_it
- Comunicação HTTP: http
- Captura de imagens: image_picker
- TTS: flutter_tts
- Armazenamento local: shared_preferences

## Requisitos

- Flutter instalado (recomenda-se a versão estável compatível com o SDK do projeto: ver `pubspec.yaml` — environment sdk: ^3.7.0)
- Android Studio / Xcode (opcional, para emuladores e builds de release)
- Dispositivo com câmera ou emulador com suporte a câmera

## Configuração rápida (Desenvolvimento)

1) Instale dependências:

```powershell
flutter pub get
```

2) Gere os arquivos gerados pelo MobX (build_runner):

```powershell
flutter pub run build_runner build --delete-conflicting-outputs
```

3) Rodar o app em modo debug:

```powershell
flutter run
```

4) Build de produção (Android):

```powershell
flutter build apk --release
```

## Estrutura do projeto

Formato resumido da pasta `lib/`:

```
lib/
├── app.dart                  # Configuração do MaterialApp, temas e pontos de entrada das telas
├── main.dart                 # Inicialização (setupLocator com URL do backend)
├── data/                     # Serviços que fazem chamadas HTTP ao backend
│   └── services/
├── di/                       # Registro de dependências com get_it (service_locator.dart)
├── navigation/               # Definição de rotas e mapeamento de páginas (routes.dart)
├── stores/                   # MobX stores (estado da aplicação)
├── themes/                   # Tema claro/escuro/alto contraste
├── views/                    # Telas (camera, histórico, configurações, splash, etc.)
└── widgets/                  # Widgets reutilizáveis
```