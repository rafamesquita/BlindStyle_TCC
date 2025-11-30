from dependency_injector import containers, providers

from src.services.ai_service import AIService

from src.repositories.user_repository import UserRepository
from src.repositories.item_repository import ItemRepository

from src.services.item_service import ItemService
from src.services.user_service import UserService
from src.services.auth_service import AuthService
from src.services.image_service import ImageService
from src.services.file_service import FileService

from src.app_services.description_app_service import DescriptionAppService
from src.app_services.user_app_service import UserAppService
from src.app_services.item_app_service import ItemAppService
from src.app_services.suggestion_app_service import SuggestionAppService

# Importar componentes ML/AI
from modules.vector_db import VectorDB
from modules.embeddings import EmbeddingGenerator
from modules.feature_extractor import FeatureExtractor
from modules.pytorch_model import ModelPredictor
from modules.model_input import ModelInputBuilder

class Container(containers.DeclarativeContainer):

    wiring_config = containers.WiringConfiguration(modules=[])
    config = providers.Configuration()

    # ---------------- Repositórios ----------------
    user_repository = providers.Factory(UserRepository, db=providers.Dependency())
    item_repository = providers.Factory(ItemRepository, db=providers.Dependency())

    # ---------------- ML/AI Components (Singletons) ----------------
    vector_db = providers.Singleton(VectorDB)
    
    feature_extractor = providers.Singleton(FeatureExtractor)
    
    embedding_generator = providers.Singleton(
        EmbeddingGenerator,
        vector_db=vector_db
    )
    
    model_predictor = providers.Singleton(
        ModelPredictor,
        checkpoint_path="../checkpoints/best_model.pth",
        device=None,  # Auto-detect (CPU or CUDA)
        config=None   # Use defaults
    )
    
    model_input_builder = providers.Singleton(
        ModelInputBuilder,
        max_items=5,
        embedding_dim=96
    )

    # ---------------- Services ----------------
    user_service = providers.Factory(UserService, user_repository=user_repository)
    
    item_service = providers.Factory(
        ItemService, 
        repository=item_repository,
        vector_db=vector_db,
        embedding_generator=embedding_generator
    )
    
    auth_service = providers.Factory(AuthService, user_repository=user_repository)
    
    image_service = providers.Factory(ImageService)
    
    file_service = providers.Factory(FileService)
    
    ai_service = providers.Singleton(
        AIService,
        feature_extractor=feature_extractor,
        file_service=file_service,
        image_service=image_service
    )

    # ---------------- App Services ----------------
    user_app_service = providers.Factory(
        UserAppService, 
        user_service=user_service, 
        auth_service=auth_service
    )
    
    item_app_service = providers.Factory(
        ItemAppService, 
        item_service=item_service
    )
    
    description_app_service = providers.Factory(
        DescriptionAppService, 
        image_service=image_service, 
        ai_service=ai_service
    )
    
    suggestion_app_service = providers.Factory(
        SuggestionAppService,
        db=providers.Dependency(),
        vector_db=vector_db,
        model_predictor=model_predictor,
        model_input_builder=model_input_builder
    )