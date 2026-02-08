from app.core.base_exception import AppError


class PostDoesNotExist(AppError):
    status_code = 404
    detail = "Post does not exist"

class PostUpdateForbidden(AppError):
    status_code = 403
    detail = "You are not allowed to update a post"