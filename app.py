import os
import time
import traceback
import uvicorn
import logging
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from models import CodePrompt, CodeRequest, CodeInput
from ml_engine import (
    generate_code, generate_reply, generate_reply_code_only, _load_model, autocomplete_code
)
from db import connect_db, close_db
from auth import verify_token

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env.test"))
print("TEST_MODE =", os.getenv("TEST_MODE"))

logging.basicConfig(
    level=logging.DEBUG,  
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

app = FastAPI(
    title="Code Assistant API",
    description="FastAPI backend for code assistant",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/")
def root():
    return {"message": "Code Assistant API is running"}

@app.get("/health")
def health():
    try:
        _load_model()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.on_event("startup")
def startup_event():
    _load_model()
    logging.info("✅ Model preloaded")
    connect_db()
    logging.info("✅ MongoDB connection established")

@app.on_event("shutdown")
def shutdown_event():
    close_db()
    logging.info("🛑 MongoDB connection closed")

if __name__ == "__main__": 
    port = int(os.environ.get("PORT", 7860)) 
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)

# -------------------------------
# Group all routes under /api/assistant
# -------------------------------
assistant_router = APIRouter(prefix="/api/assistant")

@assistant_router.post("/generate")
async def generate(data: CodePrompt, user=Depends(verify_token)):
    try:
        code = generate_code(data.prompt, data.language)
        return {"code": code}
    except Exception as e:
        logging.error("Error in /generate: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@assistant_router.post("/autocomplete")
async def autocomplete(data: CodeInput, user=Depends(verify_token)):
    try:
        suggestion = autocomplete_code(data.code, data.language)
        return {"suggestion": suggestion}
    except Exception as e:
        logging.error("Error in /autocomplete: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@assistant_router.post("/reply")
async def reply(data: CodeRequest, user=Depends(verify_token)):
    try:
        logging.debug("Payload received: %s", data.dict()) 
        logging.debug("User: %s", user)

        start = time.time()
        response = generate_reply(
            data.prompt,
            data.language,
            data.code,
            data.user_id or user.get("uid", "unknown"),
            data.user_level
        )
        logging.debug("Model response: %s", response)

        duration = time.time() - start
        if not response or response.startswith("⚠️") or response.startswith("❌"):
            return {"reply": "⚠️ Unable to generate explanation, please try again."}

        return {"reply": response, "duration": duration}
    except Exception as e:
        logging.error("Error in /reply: %s", e)
        logging.error(traceback.format_exc())
        return {"reply": f"⚠️ Internal assistant error ({str(e)})"}

@assistant_router.post("/reply-code-only")
async def reply_code_only(data: CodeRequest, user=Depends(verify_token)):
    try:
        logging.debug("Payload received: %s", data.dict()) 
        logging.debug("User: %s", user)

        start = time.time()
        response = generate_reply_code_only(
            data.prompt,
            data.language,
            data.code,
            data.user_id or user.get("uid", "unknown")
        )
        logging.debug("Model response: %s", response)

        duration = time.time() - start
        if not response or response.startswith("⚠️") or response.startswith("❌"):
            return {"code": "⚠️ Unable to generate valid code."}

        return {"code": response, "duration": duration}
    except Exception as e:
        logging.error("Error in /reply-code-only: %s", e)
        logging.error(traceback.format_exc())
        return {"code": f"⚠️ Internal assistant error ({str(e)})"}

app.include_router(assistant_router)
