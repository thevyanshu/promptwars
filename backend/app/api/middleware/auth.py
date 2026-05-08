import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
import json
import os

# Initialize Firebase Admin SDK
firebase_creds_path = settings.FIREBASE_CREDENTIALS_PATH

try:
    if firebase_creds_path and os.path.exists(firebase_creds_path):
        cred = credentials.Certificate(firebase_creds_path)
        firebase_admin.initialize_app(cred)
    else:
        # Fallback to default credentials if running in GCP environment
        # Or mock for local dev if Firebase isn't configured
        firebase_admin.initialize_app()
except ValueError:
    # App already initialized
    pass
except Exception as e:
    print(f"Warning: Firebase Admin SDK initialization failed: {e}")

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Verify the Firebase JWT token and return the decoded token.
    For local MVP development, we'll allow a dummy token if Firebase isn't strictly configured.
    """
    token = credentials.credentials
    
    # --- Local Dev / MVP Override ---
    if token == "local-dev-token":
        return {"uid": "dummy-user-123"}
    # --------------------------------
    
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(decoded_token: dict = Security(verify_token)) -> str:
    """
    Dependency to get the current user's UID.
    """
    return decoded_token.get("uid")
