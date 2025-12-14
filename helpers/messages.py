from aiogram import Bot
from database.db_handlers import (
    get_all_records, get_tg_ids_from_model, get_user_by_tg_id, add_or_update_record, get_all_in_town, remove_record
    )
from struction import (
    all_town_name
    )
from typing import List, Dict, Any
from utils import format_date, escape_markdown, get_model_name_ru, get_current_time
from datetime import date, datetime
from sqlalchemy import inspect
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def create_new_message_text(
    town: str,
    event: str,
    description: str,
    event_date: date,
    time: str,
    link_to_source: str,
    price: int,
    place: str,
    new_action: str = None,
    title: str = None,
):
    """
    Создаем сообщение для отправки пользователю.
    
    :param town: Город мероприятия.
    :param event: Название мероприятия.
    :param event_date: Дата мероприятия.
    :param time: Время мероприятия.
    :param link_to_source: Ссылка на источник.
    :param price: Цена мероприятия.
    :param place: Место проведения.
    :param new_action: Новый статус мероприятия (опционально).
    :param title: Заголовок сообщения (опционально).
    """
    # Преобразуем дату в формат дд.мм.гггг
    formatted_date = format_date(event_date)

    # Формируем основную часть сообщения
    if title:
        message_text = (
            f"🎉 {title}:\n\n"
            f"🌆 В городе {town}\n\n"
            f"🎭 Название: {event}\n"
            f"📅 Дата: {formatted_date}\n"
            f"⏰ Время: {time}\n"
            f"📍 Место: {place}\n"
        )
    else:
        if new_action == "отменено":
            message_text = (
                f"🚫 Мероприятие отменено!\n\n"
                f"🌆 В городе {town}\n\n"
                f"🎭 Название: {event}\n"
                f"📅 Дата: {formatted_date}\n"
                f"⏰ Время: {time}\n\n"
                f"📍 Место: {place}\n"
            )
        elif new_action == "перенесено":
            message_text = (
                f"🔄 Мероприятие перенесено!\n\n"
                f"🌆 В городе {town}\n\n"
                f"🎭 Название: {event}\n"
                f"📅 Дата: {formatted_date}\n"
                f"⏰ Время: {time}\n\n"
                f"📍 Место: {place}\n"
            )
        else:
            # Если new_action другое или не указано
            message_text = (
                f"🎉 Новое мероприятие!\n\n"
                f"🌆 В городе {town}\n\n"
                f"🎭 Название: {event}\n"
                f"📅 Дата: {formatted_date}\n"
                f"⏰ Время: {time}\n"
                f"📍 Место: {place}\n"
            )

    # Добавляем описание, если она больше 0
    if description:
        message_text += f"🌟 Описание: {description}\n\n"

    # Добавляем стоимость, если она больше 0
    if price != 0:
        message_text += f"💵 Стоимость: {price}\n"

    # Добавляем ссылку на источник
    message_text += f"🔗 Ссылка на источник: {link_to_source}\n"

    # Добавляем "Следите за новостями!" в конце сообщения
    message_text += "\nСледите за новостями!\n\n Информацию уточняйте на кассе!\n"

    return message_text

