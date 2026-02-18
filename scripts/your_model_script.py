from fastapi import FastAPI
from pydantic import BaseModel
from ml_engine import generate_reply

app = FastAPI()

class CodeRequest(BaseModel):
    """
    Model representing a request to generate a mentor-style reply.

    Attributes:
        prompt (str): Task description or user question.
        language (str): Programming language of the code.
        code (str): Code snippet provided by the user.
        user_id (str): Identifier for the user.
    """
    prompt: str
    language: str
    code: str
    user_id: str

@app.post("/reply")
async def reply(data: CodeRequest):
    """
    Endpoint to generate a mentor-style reply for a given code snippet.

    Args:
        data (CodeRequest): Request containing prompt, language, code, and user ID.

    Returns:
        dict: Generated reply from the model.
    """
    response = generate_reply(data.prompt, data.language, data.code, data.user_id)
    return {"reply": response}
