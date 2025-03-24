from fastapi import APIRouter, Depends, HTTPException, Security, status

from app.v1.auth.schemas.api_key import CreateAPIKeyResponse, CreateAPIKeyRequest
from app.v1.auth.services.api_keys import APIKeysService
from app.v1.dependencies import get_api_keys_service, verify_jwt_authorization
from app.v1.schemas import AccessScope


router = APIRouter()


@router.post(
    "/",
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN])],
    response_model=CreateAPIKeyResponse,
    status_code=status.HTTP_201_CREATED
)
def create_api_key(
    api_key: CreateAPIKeyRequest,
    api_keys_service: APIKeysService = Depends(get_api_keys_service)
):
    try:
        (api_key_string, created_api_key) = api_keys_service.create_api_key(name=api_key.name)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='API key already exists')
    return CreateAPIKeyResponse(
        api_key_id=created_api_key.api_key_id,
        name=created_api_key.name,
        api_key=api_key_string,
        created_at=created_api_key.created_at,
        updated_at=created_api_key.updated_at
    ) 