async def send_messages_to_users_all(
    bot: Bot,
    message: str,
    model_name: str = None,
    place_name: str = None,
    town: str = None,
):
    """
    Отправляет уведомление всем пользователям, кроме забаненных и тех, кто есть в указанной таблице.

    :param bot: Объект бота.
    :param message: Текст сообщения для отправки.
    :param model_name: Имя модели, пользователи из которой будут исключены из рассылки.
                      Если None, исключения по модели не применяются.
    :place_name - для удаления из рассылки юзера, кто добавил исключение по месту
    """
    # Получаем список всех пользователей
    users = await get_all_records("User")

    # Инициализируем список исключенных tg_id
    excluded_tg_ids = set()

    # Если model_name указан, получаем список tg_id из указанной модели
    if model_name is not None:
        settings_model_name = f"settings_{model_name}"
        try:
            excluded_tg_ids = await get_tg_ids_from_model(settings_model_name)
        except Exception as e:
            logger.error(f"Ошибка при получении данных из модели {settings_model_name}: {e}")
            return

    # Отправляем сообщение каждому пользователю
    for user in users:
        # Проверяем, забанен ли пользователь
        if user.ban:  # Если user.ban == True
            logger.info(f"Пользователь {user.tg_id} забанен, сообщение не отправлено.")
            continue  # Пропускаем этого пользователя
        
        if model_name in all_town_name:
            excluded_tg_ids_Event = set()
            excluded_tg_ids_Event = await get_tg_ids_from_model("settings_Event")
            if user.tg_id in excluded_tg_ids_Event:
                logger.info(f'Пользователь {user.tg_id} найден в таблице "settings_Event", сообщение не отправлено.')
                continue  # Пропускаем этого пользователя

        # Если model_name указан, проверяем, есть ли пользователь в списке исключений
        if model_name is not None and user.tg_id in excluded_tg_ids:
            logger.info(f"Пользователь {user.tg_id} найден в таблице {settings_model_name}, сообщение не отправлено.")
            continue  # Пропускаем этого пользователя

        
        model = "Place_settings"
        try:
            filters={
                "town": town,
                "place_name": place_name,
                "tgId": int(user.tg_id)
            }
            check_in_places=await get_all_in_town(model_name=model, town=town, filters=filters)
        except Exception as e:
            logger.error(f"Ошибка при получении данных из модели {model}: {e}")
            return
        if check_in_places:
            logger.info(f"Пользователь {user.tg_id} найден в таблице {model} c местом провдеедния {place_name}, сообщение не отправлено.")
            continue  # Пропускаем этого пользователя

        # Отправляем сообщение
        try:
            await bot.send_message(chat_id=int(user.tg_id), text=message)
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления пользователю {user.tg_id}: {e}")

            # Если пользователь заблокировал бота, удаляем его из таблицы User
            if "Forbidden: bot was blocked by the user" in str(e):
                logger.info(f"Пользователь {user.tg_id} заблокировал бота. Удаляем его из таблицы User.")
                try:
                    await remove_record(
                        model_name="User",
                        filters={"tg_id": int(user.tg_id)}
                    )
                except Exception as delete_error:
                    logger.error(f"Ошибка при удалении пользователя {user.tg_id} из таблицы User: {delete_error}")


