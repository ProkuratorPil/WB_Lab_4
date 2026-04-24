# Архитектура проекта Web Lab 3

## Общая структура

```
app/
├── api/                    # API роутеры (в哀)
├── core/                   # Ядро приложения
│   ├── config.py          # Настройки (Pydantic Settings)
│   ├── database.py         # Подключение к PostgreSQL
│   ├── dependencies.py    # Зависимости FastAPI
│   ├── jwt.py             # JWT работа с токенами
│   ├── security.py        # Хэширование паролей
│   └── oauth/             # OAuth авторизация (Яндекс, VK)
├── crud/                  # CRUD операции
├── models/                # SQLAlchemy ORM модели
├── routers/               # API роутеры
├── schemas/               # Pydantic DTO схемы
└── services/              # Бизнес-логика
```

## Принцип работы

### 1. Запрос → Роутер → Сервис → CRUD → ORM → База данных

```
HTTP Request
    ↓
Router (app/routers/*.py)       # Маршрутизация, валидация запроса
    ↓
Service (app/services/*.py)     # Бизнес-логика
    ↓
CRUD (app/crud/*.py)           # Операции с данными
    ↓
ORM Model (app/models/*.py)     # SQLAlchemy модели
    ↓
PostgreSQL Database
```

### 2. Аутентификация (JWT)

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Клиент    │────▶│  Auth Router │────▶│  JWT Token  │
└─────────────┘     └──────────────┘     └─────────────┘
                           │                     │
                           ▼                     ▼
                    ┌──────────────┐     ┌─────────────┐
                    │  User Model   │◀────│   Cookie    │
                    └──────────────┘     └─────────────┘
```

---

## ORM Модели (SQLAlchemy)

### User Model (`app/models/user.py`)

```python
class User(Base):
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True)
    
    # Осные поля
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Nullable для OAuth
    password_salt = Column(String, nullable=True)
    
    # OAuth
    yandex_id = Column(String, unique=True, nullable=True)
    vk_id = Column(String, unique=True, nullable=True)
    
    # Статус
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft Delete
    
    # Связи
    files = relationship("UploadedFile", back_populates="user")
    tokens = relationship("Token", back_populates="user")
    
    @property
    def is_oauth_user(self) -> bool:
        return self.hashed_password is None and (self.yandex_id or self.vk_id)
```

### UploadedFile Model (`app/models/uploaded_file.py`)

```python
class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    filename = Column(String, nullable=False)          # Оригинальное имя
    stored_filename = Column(String, nullable=False)   # Имя на сервере
    file_path = Column(String, nullable=False)          # Путь к файлу
    file_size = Column(Integer, nullable=False)         # Размер в байтах
    mime_type = Column(String, nullable=False)         # MIME-тип
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft Delete
    
    # Связь
    user = relationship("User", back_populates="files")
```

---

## DTO Схемы (Pydantic)

### User DTO (`app/schemas/user.py`)

```python
# Создание пользователя (входные данные)
class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=6, max_length=72)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)

# Обновление пользователя (все поля опциональны)
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[str] = Field(None, min_length=1, max_length=100)
    password: Optional[str] = Field(None, min_length=6, max_length=72)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None

# Ответ клиенту (без sensitive данных)
class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    is_oauth_user: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
```

### Auth DTO (`app/schemas/auth.py`)

```python
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8, max_length=72)
    phone: Optional[str] = Field(None, max_length=20)
    
    # Валидаторы
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Только латинские буквы, цифры, _ и -')
        return v.lower()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r'[A-Z]', v):
            raise ValueError('Нужна заглавная буква')
        if not re.search(r'[a-z]', v):
            raise ValueError('Нужна строчная буква')
        if not re.search(r'\d', v):
            raise ValueError('Нужна цифра')
        return v

