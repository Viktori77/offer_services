from datetime import datetime, timedelta
from typing import List, Dict, Any
from struction import combined_model_names_for_users
from datetime import date
from sqlalchemy import func
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_current_time() -> date:
    """
    Возвращает текущее время в формате "YYYY-MM-DD %H:%M:%S".

    :return: Текущее время в виде строки.
    """
    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return datetime.now() 

def get_today_date_dmy() -> date:
    """
    Возвращает сегодняшнюю дату в формате дд.мм.гг.
    :return: Сегодняшняя дата в виде даты.
    """
    today = datetime.now()
    today.strftime("%Y-%m-%d")
    return func.date(today)


def get_tomorrow_date() -> date:
    """
    Возвращает завтрашнюю дату в виде даты".

    """
    # tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    tomorrow_date = (datetime.now() + timedelta(days=1))
    return func.date(tomorrow_date)

def format_date(date_obj, default: str = "Не указано") -> str:
    """
    Преобразует дату из формата yyyy-mm-dd в формат дд.мм.гггг.

    :param date_obj: Объект даты (datetime.date, datetime.datetime или строка в формате yyyy-mm-dd).
    :param default: Значение по умолчанию, если дата не указана или некорректна.
    :return: Отформатированная дата в формате дд.мм.гггг или значение по умолчанию.
    """

    # Если date_obj уже является строкой, возвращаем её
    if isinstance(date_obj, str):
        try:
            # Пробуем преобразовать строку в объект datetime
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d %H:%M:%S")  # Формат с временем
        except ValueError:
            try:
                date_obj = datetime.strptime(date_obj, "%Y-%m-%d")  # Формат без времени
            except ValueError:
                logger.info(f'Дата не преобразовалась и вернулась строкой')
                return date_obj  # Если формат не совпадает, возвращаем исходное значение

    # Если date_obj является объектом datetime, преобразуем его в date
    if isinstance(date_obj, datetime):
        date_obj = date_obj.date()

    # Если date_obj является объектом date, форматируем его
    if isinstance(date_obj, date):
        return date_obj.strftime("%d.%m.%Y")  # Форматируем в дд.мм.гггг

    # Если date_obj не является ни строкой, ни объектом date/datetime, возвращаем значение по умолчанию
    logger.info(f'Дата не преобразовалась и вернулась объектом, а не строкой')
    return default

#Функция для экранирования
def escape_markdown(text: str) -> str:
    """
    Экранирует символы, которые могут быть интерпретированы как Markdown.
    """
    if not isinstance(text, str):
        text = str(text)  # Преобразуем в строку, если это не строка
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f"\\{char}")
    return text

# Вспомогательная функция для удаления "settings_" из имени модели
def remove_settings_prefix(model_name: str) -> str:
    """
    Удаляет префикс 'settings_' из названия модели.
    
    :param model_name: Название модели с префиксом 'settings_'.
    :return: Название модели без префикса.
    """
    return model_name.replace("settings_", "")


def get_filters_for_model(model_name: str, row_data: dict) -> dict:
    """
    Возвращает фильтры для поиска существующей записи в зависимости от модели.

    :param model_name: Имя модели.
    :param row_data: Данные из строки Excel-файла.
    :return: Словарь с фильтрами.
    """
    filters = {}

    if model_name == "Town":
        filters = {"town": row_data.get("town")}  # Пример для модели Town
    elif model_name == "Event":
        filters = {
            "town": row_data.get("town"),
            "event": row_data.get("event"),
            "event_date": row_data.get("event_date"),
        }  # Пример для модели Event
    elif model_name == "EventCheck":
        filters = {
            "event_date": row_data.get("event_date"),
            "time": row_data.get("time"),
            "town": row_data.get("town"),
            "place": row_data.get("place"),
        }  # Пример для модели Event
    elif model_name == "User":
        filters = {
            "event_date": row_data.get("event_date"),
            "tg_id": row_data.get("tg_id"),
        }  # Пример для модели Event
    elif model_name == "BusSchedule":
        filters = {
            "town": row_data.get("town"),
            "start_place": row_data.get("start_place"),
            "finish_place": row_data.get("finish_place"),
            "time_start": row_data.get("time_start"),
            "days": row_data.get("days"),
        } 
    else:
        filters = {
            "town": row_data.get("town"),
            "section": row_data.get("section"),
            "name": row_data.get("name"),
            
        }

    return filters

