"""
DTO (Data Transfer Objects) для аутентификации и авторизации.
"""
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional
import re


class UserRegister(BaseModel):
    """DTO для регистрации нового пользователя."""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Уникальное имя пользователя (латиница и цифры)",
        example="john_doe"
    )
    email: EmailStr = Field(
        ...,
        description="Email пользователя",
        example="john.doe@example.com"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description="Пароль (минимум 8 символов, включая заглавные, строчные и цифры)",
        example="SecurePassword123"
    )
    phone: Optional[str] = Field(
        None,
        max_length=20,
        description="Телефон пользователя (опционально)",
        example="+1234567890"
    )
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username может содержать только латинские буквы, цифры, _ и -')
        return v.lower()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r'[A-Z]', v):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        if not re.search(r'[a-z]', v):
            raise ValueError('Пароль должен содержать хотя бы одну строчную букву')
        if not re.search(r'\d', v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = re.sub(r'[^\d+]', '', v)
            if len(cleaned) < 10:
                raise ValueError('Номер телефона должен содержать минимум 10 цифр')
            return cleaned
        return v


class UserLogin(BaseModel):
    """DTO для входа пользователя."""
    email: EmailStr = Field(
        ...,
        description="Email пользователя",
        example="john.doe@example.com"
    )
    password: str = Field(
        ...,
        description="Пароль пользователя",
        example="SecurePassword123"
    )


class TokenResponse(BaseModel):
    """DTO для ответа с токенами."""
    access_token: str = Field(
        ...,
        description="JWT токен доступа (15 минут)",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )
    refresh_token: str = Field(
        ...,
        description="JWT токен обновления (7 дней)",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )
    token_type: str = Field(
        "bearer",
        description="Тип токена",
        example="bearer"
    )
    access_expires_at: datetime = Field(
        ...,
        description="Время истечения access токена",
        example="2024-01-01T12:15:00Z"
    )
    refresh_expires_at: datetime = Field(
        ...,
        description="Время истечения refresh токена",
        example="2024-01-08T12:00:00Z"
    )


class UserResponse(BaseModel):
    """DTO для ответа с данными пользователя."""
    id: UUID = Field(
        ...,
        description="Уникальный идентификатор пользователя",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    username: str = Field(
        ...,
        description="Уникальное имя пользователя",
        example="john_doe"
    )
    email: str = Field(
        ...,
        description="Email пользователя",
        example="john.doe@example.com"
    )
    phone: Optional[str] = Field(
        None,
        description="Телефон пользователя (опционально)",
        example="+1234567890"
    )
    is_verified: bool = Field(
        ...,
        description="Статус верификации email",
        example=False
    )
    is_oauth_user: bool = Field(
        ...,
        description="Признак регистрации через OAuth провайдера",
        example=False
    )
    created_at: datetime = Field(
        ...,
        description="Дата и время создания пользователя",
        example="2024-01-01T12:00:00Z"
    )

    model_config = ConfigDict(from_attributes=True)


class UserProfile(BaseModel):
    """Расширенный профиль пользователя для /whoami."""
    id: UUID = Field(
        ...,
        description="Уникальный идентификатор пользователя",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    username: str = Field(
        ...,
        description="Уникальное имя пользователя",
        example="john_doe"
    )
    email: str = Field(
        ...,
        description="Email пользователя",
        example="john.doe@example.com"
    )
    phone: Optional[str] = Field(
        None,
        description="Телефон пользователя (опционально)",
        example="+1234567890"
    )
    is_verified: bool = Field(
        ...,
        description="Статус верификации email",
        example=False
    )
    is_oauth_user: bool = Field(
        ...,
        description="Признак регистрации через OAuth провайдера",
        example=False
    )
    created_at: datetime = Field(
        ...,
        description="Дата и время создания пользователя",
        example="2024-01-01T12:00:00Z"
    )
    oauth_providers: list[str] = Field(
        [],
        description="Список подключенных OAuth провайдеров",
        example=["yandex", "vk"]
    )

    model_config = ConfigDict(from_attributes=True)


class ForgotPasswordRequest(BaseModel):
    """DTO для запроса сброса пароля."""
    email: EmailStr = Field(
        ...,
        description="Email пользователя для сброса пароля",
        example="john.doe@example.com"
    )


class ResetPasswordRequest(BaseModel):
    """DTO для установки нового пароля."""
    token: str = Field(
        ...,
        description="Токен сброса пароля",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description="Новый пароль (минимум 8 символов, включая заглавные, строчные и цифры)",
        example="NewSecurePassword123"
    )

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r'[A-Z]', v):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        if not re.search(r'[a-z]', v):
            raise ValueError('Пароль должен содержать хотя бы одну строчную букву')
        if not re.search(r'\d', v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        return v


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str = Field(
        ...,
        description="Основное сообщение ответа",
        example="Операция выполнена успешно"
    )
    detail: Optional[str] = Field(
        None,
        description="Дополнительная информация (опционально)",
        example="Пользователь создан с ID: 123"
    )
