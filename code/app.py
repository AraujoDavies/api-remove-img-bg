from fastapi import FastAPI, UploadFile, File,  HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from rembg import remove
import base64
import logging

logging.basicConfig(
    level=logging.CRITICAL,
    encoding="utf-8",
    format="%(asctime)s - %(levelname)s: %(message)s"
)

app = FastAPI(escription="Remove background of any image" )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "status_code": exc.status_code, "error_message": exc.detail},
    )


@app.post('/upload-file')
async def create_upload_file(file: UploadFile = File(...)):
    try:
        # PNG or JPG
        extensao = file.filename.lower()[-4:]
        if extensao != '.png' and extensao != '.jpg':
            raise HTTPException(status_code=415, detail="Only accept .png or .jpg")
        
        # size can't be too big
        max_kb_accept = 500 # KB
        accept_size = max_kb_accept * 1024 # convert to bytes

        if file.size > accept_size:
            raise HTTPException(status_code=415, detail=f"file size is bigger than {max_kb_accept}KB")
    
        # remove bg, convert both images to base64 and return this in HTML.
        input_bytes = await file.read()
        output_bytes = remove(input_bytes)

        input_b64 = base64.b64encode(input_bytes).decode("utf-8")
        output_b64 = base64.b64encode(output_bytes).decode("utf-8")

        html_content = f"""
        <html>
            <body>
                <h2>Original Image</h2>
                <img src="data:image/png;base64,{input_b64}" style="max-width: 400px;"/>
                <h2>Background Removed</h2>
                <img src="data:image/png;base64,{output_b64}" style="max-width: 400px;"/>

                <a href="data:image/png;base64,{output_b64}" download="output.png">
                    <button style="padding: 10px 20px; font-size: 16px;">Download Image</button>
                </a>
            </body>
        </html>
        """
        return JSONResponse(content={"success": True, 'html': html_content})
        return HTMLResponse(content= html_content)
    except Exception as error:
        logging.critical(error)
        raise HTTPException(status_code=500, detail="Server error")