async def send_message_to_user(
    fromWhomUser: str,  
    bot: Bot,
    user_id: int,
    # message: str,
    topic: str, 
    message_text: str,
    status: str, #новость или ответ, или предлоежние
    model_name: str = None,
    model_name_for_messages: str = None,
    fromWhomUser_tgId: int = None,
):
    """
    Отправляет сообщение одному пользователю, если он не забанен и не находится в списке исключений.

    :param bot: Объект бота.
    :param user_id: ID пользователя, которому нужно отправить сообщение.
    :param topic: ТЕма сообщения для отправки.
    :param message_text: Текст сообщения для отправки.
    :param model_name: Имя модели, пользователи из которой будут исключены из рассылки.
    Если None, исключения по модели не применяются.
    :model_name_for_messages: Имя модели, для того, чтобы занесено было это сообщение в отправленные или полученные, в зависимсоти от переданной модели model_name_for_messages="SendMessagesAdmin" или model_name_for_messages="SendMessagesUser". Если этот параметр не передан, значит сообщение не будет добавлено в таблицу
    """
    # Получаем информацию о пользователе
    user = await get_user_by_tg_id(user_id)  # Предположим, что у вас есть функция для получения пользователя по ID

    if not user:
        logger.error(f"Пользователь с ID {user_id} не найден.")
        return
    

    # Проверяем, забанен ли пользователь
    if user.ban:  # Если user.ban == True
        logger.info(f"Пользователь {user_id} забанен, сообщение не отправлено.")
        return
    

    # Если model_name указан, проверяем, есть ли пользователь в списке исключений
    if model_name is not None:
        settings_model_name = f"settings_{model_name}"
        try:
            excluded_tg_ids = await get_tg_ids_from_model(settings_model_name)
            if user.tg_id in excluded_tg_ids:
                logger.info(f"Пользователь {user.tg_id} найден в таблице {settings_model_name}, сообщение не отправлено.")
                return
        except Exception as e:
            logger.error(f"Ошибка при получении данных из модели {settings_model_name}: {e}")
            # return
        
    # Формируем красивое сообщение
    formatted_message = format_message_for_send(fromWhomUser, user.tg_name, topic, message_text)    

    # Отправляем сообщение
    try:
        await bot.send_message(chat_id=user.tg_id, text=formatted_message)
        logger.info(f"Сообщение успешно отправлено пользователю {user.tg_id}.")
        if model_name_for_messages=="SendMessagesAdmin":
            tg_id=int(user.tg_id)
        elif model_name_for_messages=="SendMessagesUser":
            tg_id=fromWhomUser_tgId

        if model_name_for_messages:
            # Данные для добавления в таблицу SendMessagesAdmin
            record_data = {
                "tgId": int(tg_id),
                "topic": topic,
                "body": message_text,
                "createdAt": str(get_current_time()),  # Форматируем дату и время
                "status": status,  # Статус по умолчанию
            }

            # Добавляем запись в таблицу SendMessagesAdmin
            success = await add_or_update_record(
                model_name=model_name_for_messages,  # Имя модели
                filters={"tgId": int(user.tg_id), "topic": topic, "body": message_text},  # Фильтры для поиска существующей записи
                data=record_data,  # Данные для добавления/обновления
            )

            if success:
                logger.info(f"Запись о сообщении добавлена/обновлена в таблице {model_name} для пользователя {user.tg_id}.")
            else:
                logger.error(f"Не удалось добавить/обновить запись в таблице SendMessagesAdmin для пользователя {user.tg_id}.")
        else:
            logger.info(f"Это не сообщение, а предложение, поэтому оно в таблицы сообщений не добавляется.")
        

    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления пользователю {user.tg_id}: {e}")

def format_data_message(events: List[Dict[str, Any]], title: str = "Мероприятия") -> str:
    """
    Форматирует список мероприятий в читаемое сообщение.

    :param events: Список мероприятий.
    :param title: Заголовок сообщения (по умолчанию "Мероприятия").
    :return: Отформатированное сообщение.
    """
    event_messages = []
    for event in events:
        # Форматируем дату
        formatted_date = format_date(event.get('event_date'), 'Не указано')
        event_message = (
            f"🏙 Город: {event.get('town', 'Не указано')}\n"
            f"🎭 Мероприятие: {event.get('event', 'Не указано')}\n"
            f"🎭 Описание: {event.get('description', 'Не указано')}\n"
            # f"🎭 Описание: 'Не указано')\n"
            f"📅 Дата: {formatted_date}\n"
            f"⏰ Время: {event.get('time', 'Не указано')}\n"
            f"📍 Место: {event.get('place', 'Не указано')}\n"
            f"💵 Цена: {event.get('price', 'Не указано')}\n"
            f"🔗 Ссылка: {event.get('link_to_source', 'Не указано')}\n"
            f"🎉 Статус мероприятия: {event.get('action', 'Не указано')}\n\n"            
            "-------------------------"
        )
        event_messages.append(event_message)

    # Формируем итоговое сообщение
    message = f"{title}:\n\n" + "\n".join(event_messages) + "\n Информацию уточняйте на кассе!\n"

    # Проверяем, не превышает ли сообщение лимит
    if len(message) > 4096:
        logger.info(f"Превышен лимит")
        # Если превышает, возвращаем сообщение с предложением скачать Excel
        return "Сообщение слишком длинное. Хотите скачать Excel-файл со всеми записями?"
    
    return message


