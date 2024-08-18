from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import UserLogin
from ..models import User
from .. import utils, oauth2

router = APIRouter(tags=["Auth"])


@router.post("/login")
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # OAuth2PasswordRequestForm returns username & password as a dict
    fetched_user = (
        db.query(User).filter(User.email == user_credentials.username).first()
    )
    if fetched_user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credential"
        )
    if not utils.verify(user_credentials.password, fetched_user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )
    access_token = oauth2.create_access_token(data={"user_id": fetched_user.id})

    return {"token": access_token, "token_type": "bearer"}
