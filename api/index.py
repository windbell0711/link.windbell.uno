import dotenv
from os import getenv 
from datetime import datetime, date, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncpg

dotenv.load_dotenv()
assert getenv("DATABASE_URL"), "DATABASE_URL environment variable not set."

today = lambda: datetime.now(timezone.utc).date()

class PgLink(BaseModel):
    id: int
    code: str
    url: str
    access_lastdate: date
    access_daylmt: int = 0
    access_daycnt: int = 5
    date_begin: date | None = None
    date_end: date | None = None

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
async def redirect(code: str) -> dict:
    """返回值：{"valid": bool, "url": "重定向链接", "msg": "错误信息"}"""
    pool: asyncpg.pool.Pool = app.state.pool
    async with pool.acquire() as conn:
        # 查询数据库
        row = await conn.fetchrow(
            "SELECT * FROM link WHERE code = $1", code
        )
        if not row:
            return {"valid": False, "msg": "code不存在"}
        # 校验链接是否有效
        link = PgLink.model_validate(dict(row))
        if link.date_begin and link.date_begin > today():
            return {"valid": False, "msg": "链接未生效"}
        if link.date_end and link.date_end < today():
            return {"valid": False, "msg": "链接已过期"}
        # 校验链接是否次数已达上限，更新访问次数
        if link.access_lastdate == today():
            if link.access_daylmt > 0 and link.access_daycnt >= link.access_daylmt:
                return {"valid": False, "msg": "链接当日访问次数已达上限"}
            await conn.execute(
                "UPDATE link SET access_daycnt = access_daycnt + 1 WHERE code = $1", code
            )
        else:
            await conn.execute(
                "UPDATE link SET access_daycnt = 1, access_lastdate = $2 WHERE code = $1", code, today()
            )
        # 返回重定向链接
        return {"valid": True, "url": link.url, "msg": "成功找到有效链接"}

@app.get("/api/storage")
async def storage(key: str) -> dict:
    """返回值：{"valid": bool, "url": "带预签名的oss链接", "msg": "错误信息"}"""
    import api.oss as oss
    ret = oss.get_oss_url("wint-storage-1", object_key=key)
    if not ret:
        return {"valid": False, "msg": "预签名oss链接生成失败"}
    return {"valid": True, "url": ret, "msg": "成功生成带预签名的oss链接"}
