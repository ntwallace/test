from typing import Final, Literal
from uuid import uuid4
from fastapi import FastAPI, Request, Response
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from app.px.pxlogger import PxContext, PxLogger, PxNote
from app.internal.router import router as internal_router
from app.v1.router import router as v1_router
from app.v3_adapter.router import router as v3_adapter_router


_logger: Final = PxLogger(__name__)

app: Final = FastAPI(
    title='powerx-api'
)


@app.middleware('http')
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        _logger.error(
            PxNote("Uncaught exception found"),
            exc_info=e,
        )
        return Response("Internal server error", status_code=500)


@app.middleware('http')
async def logger_context_middleware(request: Request, call_next):
    _logger.alter_context(PxContext.set_empty())
    with _logger.with_context(
        PxContext.request().as_managed(str(uuid4())),
        PxContext("url").as_managed(str(request.url)),
        PxContext("method").as_managed(str(request.method)),
        PxContext("query_params").as_managed({k: v for k,v in request.query_params.items()}),
    ):
        return await call_next(request)


app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/status/alive')
def get_status_alive() -> Literal[True]:
    return True

@app.get('/status/ready')
def get_status_ready() -> Literal[True]:
    return True


app.include_router(v1_router, prefix='/v1')
app.include_router(v3_adapter_router, prefix='/v3')
app.include_router(internal_router, prefix='/internal')