class UserLogin(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    access_expires_at: datetime
    refresh_expires_at: datetime

class UserProfile(BaseModel):
    id: UUID
    username: str
    email: str
    phone: Optional[str] = None
    is_verified: bool
    is_oauth_user: bool
    created_at: datetime
    oauth_providers: list[str] = []
    
    model_config = ConfigDict(from_attributes=True)
```

### File DTO (`app/schemas/file.py`)

```python
class FileCreate(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    stored_filename: str = Field(..., min_length=1, max_length=255)
    file_path: str = Field(..., min_length=1, max_length=500)
    file_size: int = Field(..., gt=0)
    mime_type: str = Field(..., min_length=1, max_length=100)
    user_id: UUID

class FileResponse(BaseModel):
    id: UUID
    filename: str
    stored_filename: str
    file_path: str
    file_size: int
    mime_type: str
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
```

---

## Пагинация

### Схема пагинации

```python
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)      # Страница (минимум 1)
    limit: int = Field(10, ge=1, le=100)  # Элементов на страницу (1-100)

class PaginatedResponse(BaseModel):
    data: list[UserResponse]  # или list[FileResponse]
    meta: dict               # Метаданные
```

### Ответ с пагинацией

```json
{
    "data": [
        {"id": "uuid", "username": "user1", ...},
        {"id": "uuid", "username": "user2", ...}
    ],
    "meta": {
        "total": 50,
        "page": 1,
        "limit": 10,
        "totalPages": 5
    }
}
```

### Пример использования в роутере

```python
@router.get("/users", response_model=PaginatedResponse)
def get_users(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = UserService(db)
    users, total = service.get_all_active(pagination)
    
    total_pages = (total + pagination.limit - 1) // pagination.limit
    
    return {
        "data": users,
        "meta": {
            "total": total,
            "page": pagination.page,
            "limit": pagination.limit,
            "totalPages": total_pages,
        }
    }
```

### Пример в сервисе

```python
def get_all_active(self, pagination: PaginationParams) -> Tuple[list[User], int]:
    # Считаем общее количество
    offset = (pagination.page - 1) * pagination.limit
    
    count_stmt = select(func.count()).select_from(
        select(User).where(User.deleted_at.is_(None)).subquery()
    )
    total = self.db.execute(count_stmt).scalar()
    
    # Получаем страницу
    stmt = (
        select(User)
        .where(User.deleted_at.is_(None))
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(pagination.limit)
    )
    users = self.db.execute(stmt).scalars().all()
    
    return users, total
```

---

## API Endpoints

### Auth (`/auth`)

| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| POST | `/auth/register` | Регистрация | Public |
| POST | `/auth/login` | Вход | Public |
| POST | `/auth/refresh` | Обновить токены | Public |
| POST | `/auth/logout` | Выход | Private |
| POST | `/auth/logout-all` | Выйти со всех устройств | Private |
| GET | `/auth/whoami` | Профиль текущего пользователя | Private |
| GET | `/auth/oauth/{provider}` | Инициация OAuth (yandex/vk) | Public |
| GET | `/auth/oauth/{provider}/callback` | OAuth callback | Public |
| POST | `/auth/forgot-password` | Запрос сброса пароля | Public |
| POST | `/auth/reset-password` | Сброс пароля | Public |

### Users (`/users`)

| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| POST | `/users` | Создать пользователя | Public |
| GET | `/users` | Список пользователей (пагинация) | Private |
| GET | `/users/{id}` | Получить пользователя | Private |
| PUT | `/users/{id}` | Полное обновление | Private (owner) |
| PATCH | `/users/{id}` | Частичное обновление | Private (owner) |
| DELETE | `/users/{id}` | Удалить (soft delete) | Private (owner) |

### Files (`/files`)

| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| POST | `/files` | Создать запись о файле | Private |
| GET | `/files` | Список файлов (пагинация) | Private |
| GET | `/files/{id}` | Получить файл | Private (owner) |
| PUT | `/files/{id}` | Обновить | Private (owner) |
| PATCH | `/files/{id}` | Частично обновить | Private (owner) |
| DELETE | `/files/{id}` | Удалить (soft delete) | Private (owner) |

---

## База данных (PostgreSQL)

### Основные таблицы

- `users` — пользователи
- `uploaded_files` — файлы
- `tokens` — токены авторизации

### Особенности

- **UUID** как primary key
- **Soft Delete** — записи не удаляются физически, а помечаются `deleted_at`
- **Timestamps** — `created_at`, `updated_at` с timezone
- **OAuth** — поддержка Яндекса и VK

---

## Запуск

```bash
# Разработка
docker-compose up --build

# Пересборка
docker-compose down
docker-compose up --build --force-recreate
```

Приложение доступно на `http://localhost:4200`
Swagger UI: `http://localhost:4200/docs`
