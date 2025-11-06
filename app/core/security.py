from typing import Optional
from fastapi import HTTPException, status, Depends, Header 

def get_current_user_id(
    
    user_id_from_header: Optional[str] = Header(None, alias="user-id")
) -> int:
    """
    Gets the user ID directly from the header
    that the API gateway (KrakenD) sets upon
    successful authentication.

    KrakenD adds the header: "user-id: 1"
    """
    
    if user_id_from_header is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID header not found. Access denied."
        )
        
    try:
        user_id = int(user_id_from_header)
        return user_id
    except ValueError:
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid User ID format in header: '{user_id_from_header}'"
        )

