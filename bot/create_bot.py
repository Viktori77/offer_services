
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from decouple import config
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from middleware.ban_user import BanMiddleware
from aiogram import Dispatcher



# Инициализация планировщика
scheduler = AsyncIOScheduler(timezone='Europe/Moscow')

# Получение списка админов из конфига
admins = [int(admin_id) for admin_id in config('ADMINS').split(',')]
url_recording = config('URL_RECORDING')

# Инициализация бота
bot = Bot(token=config('TELEGRAM_TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# Инициализация диспетчера
dp = Dispatcher(storage=MemoryStorage())

# Подключаем мидлварь к роутеру
dp.message.middleware(BanMiddleware())
dp.callback_query.middleware(BanMiddleware())