def format_data_one_message(event: dict) -> str:
    """
    Форматирует список мероприятий в читаемое сообщение.

    :param events: Список мероприятий.
    :param title: Заголовок сообщения (по умолчанию "Мероприятия").
    :return: Отформатированное сообщение.
    """
    
    # Форматируем дату
    formatted_date = format_date(event.get('event_date'), 'Не указано')
    event_message = (
            f"🏙 Город: {event.get('town', 'Не указано')}\n"
            f"🎭 Мероприятие: {event.get('event', 'Не указано')}\n"
            f"🎭 Описание: {event.get('description', 'Не указано')}\n"
            f"📅 Дата: {formatted_date}\n"
            f"⏰ Время: {event.get('time', 'Не указано')}\n"
            f"📍 Место: {event.get('place', 'Не указано')}\n"
            f"💵 Цена: {event.get('price', 'Не указано')}\n"
            f"🔗 Ссылка: {event.get('link_to_source', 'Не указано')}\n"
            f"🎉 Статус мероприятия: {event.get('action', 'Не указано')}\n\n"            
            f" Информацию уточняйте на кассе!\n\n"  
        )
    
    # Формируем итоговое сообщение
    message = f"Мероприятие на {formatted_date}:\n\n{event_message}"

    # Проверяем, не превышает ли сообщение лимит
    if len(message) > 4096:
        logger.info(f"Превышен лимит")
        # Если превышает, возвращаем сообщение с предложением скачать Excel
        return None
    
    return message


from html import escape

def escape_html(text: str) -> str:
    """
    Экранирует HTML-символы в тексте.

    :param text: Исходный текст.
    :return: Текст с экранированными HTML-символами.
    """
    return escape(text)

async def generate_message_from_model(
    model: object,
    records: list = None,
    record: object = None,
    fields_to_include: list = None
) -> str:
    """
    Формирует сообщение на основе записей модели со всеми полями.

    :param model: Имя модели.
    :param records: Список записей модели (опционально).
    :param record: Одна запись модели (опционально).
    :param fields_to_include: Список полей, которые нужно включить в сообщение (опционально).
    :return: Сформированное сообщение.
    """
    # Проверяем, что передана хотя бы одна запись
    if not records and not record:
        return "Записей не найдено."

    # Получаем класс модели по имени
    # model_class = get_model_by_name(model)
    if not model:
        return f"Модель '{model}' не найдена."

    # Если передана одна запись, добавляем её в список
    if record:
        records = [record]

    # Получаем список полей модели
    inspector = inspect(model)
    columns = inspector.mapper.columns

    # Если указаны конкретные поля, фильтруем их
    if fields_to_include:
        columns = [col for col in columns if col.name in fields_to_include]

    # Формируем сообщение
    message = f"Все записи '{model}':\n\n"
    for record in records:
        record_info = ""
        for column in columns:
            # Получаем значение поля
            value = getattr(record, column.name)
            # Форматируем значение, если это дата
            if column.name == "event_date":
                value = format_date(value)
            
            # Экранируем HTML-символы
            value = escape_html(str(value))
            column_name = escape_html(column.name.capitalize())

            # Добавляем поле в сообщение
            record_info += f"<b>{column_name}:</b> {value}\n"
        record_info += "-------------------------\n"
        # Проверяем, не превышает ли сообщение лимит
        if len(message) + len(record_info) > 4096:
            # Если превышает, возвращаем сообщение с предложением скачать Excel
            return "Сообщение слишком длинное. Хотите скачать Excel-файл со всеми записями?"
        message += record_info

    return message


