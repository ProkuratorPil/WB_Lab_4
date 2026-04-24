# main_fastapi.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import logging
import os

from app.routers import user_router
from app.routers import file_router
from app.routers.auth_router import router as auth_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="User & File Management API",
    description="API для управления пользователями и файлами с JWT аутентификацией",
    version="2.0.0"
)

# OpenAPI документация (только в development режиме)
if os.getenv('NODE_ENV') != 'production':
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title="User & File Management API",
            version="2.0.0",
            description="Документация API для управления пользователями и файлами с JWT аутентификацией",
            routes=app.routes,
        )
        openapi_schema["info"]["x-logo"] = {
            "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
        }
        if "components" not in openapi_schema:
            openapi_schema["components"] = {}
        
        openapi_schema["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            },
            "oauth2": {
                "type": "oauth2",
                "flows": {
                    "authorizationCode": {
                        "authorizationUrl": "https://oauth.yandex.ru/authorize",
                        "tokenUrl": "https://oauth.yandex.ru/token",
                        "scopes": {
                            "email": "Access to user's email",
                            "openid": "Access to user's profile"
                        }
                    }
                }
            }
        }
        openapi_schema["security"] = [
            {"bearerAuth": {}},
            {"oauth2": ["email", "openid"]}
        ]
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Глобальная обработка исключений
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Глобальный обработчик ошибок."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Обработчик HTTP исключений."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


# Подключение роутеров
app.include_router(auth_router)
app.include_router(user_router.router)
app.include_router(file_router.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the User & File Management API"}


@app.get("/health")
def health_check():
    """Healthcheck endpoint."""
    return {"status": "healthy"}