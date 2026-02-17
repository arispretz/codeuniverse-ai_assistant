import os
import json
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import Header, HTTPException

# Only initialize Firebase if not in test mode
if os.getenv("TEST_MODE") != "true":
    firebase_credentials = os.environ.get("FIREBASE_CREDENTIAL_JSON")

    if not firebase_credentials:
        raise RuntimeError("Missing FIREBASE_CREDENTIAL_JSON environment variable")

    try:
        # Parse the JSON string directly from the environment variable
        cred_dict = json.loads(firebase_credentials)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase initialized")
    except json.JSONDecodeError:
        raise RuntimeError("Invalid FIREBASE_CREDENTIAL_JSON: not valid JSON")

def verify_token(authorization: str = Header(...)):
    """
    Verify Firebase authentication token.
    In test mode, accepts any token and returns a fake user.
    """
    if os.getenv("TEST_MODE") == "true":
        return {"uid": "test_user", "email": "test@example.com"}

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")

    token = authorization.split(" ")[1]
    try:
        decoded = auth.verify_id_token(token)
        return decoded
    except Exception as e:
        print("❌ Firebase token verification failed:", e)
        raise HTTPException(status_code=401, detail="Invalid or expired token")