def create_schedule_message(shedules, town_name, section_name):
    """
    Формирует сообщение с расписанием.

    :param shedules: Список расписаний.
    :param town_name: Название города.
    :param section_name: Название раздела.
    :return: Сформированное сообщение.
    """
    if not shedules:
        return "Данных не найдено."

    # Формируем заголовок
    
    message = f"Расписание в городе {town_name} в разделе '{section_name}':\n\n"

    
    for shedule in shedules:
        shedule_info = (
            f"📍 Номер: {shedule.number}\n"
            f"📍 От: {shedule.start_place}\n"
            f"🏠 До: {shedule.finish_place}\n"
            f"⏰ Время отправления: {shedule.time_start}\n"
            f"⏰ Время прибытия: {shedule.time_finish}\n"
            f"📅 Дни: {shedule.days}\n"
            f"🔗 Ссылка: {shedule.link_to_source}\n\n"
            f" Информацию уточняйте!\n\n" 
        )
        
        # Проверяем, не превышает ли сообщение лимит
        if len(message) + len(shedule_info) > 4096:
            return None  # Сообщение превышает лимит
        
        message += shedule_info
    
    return message


def create_user_message(users: List[Any]):
    """
    Формирует сообщение с информацией о пользователях.

    :param users: Список пользователей.
    :return: Сформированное сообщение или None, если сообщение превышает лимит.
    """
    message = "Все пользователи:\n\n"
    
    for user in users:
        formatted_date = format_date(user.time_reg)

        user_info = (
            f"ID: {user.id}\n\n"
            f"👤tgId: {user.tg_id}\n"
            f"👤tgName: {user.tg_name}\n"
            f"📅 Дата начала пользования: {formatted_date}\n"
            f"⏰ Бан: {str(user.ban)}\n"
            "-------------------------\n"
        )

        
        # Проверяем, не превышает ли сообщение лимит
        if len(message) + len(user_info) > 4096:
            logger.info(f'Сообщение превышает лимит')
            return None  # Сообщение превышает лимит
        
        message += user_info
    
    return message

def create_upload_message(model_name: str, count: int) -> str:
    """
    Формирует красивое сообщение о количестве добавленных записей с эмоджи.

    :param model_name: Имя модели (например, "Event", "BusSchedule").
    :param count: Количество добавленных записей.
    :return: Текстовое сообщение с эмоджи.
    """
    # Определяем эмоджи в зависимости от модели
    if model_name == "Event":
        emoji = "🎉"  # Эмоджи для мероприятий
    elif model_name == "BusSchedule":
        emoji = "🚌"  # Эмоджи для расписания автобусов
    elif model_name == "User":
        emoji = "👤"  # Эмоджи для пользователей
    else:
        emoji = "📄"  # Эмоджи по умолчанию
    
    # Получаем русское название модели
    model_name_ru = get_model_name_ru(model_name)
    
    # Формируем сообщение
    message = (
        f"{emoji} Новые данные добавлены! {emoji}\n\n"
        f'📂 В раздел "{model_name_ru}" добавлено {count} записей\n\n'
        f"👉 Заходи в город, посмотри! 👀"
    )

    return message

def get_full_info_message(record) -> str:
    """
    Формирует сообщение с полной информацией из объекта модели.

    :param record: Объект модели, содержащий поля: town, section, name, descriptionSmall,
                  descriptionFull, schedule, coordinates, address, phone, website, nameUser, tgId, grade.
    :return: Строка с полной информацией.
    """

    message_parts = []

    # Добавляем только те поля, которые не равны None или пустой строке
    if record.name:
        message_parts.append(f"<b>Название:</b> {record.name}")  # Жирный текст
    if record.town:
        message_parts.append(f"<b>Город:</b> {record.town}")
    if record.section:
        message_parts.append(f"<b>Раздел:</b> {record.section}")
    if record.descriptionSmall:
        message_parts.append(f"<b>Описание (краткое):</b> {record.descriptionSmall}")
    if record.descriptionFull:
        message_parts.append(f"<b>Описание (полное):</b> {record.descriptionFull}")
    if record.schedule:
        message_parts.append(f"<b>График работы:</b> {record.schedule}")
    if record.coordinates:
        message_parts.append(f"<b>Координаты:</b> {record.coordinates}")
    if record.address:
        message_parts.append(f"<b>Адрес:</b> {record.address}")
    if record.phone:
        message_parts.append(f"<b>Телефон:</b> {record.phone}")
    if record.website:
        message_parts.append(f"<b>Сайт:</b> {record.website}")

    return "\n".join(message_parts).strip()



