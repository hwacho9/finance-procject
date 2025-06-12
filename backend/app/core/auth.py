import os
import json
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import credentials, auth
import logging

logger = logging.getLogger(__name__)


# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if firebase_admin._apps:
        return

    # Try to get service account from environment variable
    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    project_id = os.getenv("FIREBASE_PROJECT_ID")

    if not service_account_json:
        logger.error(
            "FIREBASE_SERVICE_ACCOUNT_JSON is not set. "
            "Firebase Admin SDK could not be initialized."
        )
        return

    try:
        service_account_info = json.loads(service_account_json)
        cred = credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(cred, {"projectId": project_id})
        logger.info(
            f"Firebase Admin SDK initialized successfully for project ID: {project_id}"
        )
    except Exception as e:
        logger.error(
            f"Failed to initialize Firebase Admin SDK from service account: {e}"
        )
        raise


# Initialize Firebase on module import
initialize_firebase()

# Security scheme
security = HTTPBearer()


class FirebaseUser:
    """Firebase user information"""

    def __init__(
        self, uid: str, email: Optional[str] = None, name: Optional[str] = None
    ):
        self.uid = uid
        self.email = email
        self.name = name


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> FirebaseUser:
    """
    Verify Firebase ID token and return current user
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not firebase_admin._apps:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Firebase is not initialized on the server.",
        )
    try:
        # Verify the ID token
        decoded_token = auth.verify_id_token(credentials.credentials)

        # Extract user information
        uid = decoded_token.get("uid")
        email = decoded_token.get("email")
        name = decoded_token.get("name")

        if not uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
            )

        return FirebaseUser(uid=uid, email=email, name=name)

    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid ID token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired ID token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Error verifying token: {e}")

        # For development: Allow bypassing with special dev token
        if (
            os.getenv("DEBUG", "false").lower() == "true"
            and credentials.credentials == "dev-token"
        ):
            logger.warning("Using development bypass token")
            return FirebaseUser(
                uid="dev-user-123", email="dev@example.com", name="Development User"
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Optional dependency for endpoints that can work with or without auth
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[FirebaseUser]:
    """
    Optional authentication - returns None if no token provided
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
