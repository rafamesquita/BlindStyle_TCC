description: MUST BE APPLIED WHEN working on security-related code including API authentication, data protection, input validation, and secure coding practices.
applyTo: "**/config.py,**/.env*,**/security/**/*,**/auth/**/*,**/validators/**/*"
alwaysApply: false

# Security Guidelines: Blind Style Model

## Security Philosophy

### Security Principles
- **API Key Protection**: Nunca expor GEMINI_KEY no código
- **Input Validation**: Validar todos os dados antes de processar
- **Data Privacy**: Proteger dados sensíveis (imagens de usuários)
- **Secure Defaults**: Configurações seguras por padrão
- **Fail Securely**: Erros não devem vazar informação sensível


## API Key and Secrets Management

### ✅ DO: Secure API Key Storage
```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY não encontrada. Crie .env com a chave.")
```

### ❌ DON'T: Hardcode API Keys
```python
# ❌ NUNCA FAÇA ISSO
GEMINI_API_KEY = "AIzaSyB..."  # Hardcoded
```

### .env File Management
```bash
# .env (NUNCA COMMITAR)
GEMINI_KEY=your_actual_api_key_here

# Use .gitignore para proteger
.env
.env.local
.env.production
```

## Input Validation and Sanitization

### File Path Validation (Future)
```python
from pathlib import Path

def validate_image_path(path: str) -> Path:
    """Valida path de imagem para prevenir directory traversal"""
    image_path = Path(path).resolve()
    
    # Verificar que path está dentro do diretório permitido
    if not str(image_path).startswith(str(IMAGES_DIR.resolve())):
        raise ValueError(f"Path inválido: {path}")
    
    # Verificar extensão permitida
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    if image_path.suffix.lower() not in allowed_extensions:
        raise ValueError(f"Extensão não permitida: {image_path.suffix}")
    
    return image_path
```

### JSON Schema Validation (Future)
```python
def validate_piece_data(piece_data: Dict[str, str]) -> bool:
    """Valida estrutura de dados de peça"""
    required_fields = [
        "category", "item_type", "primary_color",
        "usage", "texture", "print_category"
    ]
    
    # Verificar campos obrigatórios
    for field in required_fields:
        if field not in piece_data:
            raise ValueError(f"Campo obrigatório ausente: {field}")
    
    # Validar categorias
    if piece_data["category"] not in VALID_CATEGORIES:
        raise ValueError(f"Categoria inválida: {piece_data['category']}")
    
    if piece_data["usage"] not in VALID_USAGE:
        raise ValueError(f"Usage inválido: {piece_data['usage']}")
    
    # Validar tipos de dados
    for field, value in piece_data.items():
        if not isinstance(value, str):
            raise TypeError(f"Campo {field} deve ser string, recebeu {type(value)}")
    
    return True
```

### Sanitize User Input (Future)
```python
def sanitize_filename(filename: str) -> str:
    """Sanitiza nome de arquivo para prevenir injeção"""
    import re
    
    # Remove caracteres perigosos
    safe_filename = re.sub(r'[^\w\s.-]', '', filename)
    
    # Previne path traversal
    safe_filename = safe_filename.replace('..', '')
    safe_filename = safe_filename.replace('/', '')
    safe_filename = safe_filename.replace('\\', '')
    
    return safe_filename
```

## Data Protection

### Sensitive Data Handling
```python
# ❌ DON'T: Log sensitive data
logging.info(f"Processing with API key: {GEMINI_API_KEY}")

# ✅ DO: Mask sensitive data in logs
logging.info(f"Processing with API key: ***{GEMINI_API_KEY[-4:]}")
```

## Vulnerability Prevention

### Path Traversal Prevention (Future)
```python
def safe_file_read(filename: str, base_dir: Path) -> str:
    """Leitura segura de arquivos prevenindo path traversal"""
    file_path = (base_dir / filename).resolve()
    
    # Verificar que path final está dentro de base_dir
    if not str(file_path).startswith(str(base_dir.resolve())):
        raise ValueError(f"Acesso negado: {filename}")
    
    with open(file_path, 'r') as f:
        return f.read()
```

### Command Injection Prevention (Future)
```python
# ❌ DON'T: Use shell=True with user input
import subprocess
subprocess.run(f"convert {user_filename} output.jpg", shell=True)

# ✅ DO: Use list arguments
subprocess.run(["convert", sanitize_filename(user_filename), "output.jpg"])
```

### Deserialization Security (Future)
```python
import json

# ✅ DO: Safe JSON parsing
def safe_load_json(file_path: Path) -> Dict:
    """Carrega JSON de forma segura"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logging.error(f"JSON inválido em {file_path}: {e}")
        raise ValueError(f"Arquivo JSON malformado")

# ❌ DON'T: Use pickle com dados não confiáveis
# pickle.load() pode executar código arbitrário
```

## Security Checklist

### Before Deployment
- [ ] API keys em variáveis de ambiente (`.env`)
- [ ] `.env` no `.gitignore`
- [ ] Validação de inputs implementada
- [ ] Paths validados (prevenção de traversal)

### Code Review Security Focus
- [ ] Nenhuma credencial hardcoded
- [ ] Inputs validados antes de uso
- [ ] Outputs sanitizados/encoded

## Security Best Practices

### Secure Configuration (Future)
```python
# config.py
class SecurityConfig:
    """Configurações de segurança centralizadas"""
    
    # API
    API_TIMEOUT = 30  # segundos
    MAX_RETRIES = 3
    RATE_LIMIT_PER_MINUTE = 10
    
    # File Upload
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    MASK_SENSITIVE_DATA = True
```

---
*Security guidelines for Blind Style Model using GitHub Copilot*
