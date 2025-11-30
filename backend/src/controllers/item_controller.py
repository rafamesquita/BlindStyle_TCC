from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from src.app_services.item_app_service import ItemAppService
from src.schemas.item import (
    ItemCreate,
    ItemUpdate,
    ItemStatusUpdate,
    Item,
    ItemList,
    ItemStatus,
)
from src.core.dependencies import get_current_user, get_item_app_service
from src.schemas.user import User

router = APIRouter(prefix="/items", tags=["items"])

@router.post("create", response_model=Item)
async def create_item(item: ItemCreate, current_user: User = Depends(get_current_user), app_service: ItemAppService = Depends(get_item_app_service)):
    try:
        return app_service.create_item(current_user.id, item)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("list/{item_id}", response_model=Item)
async def get_item(item_id: int = Path(..., description="ID do item"), current_user: User = Depends(get_current_user), app_service: ItemAppService = Depends(get_item_app_service), allow_others: bool = Query(False, description="Permite ver itens de outros usuários")):
    try:
        return app_service.get_item(item_id, current_user.id, allow_others)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("list-all", response_model=ItemList)
async def list_items(
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(10, ge=1, le=100, description="Itens por página"),
    status: Optional[ItemStatus] = Query(ItemStatus.ACTIVE, description="Status dos itens"),
    category: Optional[str] = Query(None, description="Categoria dos itens"),
    current_user: User = Depends(get_current_user),
    app_service: ItemAppService = Depends(get_item_app_service)
):
    try:
        return app_service.list_user_items(current_user.id, page=page, size=size, status=status, category=category)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("update/{item_id}", response_model=Item)
async def update_item(
    item_update: ItemUpdate,
    item_id: int = Path(..., description="ID do item"),
    current_user: User = Depends(get_current_user),
    app_service: ItemAppService = Depends(get_item_app_service)
):
    try:
        return app_service.update_item(item_id, current_user.id, item_update)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("update-status/{item_id}/status", response_model=Item)
async def update_item_status(
    status_update: ItemStatusUpdate,
    item_id: int = Path(..., description="ID do item"),
    current_user: User = Depends(get_current_user),
    app_service: ItemAppService = Depends(get_item_app_service)
):
    try:
        return app_service.update_item_status(item_id, current_user.id, status_update)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("delete/{item_id}")
async def delete_item(
    item_id: int = Path(..., description="ID do item"),
    permanent: bool = Query(False, description="Remove permanentemente o item"),
    current_user: User = Depends(get_current_user),
    app_service: ItemAppService = Depends(get_item_app_service)
):
    try:
        return app_service.delete_item(item_id, current_user.id, permanent)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

