from typing import Generator
from contextlib import contextmanager
import logging

from sqlalchemy import create_engine, event, pool, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from src.core.config.settings import settings
from src.models.base import Base

logger = logging.getLogger(__name__)


POOL_SETTINGS = {
    "pool_size": settings.DB_POOL_SIZE,
    "max_overflow": settings.DB_MAX_OVERFLOW,
    "pool_timeout": settings.DB_POOL_TIMEOUT,
    "pool_recycle": settings.DB_POOL_RECYCLE,
    "pool_pre_ping": True,
}

engine = create_engine(settings.DATABASE_URL, echo=settings.DB_ECHO or settings.DEBUG, future=True, **POOL_SETTINGS)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, class_=Session)

# ============================================================================
# Dependency Injection para FastAPI
# ============================================================================

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Erro na sessão do banco: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# ============================================================================
# Context Manager para transações (uso em serviços)
# ============================================================================

@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Erro na transação: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# ============================================================================
# Funções de gerenciamento do banco
# ============================================================================

def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas criadas com sucesso")
    except SQLAlchemyError as e:
        logger.error(f"Erro ao criar tabelas: {e}")
        raise

def drop_tables():
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("Todas as tabelas foram removidas")
    except SQLAlchemyError as e:
        logger.error(f"Erro ao remover tabelas: {e}")
        raise

def check_connection() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Conexão com banco de dados: OK")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Falha na conexão com banco: {e}")
        return False

def get_db_info() -> dict:
    return {
        "pool_size": engine.pool.size(),
        "checked_in": engine.pool.checkedin(),
        "checked_out": engine.pool.checkedout(),
        "overflow": engine.pool.overflow(),
        "total": engine.pool.size() + engine.pool.overflow()
    }

# ============================================================================
# Inicialização
# ============================================================================

def init_db():
    logger.info("Inicializando banco de dados...")

    if not check_connection():
        raise ConnectionError("Não foi possível conectar ao banco de dados")

    if settings.DEBUG:
        logger.warning("Modo DEBUG: criando tabelas automaticamente")
        create_tables()

    logger.info("Banco de dados inicializado com sucesso")

# ============================================================================
# Cleanup
# ============================================================================

def close_db():
    logger.info("Fechando conexões do banco de dados...")
    engine.dispose()
    logger.info("Conexões fechadas")