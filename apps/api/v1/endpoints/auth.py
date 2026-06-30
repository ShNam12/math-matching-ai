from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.v1.models.auth import (
    AuthUserResponse,
    LoginRequest,
    LoginResponse,
)
from apps.api.v1.services.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
)
from infra.db.models import User
from infra.db.session import get_db_session


router = APIRouter(prefix="/auth", tags=["auth"])


def to_auth_user_response(user: User) -> AuthUserResponse:
    return AuthUserResponse(
        username=user.username,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
) -> LoginResponse:
    user = await authenticate_user(
        session=session,
        username=payload.username,
        password=payload.password,
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = create_access_token(
        subject=user.username,
        role=user.role,
    )

    return LoginResponse(
        access_token=access_token,
        user=to_auth_user_response(user),
    )


@router.get("/me", response_model=AuthUserResponse)
async def me(
    current_user: User = Depends(get_current_user),
) -> AuthUserResponse:
    return to_auth_user_response(current_user)