def prepare_model_data(model_name: str, raw_data: dict) -> dict:
    """
    Формирует данные для добавления/обновления записи в зависимости от модели.

    :param model_name: Имя модели (например, "Event", "BusSchedule").
    :param raw_data: Исходные данные.
    :return: Словарь с данными, подготовленными для модели.
    """
    try:
        if model_name == "Event":
            # Формируем данные для модели Event
            prepared_data = {
                "id": raw_data.get("id"),  # Добавляем ID
                "town": raw_data.get("town"),  # Используем правильные ключи
                "event": raw_data.get("event"),
                "description": raw_data.get("description"), 
                "event_date": raw_data.get("event_date"),
                "time": raw_data.get("time"),
                "link_to_source": raw_data.get("link_to_source"),
                "price": raw_data.get("price"),
                "place": raw_data.get("place"),
                "action": raw_data.get("action", "активно"),  # Статус по умолчанию
            }
            
            return prepared_data
        elif model_name == "BusSchedule":
            # Формируем данные для модели BusSchedule
            prepared_data = {
                "id": raw_data.get("id"),  # Добавляем ID
                "town": raw_data.get("town"),
                "section": raw_data.get("section"),
                "number": raw_data.get("number"),
                "start_place": raw_data.get("start_place"),
                "finish_place": raw_data.get("finish_place"),
                "time_start": raw_data.get("time_start"),
                "time_finish": raw_data.get("time_finish"),
                "days": raw_data.get("days", "Ежедневно"),  # Значение по умолчанию
                "link_to_source": raw_data.get("link_to_source", "-"),  # Значение по умолчанию
            }
            return prepared_data
        elif model_name == "User":
            # Формируем данные для модели User
            prepared_data = {
                "id": raw_data.get("id"),
                "tg_id": raw_data.get("tg_id"),
                "tg_name": raw_data.get("tg_name"),
                "time_reg": raw_data.get("time_reg"),
                "ban": raw_data.get("ban"),
            }
            return prepared_data
        elif model_name == "Record":
            prepared_data = {
                # "id": raw_data.get("id"),
                # "tgId": raw_data.get("tgId"),
                # "model": raw_data.get("model"),
                # "offerId": raw_data.get("offerId"),
                "date_booking": raw_data.get("date_booking"),
                "time_slot_start": raw_data.get("time_slot_start"),
                "time_slot_finish": raw_data.get("time_slot_finish"),
                "number_of_seats": raw_data.get("number_of_seats"),
                "params_1": raw_data.get("params_1"),
                "params_2": raw_data.get("params_2"),
                "params_3": raw_data.get("params_3"),
                "params_4": raw_data.get("params_4"),
                "params_5": raw_data.get("params_5"),
                "question_1": raw_data.get("question_1"),
                "question_2": raw_data.get("question_2"),
                "question_3": raw_data.get("question_3"),
                "question_4": raw_data.get("question_4"),
                "question_5": raw_data.get("question_5"),
                "userName": raw_data.get("userName"),
                "numberPhone": raw_data.get("numberPhone"),
                "url_record_my": raw_data.get("url_record_my"),
            }
            return prepared_data
        else:
            # Формируем данные для аналогичных моделей
            # Формируем данные для аналогичных моделей
            prepared_data = {
                "id": raw_data.get("id"),
                "town": raw_data.get("town"),
                "section": raw_data.get("section"),
                "name": raw_data.get("name"),
                "descriptionSmall": raw_data.get("descriptionSmall"),
                "descriptionFull": raw_data.get("descriptionFull"),
                "schedule": raw_data.get("schedule"),
                "coordinates": raw_data.get("coordinates"),
                "address": raw_data.get("address"),
                "phone": raw_data.get("phone"),
                "website": raw_data.get("website"),
                "nameUser": raw_data.get("nameUser"),
                "tgId": raw_data.get("tgId"),
                "grade": raw_data.get("grade"),
            }
            return prepared_data
        
        
    except Exception as e:
        # Логируем ошибку (если нужно)
        logger.error(f"Ошибка при подготовке данных для модели {model_name}: {e}")
        # Возвращаем пустой словарь в случае ошибки
        return {}

