
# from aiogram_run import app
from pydantic import BaseModel
from helpers.messages import get_message_bookig
from fastapi import FastAPI
from pydantic import BaseModel
from helpers.messages import get_message_bookig
from database.db_handlers import get_all_records, get_numberPhone
from bot.create_bot import bot
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HookModel(BaseModel):
    event: str
    userName: str
    date_booking: str
    time_slot_start: str
    numberPhone: str
    model: str
    offerId: int

    params_1: Optional[str] = None
    params_2: Optional[str] = None
    params_3: Optional[str] = None
    params_4: Optional[str] = None
    params_5: Optional[str] = None
    question_1: Optional[str] = None
    question_2: Optional[str] = None
    question_3: Optional[str] = None
    question_4: Optional[str] = None
    question_5: Optional[str] = None

# Инициализация FastAPI
app = FastAPI()
    

# Добавление пользователя
@app.post("/webhook/")
async def hook_logic(data: HookModel) -> dict:
    
    if data.event == "booking":
        logger.info(f"Получены данные: {data}")


        
        message=get_message_bookig(data)
        # logger.info(f"message: {message}")

        #Ищим запись в модели для того, чтобы найти тгId хозяитна
        offerId=data.offerId
        model_name=data.model
        # Получаем запись из модели
        filters = {"id": offerId}  # Фильтр по offerId (id записи)
        records = await get_all_records(model_name, filters)

        if records:
            record = records[0]  # Берем первую запись (если найдена)
            tg_id = record.tgId  # Извлекаем tgId владельца
            logger.info(f"Найден tgId владельца: {tg_id}")

            user = await get_numberPhone(data.numberPhone)

            if user:
                # Если номер найден в таблице User
                message += "\n\n ✔️ Пользователь с таким номером есть в боте, поэтому ему придут напоминаниe о броне. А Вам придет уведомление о подтверждении или отмене брони."
            else:
                # Если номер не найден в таблице User
                message += "\n\n ❗ Внимание! Этот номер не закреплен. Рекомендуем проверить пользователя этого номера. Он не получит напоминание о брони."

            # Отправляем сообщение владельцу
            try:
                await bot.send_message(
                    chat_id=tg_id,
                    text=message
                )
                logger.info(f"Сообщение отправлено владельцу с tgId: {tg_id}")
            except Exception as e:
                logger.error(f"Ошибка при отправке сообщения владельцу: {e}")
        else:
            logger.error(f"Запись с offerId={offerId} в модели '{model_name}' не найдена.")

    return {"status": "ok"}