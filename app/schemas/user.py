# app/schemas/user.py
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


# Схема для создания нового пользователя
class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Уникальное имя пользователя (латиница и цифры)",
        example="john_doe"
    )
    email: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Уникальный email пользователя",
        example="john.doe@example.com"
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=72,
        description="Пароль (до хэширования), ограничен 72 символами",
        example="securePassword123"
    )
    first_name: Optional[str] = Field(
        None,
        max_length=50,
        description="Имя пользователя (опционально)",
        example="John"
    )
    last_name: Optional[str] = Field(
        None,
        max_length=50,
        description="Фамилия пользователя (опционально)",
        example="Doe"
    )
    phone: Optional[str] = Field(
        None,
        max_length=20,
        description="Телефон пользователя (опционально)",
        example="+1234567890"
    )

# Схема для обновления существующего пользователя
# Все поля опциональны, чтобы поддерживать частичное обновление
class UserUpdate(BaseModel):
    username: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Новое имя пользователя (латиница и цифры)",
        example="john_doe_new"
    )
    email: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Новый email пользователя",
        example="john.doe.new@example.com"
    )
    password: Optional[str] = Field(
        None,
        min_length=6,
        max_length=72,
        description="Новый пароль (до хэширования), ограничен 72 символами",
        example="newSecurePassword123"
    )
    first_name: Optional[str] = Field(
        None,
        max_length=50,
        description="Новое имя пользователя (опционально)",
        example="John"
    )
    last_name: Optional[str] = Field(
        None,
        max_length=50,
        description="Новая фамилия пользователя (опционально)",
        example="Doe"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Возможность деактивировать аккаунт"
    )


# Схема для ответа клиенту (не включает пароль)
class UserResponse(BaseModel):
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
    first_name: Optional[str] = Field(
        None,
        description="Имя пользователя (опционально)",
        example="John"
    )
    last_name: Optional[str] = Field(
        None,
        description="Фамилия пользователя (опционально)",
        example="Doe"
    )
    phone: Optional[str] = Field(
        None,
        description="Телефон пользователя (опционально)",
        example="+1234567890"
    )
    is_active: bool = Field(
        True,
        description="Статус активности пользователя"
    )
    is_verified: bool = Field(
        False,
        description="Статус верификации email"
    )
    is_oauth_user: bool = Field(
        False,
        description="Признак регистрации через OAuth провайдера"
    )
    created_at: datetime = Field(
        ...,
        description="Дата и время создания пользователя",
        example="2024-01-01T12:00:00Z"
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Дата и время последнего обновления профиля",
        example="2024-01-02T15:30:00Z"
    )
    # deleted_at не включаем в ответ для активных пользователей

    model_config = ConfigDict(from_attributes=True)  # Позволяет ORM-объекту (User) маппиться на эту схему

# Схема для параметров пагинации (остается без изменений)
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)  # По умолчанию первая страница
    limit: int = Field(10, ge=1, le=100)  # По умолчанию 10 элементов, максимум 100

# Общая схема для ответа с пагинацией (тип данных в 'data' меняется на UserResponse)
class PaginatedResponse(BaseModel):
    data: list[UserResponse]  # <-- Изменили тип данных здесь
    meta: dict