def format_message_for_send(fromWhomUser, user_name_to: str, topic: str, message_text: str) -> str:
    """
    Форматирует сообщение для отправки.

    :param user_name: Имя пользователя.
    :param topic: Тема письма.
    :param message_text: Текст письма.
    :return: Отформатированное сообщение.
    """
    return (
        f"👤 <b>От кого:</b> {fromWhomUser}\n"
        f"👤 <b>Кому:</b> {user_name_to}\n"
        f"📌 <b>Тема:</b> {topic}\n\n"
        f"📝 <b>Сообщение:</b>\n{message_text}"
    )

def get_full_info_message_data(data: dict, model_name:str=None) -> str:
    """
    Формирует сообщение с полной информацией из данных.
    """
    message_text = (
        f"Название: {data.get('name', 'Не указано')}\n\n"
        f"Город: {data.get('town', 'Не указано')}\n\n"
        f"Раздел: {data.get('section', 'Не указано')}\n\n"
        f"Краткое описание: {data.get('descriptionSmall', 'Не указано')}\n"
        f"Полное описание: {data.get('descriptionFull', 'Не указано')}\n"
        f"График работы: {data.get('schedule', 'Не указано')}\n\n"
        f"Координаты: {data.get('coordinates', 'Не указано')}\n"
        f"Адрес: {data.get('address', 'Не указано')}\n"
        f"Телефон: {data.get('phone', 'Не указано')}\n"
        f"Сайт: {data.get('website', 'Не указано')}\n\n"
        # f"ФИО: {data.get('nameUser', 'Не указано')}\n"
        # f"Telegram ID: {data.get('tgId', 'Не указано')}\n"
    )
    if model_name:
        message_text+=f'Таблица (модель): {model_name}\n\n'

    return message_text

def get_message_bookig(data: dict) -> str:
    """
    Формирует сообщение с полной информацией из данных.
    """
    #Форматируем дату в формат дд.мм.гггг
    formatted_date = format_date(data.date_booking)

    message_text = (
        # f'У Вас сделали запись!\n\n'
        f"👤 Имя: {data.userName}\n"
        f"📞 Номер телефона: {data.numberPhone}\n\n"
        f"📅 Дата: {formatted_date}\n"
        f"⏰ Время начала: {data.time_slot_start}\n"
    )
    # Добавляем параметры и вопросы, если они есть
    

    if data.params_1:  # Если параметр существует и не пустой
        message_text += f"{data.question_1}: {data.params_1}\n"
    if data.params_2:  # Если параметр существует и не пустой
         message_text += f"{data.question_2}: {data.params_2}\n"
    if data.params_3:  # Если параметр существует и не пустой
        message_text += f"{data.question_3}: {data.params_3}\n"
    if data.params_4:  # Если параметр существует и не пустой
        message_text += f"{data.question_4}: {data.params_4}\n"
    if data.params_5:  # Если параметр существует и не пустой
        message_text += f"{data.question_5}: {data.params_5}\n\n"

    # Проверяем, является ли запись на сегодня
    today = datetime.now().date()
    if data.date_booking == today:
        if data.agree==1:
            message_text += f"✅ Бронь подтверждена!\n"
        else:
            message_text += f"❌ Бронь пока не подтверждена!\n"

    return message_text