from datetime import datetime, timedelta
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.db_handlers import get_all_records
from helpers.messages import get_message_bookig
from bot.keyboards.all_keyboards import yes_or_cancel_booking

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def check_and_send_reminders_bookings(bot: Bot):
    """
    Проверяет, есть ли брони на сегодня и, если есть, находит пользователя по номеру телефона и отправляет напоминание с вопросом подтвердить или отменить.
    """
    try:
        # 1) Находим дату "завтра" в том формате, в котором у вас хранится Event.date
        
        today = (datetime.now()).date()
        filters={
            "date_booking": today
        }
        model_name="Record"
        # 2) Достаём все брони, у которых date = сегодня
        bookings_today = await get_all_records(model_name=model_name, filters=filters)
        
        if not bookings_today:
            logger.info(f"Нет броней на сегодня {today}")
            return
        else:
            for book in bookings_today:
                # Проверяем, заполнено ли поле numberPhone
                if not book.numberPhone or not book.numberPhone.strip():
                    logger.info(f"Запись {book.id} пропущена: поле numberPhone не заполнено.")
                    continue  # Пропускаем эту запись

                message_text = "❗ Вы записаны на сегодня ❗\n\n"
                message_text += get_message_bookig(book)
                message_text += f"🔗 Сайт для брони: {book.url_record_my}\n"

                filters={
                    "numberphone": book.numberPhone.strip()  # Убираем лишние пробелы
                }
                model_name="User"

                user = await get_all_records(model_name=model_name, filters=filters)

                if user and len(user) > 0:
                    keyboard = yes_or_cancel_booking(book.id)
                    # Отправляем сообщение с кнопками
                    await bot.send_message(
                        chat_id=user[0].tg_id,
                        text=message_text,
                        disable_web_page_preview=True, 
                        reply_markup=keyboard
                    )
                else:
                    logger.info(f"Пользователь с номером телефона {book.numberPhone} не найден.")
       
    except Exception as e:
        logger.error(f"Ошибка в check_and_send_reminders: {e}")


def start_scheduler_bookings(scheduler: AsyncIOScheduler, bot: Bot):
    """
    Функция для регистрации задач в планировщике и его старта.
    Запускается каждый день в 8:00.
    """
    logger.info("Запуск планировщика напоминаний о записях")

    # Пример ежедневного запуска в 12:00
    scheduler.add_job(
        check_and_send_reminders_bookings,
        "cron",
        hour=8,
        minute=0,
        args=[bot],
        id="daily_reminders_job",
        replace_existing=True  # чтобы при перезапуске приложения не создавать дубли
    )

    # Для теста - интервал каждые N секунд (раскомментируйте при необходимости):
    # scheduler.add_job(check_and_send_reminders_bookings, 'interval', seconds=30, args=[bot])

    # scheduler.start()