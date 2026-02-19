from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.base_exception import AppError
from app.auth.router import auth_router
from app.post.router import post_router
from app.likes.router import like_router

app = FastAPI(
    docs_url="/api/docs", openapi_url="/api"
)

app.include_router(auth_router)
app.include_router(post_router)
app.include_router(like_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "status": "error",
            "error": {
                "code": "VALIDATION_ERROR",
                "details": exc.errors(),
            }
        },
    )


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code,
                        content={
                            "status": "error",
                            "error": {
                                "detail": exc.detail,
                            }
                        })