def convert_orm_to_dict(records: List[Any], model_name: str) -> List[Dict[str, Any]]:
    """
    Преобразует список объектов SQLAlchemy в список словарей в зависимости от модели.

    :param records: Список объектов SQLAlchemy.
    :param model_name: Имя модели (например, "Event", "BusSchedule").
    :return: Список словарей с данными.
    """
    if model_name == "Event":
        return [
            {
                "town": record.town,
                "event": record.event,
                "description": record.description,
                "event_date": record.event_date,
                "time": record.time,
                "place": record.place,
                "price": record.price,
                "link_to_source": record.link_to_source,
                "action": record.action,
            }
            for record in records
        ]
    elif model_name == "BusSchedule":
        return [
            {
                "town": record.town,
                "section": record.section,
                "number": record.number,
                "start_place": record.start_place,
                "finish_place": record.finish_place,
                "time_start": record.time_start,
                "time_finish": record.time_finish,
                "days": record.days,
                "link_to_source": record.link_to_source,
            }
            for record in records
        ]
    elif model_name == "User":
        return [
            {
                "id": record.id,
                "tg_id": record.tg_id,
                "tg_name": record.tg_name,
                "time_reg": record.time_reg,
                "ban": record.ban,
            }
            for record in records
        ]
    else:
        # Если модель не поддерживается, возвращаем пустой список
        return []


def get_section_name_ru(section_key: str, section: str) -> str:
    """
    Преобразует ключ раздела в русское название.
    
    :param section_key: Ключ раздела (например, "FromGryaziBusStation").
    :return: Русское название раздела.
    """
    
    return section.get(section_key, "Неизвестный раздел")

def get_model_name_ru(model_name: str) -> str:
    """
    Преобразует модель в русское название.
    
    :param section_key: Ключ раздела (например, "FromGryaziBusStation").
    :return: Русское название раздела.
    """
    
    return combined_model_names_for_users.get(model_name, model_name)


def create_filters_and_data_for_Event(town, event_title, event_date, event_time, event_description, link_to_source, price, place, action, grade):

    filters = {
        "town": town,
        "event": event_title,
        "event_date": event_date,
        "time": str(event_time),
    }

    data = {
        "town": town,
        "event": event_title,
        "description": event_description[:350],
        "event_date": event_date,
        "time": str(event_time),
        "link_to_source": link_to_source,
        "price": str(price),
        "place": place,
        "action": action,
        "grade": grade,
    }

    return filters, data

def create_filters_and_data_for_img(town, file_name, base_url, image_data):

    filters = {
        "town": town,
        "file_name": file_name,
    }

    data = {
        "town": town,
        "site": base_url,
        "file_name": file_name,
        "file_data": image_data # Бинарные данные изображения
    }

    return filters, data


def get_places_from_events(events: List[dict]) -> Dict[str, List[int]]:
    """
    Группирует мероприятия по месту проведения.

    :param events: Список мероприятий.
    :return: Словарь, где ключ — место проведения, значение — список id мероприятий.
    """
    places = {}
    for event in events:
        place = event['place']
        if place in places:
            places[place].append(event['id'])  # Добавляем id мероприятия
        else:
            places[place] = [event['id']]  # Создаем список id для места
    return places


days_translate={
    "Monday": "ПН",
    "Tuesday": "ВТ",
    "Wednesday": "СР",
    "Thursday": "ЧТ",
    "Friday": "ПТ",
    "Saturday": "СБ",
    "Sunday": "ВС"
}

def get_day_week(date_obj: date):
    """
    Возвращаем день недели на русском

    """
    
    # Получаем день недели (например, "Понедельник")
    day_of_week = date_obj.strftime("%A")
   
    day_week=days_translate.get(day_of_week,day_of_week)
    return day_week