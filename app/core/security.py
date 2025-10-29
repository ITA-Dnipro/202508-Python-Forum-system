"""
Mock JWT authentication for educational purposes.
In production, this would validate real JWT tokens from an auth service.
"""
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Simple Bearer token scheme
security = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """
    Extract user ID from JWT token.
    
    For this educational MVP, we'll use a simple mock:
    - If token is present, extract a fake user_id
    - In production, you'd decode and validate the JWT
    
    Example token format: "Bearer user_123"
    This extracts "123" as the user_id.
    """
    token = credentials.credentials
    
    # Mock: Extract user_id from token (format: "user_123")
    if token.startswith("user_"):
        try:
            user_id = int(token.split("_")[1])
            return user_id
        except (IndexError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format. Use 'user_<id>' (e.g., 'user_123')",
            )
    
    # If you want to implement real JWT validation:
    # from jose import jwt, JWTError
    # try:
    #     payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    #     user_id: int = payload.get("user_id")
    #     if user_id is None:
    #         raise HTTPException(status_code=401, detail="Invalid token")
    #     return user_id
    # except JWTError:
    #     raise HTTPException(status_code=401, detail="Could not validate token")
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
    )