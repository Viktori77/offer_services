from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, AsyncEngine

# Это будет установлено при запуске бота
async_session_maker: Optional[async_sessionmaker] = None
engine: Optional[AsyncEngine] = None

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency для получения сессии базы данных"""
    if async_session_maker is None:
        raise RuntimeError("База данных не инициализирована")
    
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

def setup_db(session_maker: async_sessionmaker, db_engine: AsyncEngine = None):
    """Устанавливает sessionmaker для использования в боте"""
    global async_session_maker, engine
    async_session_maker = session_maker
    if db_engine:
        engine = db_engine