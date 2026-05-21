"""插入演示帖文: python scripts/seed_demo.py"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.community import Post
from app.models.user import User


async def main() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.username == "demo"))
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                email="demo@wanderchina.local",
                username="demo",
                hashed_password=hash_password("demo12345"),
                role="tourist",
                display_name="Demo Traveler",
                avatar_url="/uploads/avatars/default.png",
            )
            db.add(user)
            await db.flush()

        existing = await db.execute(select(Post).limit(1))
        if existing.scalar_one_or_none():
            print("Posts already exist, skip seed.")
            return

        samples = [
            ("宽窄巷子怎么逛不踩雷？", "早上九点前去，本地人推荐的茶馆比攻略靠谱。", "成都·宽窄巷子"),
            ("上海地铁换乘求助", "第一次来上海，人民广场换乘有没有英文标识？", "上海·人民广场"),
            ("北京烤鸭店推荐", "不想吃游客套餐，求胡同里靠谱的店。", "北京·东城区"),
        ]
        for title, body, loc in samples:
            db.add(
                Post(
                    author_id=user.id,
                    title=title,
                    body=body,
                    location_name=loc,
                    moderation_status="approved",
                    language="zh",
                )
            )
        await db.commit()
        print("Demo posts seeded (user: demo / demo12345).")


if __name__ == "__main__":
    asyncio.run(main())
