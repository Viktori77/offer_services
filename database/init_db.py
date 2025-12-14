from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select
from database.models import Base, Town
from struction import all_town_name
from decouple import config
import logging

logger = logging.getLogger(__name__)

LOGIN=config('LOGIN')
PASSWORD=config('PASSWORD')
HOST=config('HOST')
DB=config('DB')

async def init_database():
    """Инициализация базы данных и создание таблиц"""
    # Создаём асинхронный движок для PostgreSQL
    engine = create_async_engine(url=f'postgresql+asyncpg://{LOGIN}:{PASSWORD}@{HOST}:5432/{DB}')
    
    # Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Создаем сессию для работы с базой
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    # Инициализируем города
    await init_towns(async_session)
    
    return engine, async_session

async def init_towns(async_sessionmaker):
    """Загрузка городов в базу данных"""
    async with async_sessionmaker() as session:
        try:
            # Получаем все города, которые уже есть в базе
            result = await session.execute(select(Town.town))
            existing_town_names = set(result.scalars().all())
            
            # Список всех русских названий из словаря
            dict_town_names = set(all_town_name.values())
            
            # Находим города, которых нет в базе
            towns_to_add = dict_town_names - existing_town_names
            
            if not towns_to_add:
                logger.info("Все города из словаря уже есть в базе данных")
                return
            
            # Добавляем только отсутствующие города
            added_count = 0
            for town_name in towns_to_add:
                new_town = Town(town=town_name, grade=1)
                session.add(new_town)
                added_count += 1
                logger.info(f"Добавлен город: {town_name}")
            
            await session.commit()
            logger.info(f"Добавлено {added_count} новых городов в базу данных")
            
            # Опционально: проверяем, есть ли в базе города, которых нет в словаре
            extra_towns = existing_town_names - dict_town_names
            if extra_towns:
                logger.warning(f"В базе есть города, которых нет в словаре: {extra_towns}")
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка при добавлении городов: {e}")
            raise