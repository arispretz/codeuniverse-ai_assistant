# Project AI Assistant

FastAPI-based AI Assistant for the Collaboration Platform.  
Provides code generation, error detection, and optimization suggestions using deep learning models.

---

## 🔗 Associated Repositories

- [Frontend (codeuniverse-frontend)](https://github.com/arispretz/codeuniverse-frontend.git)
- [Backend (codeuniverse-backend)](https://github.com/arispretz/codeuniverse-backend.git)
- [Codeuniverse-App (codeuniverse-app)](https://github.com/arispretz/codeuniverse-app.git)

---

## Features
- Code generation from natural language prompts
- Smart autocompletion
- Error detection and debugging suggestions
- Performance and readability optimization
- Integration with frontend via REST API

---

## Tech Stack
- FastAPI
- PyTorch
- Judge0 API

---

## Installation
```bash
git clone https://github.com/arispretz/codeuniverse-demo-ai_assistant.git
cd codeuniverse-demo-ai_assistant
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
`````

---

## 🔑 Environment Variables
See .env.example for required variables.

---

## 🚀 Deployment
Hugging Face Spaces: Currently deployed as a FastAPI service.
Local Development / Docker Compose: Dockerfiles are included for integration with the frontend and backend.

---

## 🐳 Docker Usage
### Development
Intended for local development with the **monorepo (`codeuniverse`)**, where the `ai_assistant` folder is part of the overall project structure.  
In this case, the `WORKDIR` is `/app/ai_assistant` and the application runs on port **8000**:

```bash
docker build -f dockerfile.dev -t ai-assistant-dev .
docker run -p 8000:8000 ai-assistant-dev

`````

### Production
Intended for deployment on Hugging Face Spaces or when cloning only the standalone repository codeuniverse-demo-ai_assistant.
Here, the WORKDIR is /app and the application runs on port 7860 (required by HF Spaces):

```bash
docker build -f dockerfile.prod -t ai-assistant-prod .
docker run -p 7860:7860 ai-assistant-prod
`````

ℹ️ **Note:**  
- Use the *Development* configuration if you are working locally with the full monorepo.
- Use the *Production* configuration if you are working with the isolated ai_assistant repo or deploying to Hugging Face Spaces.

---

## 📜 License
Apache 2.0

---

