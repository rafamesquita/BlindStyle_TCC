"""
Configurações da aplicação BlindStyle API
Gerencia variáveis de ambiente e configurações globais
"""
from typing import Optional, List, Literal
from pydantic import Field, field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    """Configurações da aplicação com validação Pydantic"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )

# ========================================================================
# 🚀 Configurações da Aplicação
# ========================================================================

    APP_NAME: str = Field(default="BlindStyle API", description="Nome da aplicação")
    VERSION: str = Field(default="1.0.0", description="Versão da API")
    ENVIRONMENT: Literal["development", "staging", "production"] = Field(default="development")
    DEBUG: bool = Field(default=False)

    # URLs
    API_V1_PREFIX: str = Field(default="/api/v1", description="Prefixo da API v1")
    FRONTEND_URL: str = Field(default="http://localhost:3000")
    BACKEND_URL: str = Field(default="http://localhost:8000")

    # ========================================================================
    # 🔐 Segurança e JWT
    # ========================================================================

    SECRET_KEY: str = Field(default="your-secret-key-change-in-production-min-32-chars")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # Password hashing
    PASSWORD_MIN_LENGTH: int = Field(default=8, description="Tamanho mínimo da senha")
    BCRYPT_ROUNDS: int = Field(default=12, description="Rounds do bcrypt")

    # ========================================================================
    # 🗄️ Banco de Dados
    # ========================================================================

    DATABASE_URL: str = Field(default="sqlite:///./blindstyle.db")

    # Pool de conexões
    DB_POOL_SIZE: int = Field(default=5)
    DB_MAX_OVERFLOW: int = Field(default=10)
    DB_POOL_TIMEOUT: int = Field(default=30)
    DB_POOL_RECYCLE: int = Field(default=3600)
    DB_ECHO: bool = Field(default=False)

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Valida e ajusta a URL do banco de dados"""
        if not v:
            return "sqlite:///./blindstyle.db"
        
        # Corrige postgres:// para postgresql://
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql://", 1)
        
        return v

    # ========================================================================
    # 🌐 CORS
    # ========================================================================

    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:8080,http://localhost:5173"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True)
    CORS_ALLOW_METHODS: str = Field(default="*")
    CORS_ALLOW_HEADERS: str = Field(default="*")

    def get_cors_origins(self) -> List[str]:
        """Retorna lista de origens permitidas para CORS"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return []

    def get_cors_methods(self) -> List[str]:
        """Retorna lista de métodos permitidos para CORS"""
        if self.CORS_ALLOW_METHODS == "*":
            return ["*"]
        return [method.strip() for method in self.CORS_ALLOW_METHODS.split(",") if method.strip()]

    def get_cors_headers(self) -> List[str]:
        """Retorna lista de headers permitidos para CORS"""
        if self.CORS_ALLOW_HEADERS == "*":
            return ["*"]
        return [header.strip() for header in self.CORS_ALLOW_HEADERS.split(",") if header.strip()]

    # ========================================================================
    # 🔑 OAuth Providers
    # ========================================================================

    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = Field(default=None)
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(default=None)
    GOOGLE_REDIRECT_URI: Optional[str] = Field(default=None)

    # Microsoft OAuth
    MICROSOFT_CLIENT_ID: Optional[str] = Field(default=None)
    MICROSOFT_CLIENT_SECRET: Optional[str] = Field(default=None)
    MICROSOFT_REDIRECT_URI: Optional[str] = Field(default=None)
    MICROSOFT_TENANT: str = Field(default="common")

    # GitHub OAuth
    GITHUB_CLIENT_ID: Optional[str] = Field(default=None)
    GITHUB_CLIENT_SECRET: Optional[str] = Field(default=None)
    GITHUB_REDIRECT_URI: Optional[str] = Field(default=None)

    # Apple OAuth
    APPLE_CLIENT_ID: Optional[str] = Field(default=None)
    APPLE_TEAM_ID: Optional[str] = Field(default=None)
    APPLE_KEY_ID: Optional[str] = Field(default=None)
    APPLE_PRIVATE_KEY: Optional[str] = Field(default=None)
    APPLE_REDIRECT_URI: Optional[str] = Field(default=None)

    # ========================================================================
    # 🤖 AI Services
    # ========================================================================

    # Google Gemini
    GEMINI_API_KEY: Optional[str] = Field(default=None)
    GEMINI_MODEL: str = Field(default="gemini-pro")
    GEMINI_VISION_MODEL: str = Field(default="gemini-pro-vision")

    # OpenAI
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    OPENAI_MODEL: str = Field(default="gpt-4")
    OPENAI_VISION_MODEL: str = Field(default="gpt-4-vision-preview")

    # Google Cloud Vision
    GOOGLE_VISION_API_KEY: Optional[str] = Field(default=None)
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = Field(default=None)

    # Configurações gerais de IA
    AI_MAX_TOKENS: int = Field(default=1000)
    AI_TEMPERATURE: float = Field(default=0.7)
    AI_TIMEOUT: int = Field(default=30)

    # ========================================================================
    # 📁 Armazenamento de Arquivos
    # ========================================================================

    UPLOAD_DIR: str = Field(default="uploads")
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024)  # 10MB
    ALLOWED_EXTENSIONS: str = Field(default=".jpg,.jpeg,.png,.webp")

    def get_upload_path(self) -> Path:
        """Retorna o Path do diretório de upload"""
        path = Path(self.UPLOAD_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_allowed_extensions(self) -> List[str]:
        """Retorna lista de extensões permitidas"""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",") if ext.strip()]


    # ========================================================================
    # 📊 Logging
    # ========================================================================

    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO")
    LOG_FORMAT: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    LOG_FILE: Optional[str] = Field(default=None)

    # ========================================================================
    # ⚡ Rate Limiting
    # ========================================================================

    RATE_LIMIT_ENABLED: bool = Field(default=False)
    RATE_LIMIT_PER_MINUTE: int = Field(default=60)
    
    # ========================================================================
    # 🔧 Propriedades Computadas
    # ========================================================================

    @property
    def is_sqlite(self) -> bool:
        """Verifica se está usando SQLite"""
        return self.DATABASE_URL.startswith("sqlite")

    @property
    def is_postgres(self) -> bool:
        """Verifica se está usando PostgreSQL"""
        return self.DATABASE_URL.startswith("postgresql")

    @property
    def is_production(self) -> bool:
        """Verifica se está em produção"""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Verifica se está em desenvolvimento"""
        return self.ENVIRONMENT == "development"

    @property
    def google_oauth_enabled(self) -> bool:
        """Verifica se Google OAuth está configurado"""
        return all([
            self.GOOGLE_CLIENT_ID,
            self.GOOGLE_CLIENT_SECRET,
            self.GOOGLE_REDIRECT_URI
        ])

    @property
    def microsoft_oauth_enabled(self) -> bool:
        """Verifica se Microsoft OAuth está configurado"""
        return all([
            self.MICROSOFT_CLIENT_ID,
            self.MICROSOFT_CLIENT_SECRET,
            self.MICROSOFT_REDIRECT_URI
        ])

    @property
    def github_oauth_enabled(self) -> bool:
        """Verifica se GitHub OAuth está configurado"""
        return all([
            self.GITHUB_CLIENT_ID,
            self.GITHUB_CLIENT_SECRET,
            self.GITHUB_REDIRECT_URI
        ])

    @property
    def apple_oauth_enabled(self) -> bool:
        """Verifica se Apple OAuth está configurado"""
        return all([
            self.APPLE_CLIENT_ID,
            self.APPLE_TEAM_ID,
            self.APPLE_KEY_ID,
            self.APPLE_PRIVATE_KEY,
            self.APPLE_REDIRECT_URI
        ])

    @property
    def gemini_enabled(self) -> bool:
        """Verifica se Gemini está configurado"""
        return bool(self.GEMINI_API_KEY)

    @property
    def openai_enabled(self) -> bool:
        """Verifica se OpenAI está configurado"""
        return bool(self.OPENAI_API_KEY)

    @property
    def google_vision_enabled(self) -> bool:
        """Verifica se Google Vision está configurado"""
        return bool(self.GOOGLE_VISION_API_KEY or self.GOOGLE_APPLICATION_CREDENTIALS)

    @property
    def email_enabled(self) -> bool:
        """Verifica se email está configurado"""
        return all([
            self.SMTP_HOST,
            self.SMTP_USER,
            self.SMTP_PASSWORD,
            self.SMTP_FROM_EMAIL
        ])
    
    
    # ========================================================================
    # 🔧 Métodos Auxiliares
    # ========================================================================

    def get_oauth_providers(self) -> List[str]:
        """Retorna lista de OAuth providers habilitados"""
        providers = []
        if self.google_oauth_enabled:
            providers.append("google")
        if self.microsoft_oauth_enabled:
            providers.append("microsoft")
        if self.github_oauth_enabled:
            providers.append("github")
        if self.apple_oauth_enabled:
            providers.append("apple")
        return providers

    def get_ai_providers(self) -> List[str]:
        """Retorna lista de AI providers habilitados"""
        providers = []
        if self.gemini_enabled:
            providers.append("gemini")
        if self.openai_enabled:
            providers.append("openai")
        if self.google_vision_enabled:
            providers.append("google_vision")
        return providers

    def model_dump_safe(self) -> dict:
        """Retorna configurações sem dados sensíveis"""
        dump = self.model_dump()
        sensitive_keys = [
            "SECRET_KEY",
            "DATABASE_URL",
            "GEMINI_API_KEY",
            "OPENAI_API_KEY",
            "GOOGLE_VISION_API_KEY",
            "GOOGLE_CLIENT_SECRET",
            "MICROSOFT_CLIENT_SECRET",
            "GITHUB_CLIENT_SECRET",
            "APPLE_PRIVATE_KEY",
            "SMTP_PASSWORD",
        ]
        for key in sensitive_keys:
            if key in dump and dump[key]:
                dump[key] = "***HIDDEN***"
        return dump

