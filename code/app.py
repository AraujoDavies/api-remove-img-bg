import base64
import logging
from typing import List, Union

from fastapi import Body, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError, ValidationException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from rembg import remove
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from pathlib import Path


logging.basicConfig(
    level=logging.CRITICAL,
    encoding="utf-8",
    format="%(asctime)s - %(levelname)s: %(message)s",
)


class ValidationErrorItem(BaseModel):
    loc: List[Union[str, int]]
    msg: str
    type: str


class CustomValidationErrorResponse(BaseModel):
    success: bool = False
    status: int = 422
    error_message: str = "detail error"
    # debug: List[ValidationErrorItem]


app = FastAPI(title="API Remove BG", description="Remove background of any image")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "status": exc.status_code,
            "error_message": exc.detail,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_message = "Validation error"
    if errors[0]["msg"] == "Field required":
        error_message = "Validation error - Field required."

    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "status": HTTP_422_UNPROCESSABLE_ENTITY,
            "error_message": error_message,
        },
    )


@app.get("/", summary="index html")
def index():
    html_path = Path(__file__).parent / "index.html"
    with open(html_path, "r") as f:
        html = f.read()
    return HTMLResponse(content=html)


@app.post(
    "/upload-file",
    summary="Upload file and return HTML that contains img new and old",
    responses={
        200: {
            "description": "Removed bg success",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "before_url": "input_base64",
                        "after_url": "output_base64",
                    }
                }
            },
        },
        415: {
            "description": "File invalid",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "status": 415,
                        "error_message": "detail error",
                    }
                }
            },
        },
        422: {
            "model": CustomValidationErrorResponse,
            "description": "Validation Error",
        },
        500: {
            "description": "Some error in process",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "status": 500,
                        "error_message": "Internal server error",
                    }
                }
            },
        },
    },
)
async def create_upload_file(file: UploadFile = File(...)):
    # verfy content type
    if file.content_type not in ["image/png", "image/jpeg"]:
        raise HTTPException(status_code=415, detail="Only accept .png or .jpg")

    # size can't be too big
    max_kb_accept = 50000  # KB
    accept_size = max_kb_accept * 1024  # convert to bytes

    if file.size > accept_size:
        raise HTTPException(
            status_code=415, detail=f"file size is bigger than {max_kb_accept}KB"
        )

    try:
        # remove bg, convert both images to base64 and return this in HTML.
        input_bytes = await file.read()
        output_bytes = remove(input_bytes)

        input_b64 = base64.b64encode(input_bytes).decode("utf-8")
        output_b64 = base64.b64encode(output_bytes).decode("utf-8")

        return JSONResponse(
            content={
                "success": True,
                "before_url": f"data:image/png;base64,{input_b64}",
                "after_url": f"data:image/png;base64,{output_b64}",
            }
        )
    except Exception as error:
        logging.critical(error)
        raise HTTPException(status_code=500, detail="Internal server error")
