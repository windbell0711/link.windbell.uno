import dotenv
from os import getenv 
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncpg

dotenv.load_dotenv()
assert getenv("DATABASE_URL"), "DATABASE_URL environment variable not set."

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(
        getenv("DATABASE_URL"),
        min_size=1,
        max_size=5,
        command_timeout=5
    )
    print("Database pool created.")
    
    yield
    
    await app.state.pool.close()
    print("Database pool closed.")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # 开发环境
    allow_methods=["GET"],
    allow_credentials=True,
)

@app.get("/api/redirect")
async def redirect(code: str):
    pool: asyncpg.pool.Pool = app.state.pool

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM link WHERE code = $1", code
        )
        if not row:
            return {"valid": False, "msg": "code不存在"}
        if row["date_begin"] and row["date_begin"] > datetime.now(timezone.utc):
            return {"valid": False, "msg": "链接未生效"}
        if row["date_end"] and row["date_end"] < datetime.now(timezone.utc):
            return {"valid": False, "msg": "链接已过期"}
        today = datetime.now(timezone.utc).date()
        last_access = row["access_lastdate"]
        if isinstance(last_access, datetime):
            same_day = last_access.date() == today
        else:
            same_day = last_access == today
        if same_day:
            if row["access_daylmt"] > 0 and row["access_daycnt"] >= row["access_daylmt"]:
                return {"valid": False, "msg": "链接访问次数已达上限"}
            await conn.execute(
                "UPDATE link SET access_daycnt = access_daycnt + 1 WHERE code = $1", code
            )
        else:
            await conn.execute(
                "UPDATE link SET access_daycnt = 1, access_lastdate = $2 WHERE code = $1", code, datetime.now(timezone.utc).date()
            )
        return {"valid": True, "url": row["url"]}
