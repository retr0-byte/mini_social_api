from fastapi import HTTPException

class AppError(HTTPException):
    status_code: int = 400
    detail: str = "Application error"

    def __init__(self, detail: str | None = None):
        super().__init__(
            status_code=self.status_code,
            detail=detail or self.detail,
        )