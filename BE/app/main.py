import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.handler import set_error_handlers
from api.v1.endpoints import auth, chat, document, user_group
from db.database import init_db, init_data
from services.qdrant_service import QdrantService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("app start")
    await init_db()
    print("db init")
    await init_data()
    print("data init")
    await QdrantService().get_or_create_collection()
    print("qdrant init")
    yield
    print("app shutdown")


app = FastAPI(lifespan=lifespan)

app.include_router(auth.auth_router)
app.include_router(chat.chat_router)
app.include_router(document.docs_router)
app.include_router(user_group.user_group_router)

set_error_handlers(app)
