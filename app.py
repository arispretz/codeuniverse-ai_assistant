from fastapi import FastAPI, APIRouter

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Code Assistant API is running"}

@app.get("/ping")
def ping():
    return {"message": "pong"}

assistant_router = APIRouter(prefix="/api/assistant")

@assistant_router.get("/test")
def test():
    return {"message": "assistant route works"}

app.include_router(assistant_router)
