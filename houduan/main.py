from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from config import settings
from database import async_engine, Base
from routes.auth import router as auth_router
from routes.users import router as users_router
from routes.permission import router as permission_router

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="多智能体拟人化社交媒体数据生成与标注系统 - 认证模块",
    description="登录认证后端模块，提供用户注册、登录、权限鉴权等接口",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(permission_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"code": 500, "msg": "服务器内部错误", "data": None},
    )


@app.get("/health", tags=["健康检查"])
async def health_check():
    return {"code": 0, "msg": "success", "data": {"status": "healthy"}}


@app.on_event("startup")
async def startup():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await async_engine.dispose()
