import os
import time
import traceback
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from models import CodePrompt, CodeRequest, CodeInput
from ml_engine import (
    generate_code, generate_reply, generate_reply_code_only, _load_model, autocomplete_code
)
from db import connect_db, close_db
from auth import verify_token
from dotenv import load_dotenv
import logging

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env.test"))
print("TEST_MODE =", os.getenv("TEST_MODE"))

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]  
)

app = FastAPI()

allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    print("✅ Model preloaded")
    connect_db()
    print("✅ MongoDB connection established")

@app.on_event("shutdown")
def shutdown_event():
    close_db()
    print("🛑 MongoDB connection closed")

if __name__ == "__main__": 
    port = int(os.environ.get("PORT", 7860)) 
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)

@app.post("/generate")
async def generate(data: CodePrompt, user=Depends(verify_token)):
    """
    Generate code snippet based on a given prompt.

    Args:
        data (CodePrompt): Prompt and language information.
        user (dict): Authenticated user information.

    Returns:
        dict: Generated code snippet.
    """
    try:
        code = generate_code(data.prompt, data.language)
        return {"code": code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/autocomplete")
async def autocomplete(data: CodeInput, user=Depends(verify_token)):
    try:
        suggestion = autocomplete_code(data.code, data.language)
        return {"suggestion": suggestion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reply")
async def reply(data: CodeRequest, user=Depends(verify_token)):
    """
    Generate mentor-style explanation for provided code.

    Args:
        data (CodeRequest): Prompt, language, code, and user information.
        user (dict): Authenticated user information.

    Returns:
        dict: Explanation reply and duration.
    """
    try:
        logging.debug("Payload received: %s", data.dict()) 
        logging.debug("User: %s", user)

        start = time.time()
        response = generate_reply(
            data.prompt,
            data.language,
            data.code,
            user["uid"],
            data.user_level
        )
        
        logging.debug("Model response: %s", response)

        duration = time.time() - start

        if not response or response.startswith("⚠️") or response.startswith("❌"):
            return {"reply": "⚠️ Unable to generate explanation, please try again."}

        return {"reply": response, "duration": duration}
    except Exception as e:
        print("Error in /reply:", traceback.format_exc())
        return {"reply": f"⚠️ Internal assistant error ({str(e)})"}

@app.post("/reply-code-only")
async def reply_code_only(data: CodeRequest, user=Depends(verify_token)):
    """
    Generate code-only response for a given prompt.

    Args:
        data (CodeRequest): Prompt, language, code, and user information.
        user (dict): Authenticated user information.

    Returns:
        dict: Generated code and duration.
    """
    try:
        logging.debug("Payload received: %s", data.dict()) 
        logging.debug("User: %s", user)

        start = time.time()
        response = generate_reply_code_only(
            data.prompt,
            data.language,
            data.code,
            user["uid"]
        )

        logging.debug("Model response: %s", response)
        
        duration = time.time() - start

        if not response or response.startswith("⚠️") or response.startswith("❌"):
            return {"code": "⚠️ Unable to generate valid code."}

        return {"code": response, "duration": duration}
    except Exception as e:
        print("Error in /reply-code-only:", traceback.format_exc())
        return {"code": f"⚠️ Internal assistant error ({str(e)})"}

