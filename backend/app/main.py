from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import Base, engine
from app.middleware.auth import AuthMiddleware
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 例: /me はJWT必須（middlewareで弾く）
app.add_middleware(AuthMiddleware, protected_paths={"/me"})

app.include_router(auth_router, prefix="/auth")
app.include_router(users_router)


@app.get("/")
def root():
    return {"message": "Backend OK"}


# 起動時にテーブルを作成
Base.metadata.create_all(bind=engine)