import asyncio
from bot.create_bot import bot, dp, scheduler
from bot.handlers.start import router
from database.init_db import init_database
from reminders_bookings import start_scheduler_bookings
import uvicorn
from bot.handlers.app_webhook import app
from database.db import setup_db
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def start_fastapi():
    """Запуск FastAPI на порту 8005."""
    config = uvicorn.Config(app, host="127.0.0.1", port=8005)
    server = uvicorn.Server(config)
    await server.serve()


async def main():  
    # Инициализация базы данных
    logger.info("Инициализация базы данных...")
    engine, async_session = await init_database()
    setup_db(async_session, engine)
    # # Инициализация базы данных 
    # await async_main()
    # Подключение роутеров
    dp.include_router(router)
    # Регистрация задач в планировщике
    start_scheduler_bookings(scheduler, bot)
    # Запуск планировщика (если он ещё не запущен)
    if not scheduler.running:
        scheduler.start()
    # Удаление вебхука и запуск бота
    await bot.delete_webhook(drop_pending_updates=True)

    # Запуск FastAPI в отдельной задаче
    asyncio.create_task(start_fastapi())

    # Запуск бота
    await dp.start_polling(bot)
    

if __name__ == "__main__":
    try:        
        asyncio.run(main())
    except KeyboardInterrupt:
      print('Бот выключен')    