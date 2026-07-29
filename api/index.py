import dotenv
from os import getenv 
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncpg

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     app.state.pool = await asyncpg.create_pool(
#         os.getenv("DATABASE_URL"),
#         min_size=1,
#         max_size=5,
#         command_timeout=5
#     )
#     print("Database pool created.")
    
#     yield
    
#     await app.state.pool.close()
#     print("Database pool closed.")

# app = FastAPI(lifespan=lifespan)

# @app.get("/api/redirect")
# async def redirect(code: str):
#     pool: asyncpg.pool.Pool = app.state.pool
#     async with pool.acquire() as conn:
#         row = await conn.fetchrow(
#             "SELECT target_url, expires_at, visit_limit, visit_count FROM pickup_links WHERE code = $1",
#             code
#         )
#         if not row:
#             return {"valid": False, "msg": "鍙栦欢鐮佷笉瀛樺湪"}
            
#         if row["expires_at"] and row["expires_at"] < datetime.now(timezone.utc):
#             return {"valid": False, "msg": "閾炬帴宸茶繃鏈?}
            
#         if row["visit_limit"] > 0 and row["visit_count"] >= row["visit_limit"]:
#             return {"valid": False, "msg": "璁块棶娆℃暟宸茶揪涓婇檺"}
            
#         await conn.execute(
#             "UPDATE pickup_links SET visit_count = visit_count + 1 WHERE code = $1",
#             code
#         )
        
#         return {"valid": True, "url": row["target_url"]}

app = FastAPI()

@app.get("/api/redirect")
def redirect(code: str):
    return {"valid": True, "url": "https://cn.bing.com/search?q=%s" % code}
