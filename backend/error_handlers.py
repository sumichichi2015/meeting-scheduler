from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette.requests import Request

class CustomError(Exception):
    def __init__(self, code: int, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}

async def custom_error_handler(request: Request, exc: CustomError):
    return JSONResponse(
        status_code=exc.code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "path": request.url.path
            }
        }
    )

class MeetingNotFoundError(CustomError):
    def __init__(self, meeting_id: str):
        super().__init__(
            code=404,
            message=f"会議 ID {meeting_id} が見つかりません",
            details={"meeting_id": meeting_id}
        )

class ValidationError(CustomError):
    def __init__(self, message: str, field_errors: dict = None):
        super().__init__(
            code=400,
            message=message,
            details={"field_errors": field_errors or {}}
        )