# Instancia as configurações
settings = Settings()

    # ========================================================================
    # 🔍 Validação na inicialização
    # ========================================================================

def validate_settings():
    """Valida configurações críticas na inicialização"""
    import logging
    logger = logging.getLogger(__name__)

    errors = []
    warnings = []

    # Valida SECRET_KEY em produção
    if settings.is_production and len(settings.SECRET_KEY) < 32:
        errors.append("SECRET_KEY deve ter pelo menos 32 caracteres em produção")

    if settings.SECRET_KEY == "your-secret-key-change-in-production-min-32-chars":
        warnings.append("⚠️  Usando SECRET_KEY padrão - ALTERE EM PRODUÇÃO!")

    # Avisa se nenhum OAuth provider está configurado
    oauth_providers = settings.get_oauth_providers()
    if not oauth_providers:
        warnings.append("⚠️  Nenhum OAuth provider configurado")

    # Avisa se nenhum AI provider está configurado
    ai_providers = settings.get_ai_providers()
    if not ai_providers:
        warnings.append("⚠️  Nenhum AI provider configurado")

    # Exibe erros
    if errors:
        for error in errors:
            logger.error(f"❌ {error}")
        raise ValueError(f"Erros de configuração encontrados")

    # Exibe warnings
    for warning in warnings:
        logger.warning(warning)

    # Sucesso
    logger.info("✅ Configurações validadas com sucesso")
    logger.info(f"📍 Ambiente: {settings.ENVIRONMENT}")
    logger.info(f"💾 Banco: {'SQLite' if settings.is_sqlite else 'PostgreSQL'}")

    if oauth_providers:
        logger.info(f"🔑 OAuth: {', '.join(oauth_providers)}")

    if ai_providers:
        logger.info(f"🤖 AI: {', '.join(ai_providers)}")

    # Valida apenas se não for em modo de importação de módulos
    try:
        if __name__ != "__main__":
            validate_settings()
    except Exception as e:
        import logging
        logging.warning(f"Não foi possível validar configurações: {e}")