from fastapi import APIRouter

from app.v1.auth.routers import access_roles, api_keys, auth, users


router = APIRouter(tags=['auth'])

router.include_router(auth.router)
router.include_router(access_roles.router, prefix='/access-roles')
router.include_router(api_keys.router, prefix='/api-keys')
router.include_router(users.router, prefix='/users')
