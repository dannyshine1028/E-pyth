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


@app.on_event("startup")
def on_startup():
    # DBが落ちていてもbackend自体は起動できるようにする（開発継続性優先）
    try:
        Base.metadata.create_all(bind=engine)
        print("[db] create_all ok")
    except Exception as e:
        print(f"[db] create_all failed: {type(e).__name__}: {e}")