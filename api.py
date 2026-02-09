from email.mime import text
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from httpcore import request

from engine import speak   

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@app.post("/speak", response_class=HTMLResponse)


def generate_speech(request: Request, text: str = Form(...)):
    try:
        result = speak(text)
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "emotion": result["emotion"],
                "intensity": result["intensity"],
                "latency_ms": result.get("latency_ms"), 
                "audio_file": result["file"]
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": str(e)}
        )