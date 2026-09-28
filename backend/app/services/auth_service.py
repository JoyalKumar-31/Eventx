from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import (
    hash_password, verify_password, create_access_token, create_refresh_token, decode_token
)
from app.models.user import User, UserInterest, RefreshToken, RoleEnum
from app.schemas.auth import UserRegister, UserLogin, UserProfileUpdate, TokenResponse, UserOut


class AuthService:
    @staticmethod
    def register(db: Session, user_in: UserRegister) -> TokenResponse:
        # Check if email is already registered
        existing_user = db.query(User).filter(User.email == user_in.email.lower()).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered"
            )

        hashed = hash_password(user_in.password)
        new_user = User(
            email=user_in.email.lower(),
            hashed_password=hashed,
            full_name=user_in.full_name,
            phone=user_in.phone,
            college=user_in.college,
            department=user_in.department,
            year_of_study=user_in.year_of_study,
            role=user_in.role or RoleEnum.STUDENT,
            is_active=True,
            is_verified=True  # Auto-verified for seamless testing/demo
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Generate tokens
        access_token = create_access_token(subject=new_user.id, role=new_user.role.value)
        refresh_token = create_refresh_token(subject=new_user.id, role=new_user.role.value)

        # Store refresh token
        db_refresh = RefreshToken(
            user_id=new_user.id,
            token=refresh_token,
            expires_at=datetime.now(timezone.utc),  # will be handled
            revoked=False
        )
        db.add(db_refresh)
        db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserOut.model_validate(new_user)
        )

    @staticmethod
    def login(db: Session, credentials: UserLogin) -> TokenResponse:
        user = db.query(User).filter(User.email == credentials.email.lower()).first()
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is inactive"
            )

        access_token = create_access_token(subject=user.id, role=user.role.value)
        refresh_token = create_refresh_token(subject=user.id, role=user.role.value)

        # Store refresh token
        db_refresh = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.now(timezone.utc),
            revoked=False
        )
        db.add(db_refresh)
        db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserOut.model_validate(user)
        )

    @staticmethod
    def refresh(db: Session, refresh_token_str: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token_str)
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=401, detail="Invalid token type")
            user_id = payload.get("sub")
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

        # Verify in DB
        db_token = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token_str,
            RefreshToken.revoked == False
        ).first()

        if not db_token:
            raise HTTPException(status_code=401, detail="Refresh token has been revoked or is invalid")

        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")

        # Invalidate old refresh token and issue new pair
        db_token.revoked = True
        new_access = create_access_token(subject=user.id, role=user.role.value)
        new_refresh = create_refresh_token(subject=user.id, role=user.role.value)

        new_db_token = RefreshToken(
            user_id=user.id,
            token=new_refresh,
            expires_at=datetime.now(timezone.utc),
            revoked=False
        )
        db.add(new_db_token)
        db.commit()

        return TokenResponse(
            access_token=new_access,
            refresh_token=new_refresh,
            token_type="bearer",
            user=UserOut.model_validate(user)
        )

    @staticmethod
    def update_profile(db: Session, user: User, profile_in: UserProfileUpdate) -> User:
        update_data = profile_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def set_user_interests(db: Session, user_id: int, categories: List[str]) -> List[UserInterest]:
        # Delete existing interests
        db.query(UserInterest).filter(UserInterest.user_id == user_id).delete()
        interests = []
        for cat in set(categories):
            interest = UserInterest(user_id=user_id, category=cat.strip())
            db.add(interest)
            interests.append(interest)
        db.commit()
        return interests

    @staticmethod
    def get_user_interests(db: Session, user_id: int) -> List[str]:
        interests = db.query(UserInterest).filter(UserInterest.user_id == user_id).all()
        return [i.category for i in interests]
