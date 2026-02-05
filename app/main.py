from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.auth.auth import auth_router
from app.post.posts import post_router
from app.likes.likes import like_router


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
