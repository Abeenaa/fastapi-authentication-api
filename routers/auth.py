import random
from hashlib import sha256
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import get_current_user
from app.database import get_db
from utils.rate_limit import rate_limiter
from utils.hashing import hash_password, verify_password
from utils.jwt import create_access_token, create_refresh_token, decode_refresh_token

router = APIRouter(tags=["auth"])

@router.post(
    "/register",
    response_model=schemas.RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limiter(10, 60, "register"))],
)
def register(user: schemas.RegisterRequest, db: Session = Depends(get_db)):

    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    hashed_password = hash_password(user.password)
    new_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


@router.post(
    "/login",
    response_model=schemas.LoginResponse,
    dependencies=[Depends(rate_limiter(10, 60, "login"))],
)
def login(credentials: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    refresh_payload = decode_refresh_token(refresh_token)
    exp = refresh_payload.get("exp")
    user.refresh_token_hash = sha256(refresh_token.encode("utf-8")).hexdigest()
    user.refresh_token_expires_at = datetime.utcfromtimestamp(exp) if exp else None
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=schemas.LoginResponse)
def refresh_token(payload: schemas.RefreshRequest, db: Session = Depends(get_db)):
    try:
        decoded = decode_refresh_token(payload.refresh_token)
        user_id = int(decoded.get("sub"))
    except (JWTError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user = db.query(models.User).filter(models.User.id == user_id).first()
    incoming_hash = sha256(payload.refresh_token.encode("utf-8")).hexdigest()

    if not user or user.refresh_token_hash != incoming_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if not user.refresh_token_expires_at or user.refresh_token_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )

    access_token = create_access_token({"sub": str(user.id)})
    new_refresh_token = create_refresh_token({"sub": str(user.id)})
    refresh_payload = decode_refresh_token(new_refresh_token)
    exp = refresh_payload.get("exp")

    user.refresh_token_hash = sha256(new_refresh_token.encode("utf-8")).hexdigest()
    user.refresh_token_expires_at = datetime.utcfromtimestamp(exp) if exp else None
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.delete("/delete-account", response_model=schemas.MessageResponse)
def delete_account(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.delete(current_user)
    db.commit()
    return {"message": "Account deleted successfully"}


@router.post("/logout", response_model=schemas.MessageResponse)
def logout(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.refresh_token_hash = None
    current_user.refresh_token_expires_at = None
    db.commit()
    return {"message": "Logged out successfully"}

@router.post(
    "/send-code",
    response_model=schemas.MessageResponse,
    dependencies=[Depends(rate_limiter(5, 60, "send-code"))],
)
def send_code(payload: schemas.SendCodeRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    verification_code = f"{random.randint(0, 999999):06d}"
    user.verification_code = verification_code
   
    user.verification_code_expires_at = datetime.utcnow() + timedelta(minutes=10)
    db.commit()

    print(f"Verification code for {user.email}: {verification_code}")
    return {"message": "Verification code sent"}

@router.post("/verify", response_model=schemas.MessageResponse)
def verify_code(payload: schemas.VerifyRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user.verification_code or user.verification_code != payload.code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid code")

    if not user.verification_code_expires_at or datetime.utcnow() > user.verification_code_expires_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code expired")

    user.is_verified = True
    user.verification_code = None
    user.verification_code_expires_at = None
    db.commit()
    return {"message": "Account verified successfully"}