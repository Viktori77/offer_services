# from database.models import async_session
from sqlalchemy import select, and_, func
from database.models import User, TemplateModel, Event, SendMessagesUser, Record
from struction import combined_model_names_for_settings
from database.models import Base
from sqlalchemy import update, delete
from datetime import datetime
from sqlalchemy import inspect as sqlalchemy_inspect
from datetime import date
from database.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def get_records_for_user_in_settings(tg_id: int, model_name: str) -> bool:
    """
    Проверяем существует ли пользователь в модели.
    
    """
    model=get_model_by_name(model_name)
    # Проверяем, есть ли пользователь в базе данных
    async for session in get_db():
        result = await session.execute(select(model).where(model.tg_id == tg_id))
        user = result.scalars().first()
        if user:
            return True
        else:
            return False

async def add_or_get_user(tg_id: int, tg_name: str, time_reg: str) -> User:
    """
    Добавляет пользователя в базу данных, если его нет, или возвращает существующего.
    
    :param session: Асинхронная сессия базы данных.
    :param tg_id: ID пользователя в Telegram.
    :param tg_name: Имя пользователя в Telegram.
    :return: Объект пользователя (User).
    """
    # Проверяем, есть ли пользователь в базе данных
    async for session in get_db():
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalars().first()

        if not user:
            # Если пользователя нет, создаем новую запись
            user = User(
                tg_id=tg_id,
                tg_name=tg_name,
                time_reg=time_reg,
                ban=False  # По умолчанию пользователь не забанен
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)  # Обновляем объект, чтобы получить ID, если нужно

        return user

async def get_user_by_tg_id(user_id: int):
    try:
        async for session in get_db():
            user = await session.scalar(select(User).where(User.tg_id == user_id))
            return user
    except Exception as e:
        logger.error(f"Ошибка при получении пользователя по id: {e}")
        await session.rollback()  # Откатываем транзакцию в случае ошибки
        return False

async def update_user_ban_status(user_id: int, ban_status: bool) -> bool:
    """
    Обновляет статус бана пользователя.
    
    :param user_id: ID пользователя.
    :param ban_status: Новый статус бана (True — забанить, False — разбанить).
    :return: True, если операция успешна, иначе False.
    """
    async for session in get_db():
        try:
            # Получаем пользователя по ID
            user = await session.scalar(select(User).where(User.tg_id == user_id))
            if user:
                # Меняем статус бана
                user.ban = ban_status
                await session.commit()  # Сохраняем изменения
                return True
            else:
                logger.warning(f"Пользователь с ID {user_id} не найден.")
                return False
        except Exception as e:
            logger.error(f"Ошибка при обновлении статуса бана: {e}")
            await session.rollback()  # Откатываем транзакцию в случае ошибки
            return False

async def get_event_by_id(event_id: int) -> Event | None:
    """
    Получает полные данные о мероприятии по его ID.
    
    :param event_id: ID мероприятия.
    :return: Объект Event или None, если мероприятие не найдено.
    """
    async for session in get_db():
        # Ищем мероприятие по ID
        result = await session.execute(
            select(Event).where(Event.id == event_id)
        )
        event = result.scalar()  # Возвращаем объект Event или None
        return event

def get_prefix_models(prefix='settings', list_model_name=combined_model_names_for_settings) -> list[str]:
    """
    Возвращает список названий таблиц, начинающихся на '***_'.
    
    :return: Список названий таблиц.
    """
    # Формируем названия таблиц на основе списка моделей list_model_name
    prefix_tables = [f"{prefix}_{model_name}" for model_name in list_model_name]
    return prefix_tables


def get_model_by_name(model_name: str):
    """
    Возвращает модель по её имени.
    """
    registry = Base.registry
    for class_ in registry._class_registry.values():
        if hasattr(class_, "__tablename__") and class_.__tablename__ == model_name:
            logger.info(f"Модель {model_name} найдена.")
            return class_
    logger.error(f"Модель {model_name} не найдена в реестре.")
    raise ValueError(f"Модель {model_name} не найдена.")


async def get_models(name_list_models) -> list[str]:
    """
    Получает список всех моделей из settings_model_names, исключая те, что начинаются с 'settings_' и модель 'Users'.
    
    :return: Список названий моделей.
    """
    # Исключаем модели с префиксом 'settings_' и модель 'Users'
    filtered_models = [model for model in name_list_models 
                       if not model.startswith("settings_")]
    
    return filtered_models


async def update_event_action(event_id: int, new_action: str) -> bool:
    """
    Обновляет поле action для события с указанным ID.
    
    :param event_id: ID события.
    :param new_action: Новое значение для поля action.
    :return: True, если обновление прошло успешно, False, если событие не найдено.
    """
    async for session in get_db():
        try:
            # Проверяем, существует ли событие с таким ID
            result = await session.execute(
                select(Event).where(Event.id == event_id)
            )
            event = result.scalar()

            if event:
                # Обновляем поле action
                await session.execute(
                    update(Event)
                    .where(Event.id == event_id)
                    .values(action=new_action)
                )
                await session.commit()
                logger.info(f"Поле action для события с ID {event_id} обновлено на '{new_action}'.")
                return True
            else:
                logger.info(f"Событие с ID {event_id} не найдено.")
                return False

        except Exception as e:
            logger.error(f"Ошибка при обновлении события с ID {event_id}: {e}")
            await session.rollback()
            raise

async def get_events_by_date_and_town(event_date: date, town: str = None) -> list[str]:

    """
    Возвращает список мероприятий для указанного города и даты.

    :param session: Сессия SQLAlchemy для работы с базой данных.
    :param town: Название города.
    :param event_date: 
    :action: str = None - активно или отмена/перенос-делаем сразу фильтр, чтобы показывало только активные мероприятия. none - это для парсера. он напоминает сразу про все города, но только на завтра
    :return: Список мероприятий с полями.
    """
    async for session in get_db():
        try:
            action_filter = Event.action == "активно"
            date_filter = Event.event_date == event_date
            if town:
                town_filter = Event.town == town
                
                # Формируем запрос
                query = select(Event).where(and_(town_filter, date_filter, action_filter))
            else:
                query = select(Event).where(and_(date_filter, action_filter))

            # Выполняем запрос
            result = await session.execute(query)
            
            events = result.scalars().all()
            
            

            # Преобразуем объекты Event в словари
            events_list = [
                {
                    "id": event.id,
                    "town": event.town,
                    "event": event.event,
                    "description": event.description,
                    "event_date": event.event_date,
                    "time": event.time,
                    "link_to_source": event.link_to_source,
                    "price": event.price,
                    "place": event.place,
                    "action": event.action,
                    "grade": event.grade,
                }
                for event in events
            ]

            return events_list

        except Exception as e:
            logger.error(f"Ошибка при получении мероприятий: {e}")
            return []



async def get_events_future_by_town(town: str, event_date: str, place: str = None) -> list[dict]:
    """
    Возвращает список мероприятий для указанного города и даты.

    :param town: Название города.
    :param event_date: Дата в формате "дд.мм.гггг".
    :place: str = None - это для фильтрации по месту
    :return: Список мероприятий с полями.
    """
    async for session in get_db():
        try:
            # # Преобразуем дату в формат YYYY-MM-DD
            # date_formatted = datetime.strptime(date, "%d.%m.%y").strftime("%Y-%m-%d")
            
            # Определяем фильтры по городу и дате
            action_filter = Event.action == "активно"
            town_filter = Event.town == town
            date_filter = Event.event_date >= event_date
            if place:
                place_filter = Event.place == place

                query = select(Event).where(and_(town_filter, date_filter, action_filter, place_filter))
            else:
                # Формируем запрос
                query = select(Event).where(and_(town_filter, date_filter, action_filter))
            

            # Выполняем запрос
            result = await session.execute(query)
            
            events = result.scalars().all()
            
            # Преобразуем объекты Event в словари
            events_list = [
                {
                    "id": event.id,
                    "town": event.town,
                    "event": event.event,
                    "description": event.description,
                    "event_date": event.event_date,
                    "time": event.time,
                    "link_to_source": event.link_to_source,
                    "price": event.price,
                    "place": event.place,
                    "action": event.action,
                    "grade": event.grade,
                }
                for event in events
            ]

            return events_list

        except Exception as e:
            logger.error(f"Ошибка при получении мероприятий: {e}")
            return []

async def update_grade(model_name: str, obj_id: int, new_grade: int, grade_field_name: str = "grade") -> bool:
    """
    Универсальная функция для обновления грейда в модели.

    :param model_name: Имя модели (например, "Event").
    :param obj_id: Идентификатор объекта, который нужно обновить.
    :param new_grade: Новое значение грейда.
    :param grade_field_name: Название поля, в котором хранится грейд (по умолчанию "grade").
    :return: True, если обновление прошло успешно, иначе False.
    """
    # Получаем класс модели по имени
    model = get_model_by_name(model_name)
    if not model:
        logger.error(f"Модель '{model_name}' не найдена.")
        return False

    async for session in get_db():
        try:
            # Ищем объект по ID
            result = await session.execute(select(model).where(model.id == obj_id))
            obj = result.scalars().first()

            if obj:
                # Обновляем грейд
                setattr(obj, grade_field_name, new_grade)
                await session.commit()
                return True
            else:
                logger.error(f"Объект с ID {obj_id} не найден в модели {model_name}.")
                return False  # Если объект не найден
            return False  # Если объект не найден
        except Exception as e:
            logger.error(f"Ошибка при обновлении грейда: {e}")
            await session.rollback()
            return False
        

async def get_all_records(model_name: str, filters: dict = None):
    """
    Универсальная функция для получения всех записей в модели.

    :param model_name: Имя модели (например, "Event").
    :param filters: фильтры 
    """

    # Получаем класс модели по имени
    model = get_model_by_name(model_name)
    if not model:
        logger.error(f"Модель '{model_name}' не найдена.")
        return []

    if not filters:
        async for session in get_db():
            try:
                
                result = await session.execute(select(model))
                records = result.scalars().all()  # Получаем список объектов модели
                return records
                    
            except Exception as e:
                logger.error(f"Ошибка при получении всех записей: {e}")
                await session.rollback()
                return []
    else:
        async for session in get_db():
            try:
                additional_filters = [getattr(model, field) == value for field, value in filters.items()]
                combined_filter = and_(*additional_filters)
                # Формируем запрос
                query = select(model).where(combined_filter)

                # Выполняем запрос
                result = await session.execute(query)
                records = result.scalars().all()  # Получаем список объектов Event
                return records
                    
            except Exception as e:
                logger.error(f"Ошибка при получении всех записей: {e}")
                await session.rollback()
                return []
        
async def get_all_in_town(model_name: str, town: str, filters: dict = None):
    """
    Получает список всех строк для заданныой модели для указанного города.
    :param model_name: Имя модели (например, "Event").

    :param town: Название города.
    :param filters: Дополнительные фильтры в виде словаря {поле: значение}.
    :return: Список объектов Event со всеми полями.
    """
    # Получаем класс модели по имени
    model = get_model_by_name(model_name)
    if not model:
        logger.error(f"Модель '{model_name}' не найдена.")
        return False
    
    async for session in get_db():
        try:
            # Формируем фильтр по городу
            town_filter = model.town == town
            # Если переданы дополнительные фильтры, добавляем их
            if filters:
                additional_filters = [getattr(model, field) == value for field, value in filters.items()]
                combined_filter = and_(town_filter, *additional_filters)
            else:
                combined_filter = town_filter

            # Формируем запрос
            query = select(model).where(combined_filter)

            # Выполняем запрос
            result = await session.execute(query)
            events = result.scalars().all()  # Получаем список объектов Event

            return events
        except Exception as e:
            logger.error(f"Ошибка при получении данных: {e}")
            return []
  
async def add_or_update_record(    
    model_name: str,
    filters: dict,
    data: dict,
) -> bool:
    """
    Универсальная функция для добавления или обновления записи в таблице.

    :param session: Асинхронная сессия SQLAlchemy.
    :param model: Модель (класс таблицы).
    :param filters: Словарь с условиями для поиска существующей записи.
    :param data: Словарь с данными для добавления или обновления.
    :return: True, если операция выполнена успешно, иначе False.
    """
    # Получаем класс модели по имени
    model = get_model_by_name(model_name)
    if not model:
        logger.error(f"Модель '{model_name}' не найдена.")
        return False
    
    async for session in get_db():
        try:
            # Проверяем, существует ли запись с указанными фильтрами
            existing_record = await session.execute(
                select(model).filter_by(**filters)
            )
            existing_record = existing_record.scalar()

            if not existing_record:
                # Если запись не существует, создаем новую
                new_record = model(**data)
                session.add(new_record)
                await session.commit()
                logger.info(f"Запись добавлена в таблицу {model.__tablename__}.")
                return True
            else:
                # Если запись существует, обновляем её
                await session.execute(
                    update(model)
                    .where(model.id == existing_record.id)
                    .values(**data)
                )
                await session.commit()
                logger.info(f"Запись обновлена в таблице {model.__tablename__}.")
                return True

        except Exception as e:
            logger.error(f"Ошибка при добавлении/обновлении записи в таблице {model.__tablename__}: {e}")
            await session.rollback()
            raise


async def add_record(    
    model_name: str,
    data: dict
) -> bool:
    """
    Универсальная функция для добавления записи в таблице без обновления записей. То есть можно дублировать строки.

    :param session: Асинхронная сессия SQLAlchemy.
    :param model: Модель (класс таблицы).
    
    :param data: Словарь с данными для добавления или обновления.
    :return: True, если операция выполнена успешно, иначе False.
    """
    # Получаем класс модели по имени
    model = get_model_by_name(model_name)
    if not model:
        logger.error(f"Модель '{model_name}' не найдена.")
        return False
    
    async for session in get_db():
        try:
            # Если запись не существует, создаем новую
            new_record = model(**data)
            session.add(new_record)
            await session.commit()
            logger.info(f"Запись добавлена в таблицу {model.__tablename__}.")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при добавлении записи в таблице {model.__tablename__}: {e}")
            await session.rollback()
            raise


async def remove_record(
    model_name: str,
    filters: dict,
) -> bool:
    """
    Универсальная функция для удаления записи из таблицы.

    
    :param model_name: Модель (класс таблицы).
    :param filters: Словарь с условиями для поиска записи.
    :return: True, если запись была удалена, False, если её не было.
    """
    # Получаем класс модели по имени
    model = get_model_by_name(model_name)
    if not model:
        logger.error(f"Модель '{model_name}' не найдена.")
        return False
    
    async for session in get_db():
        try:
            # Проверяем, существует ли запись с указанными фильтрами
            record_to_delete = await session.execute(
                select(model).filter_by(**filters)
            )
            record_to_delete = record_to_delete.scalar()

            if record_to_delete:
                # Удаляем запись
                await session.delete(record_to_delete)
                await session.commit()
                logger.info(f"Запись удалена из таблицы {model.__tablename__}.")
                return True
            else:
                logger.info(f"Запись не найдена в таблице {model.__tablename__}.")
                return False

        except Exception as e:
            logger.error(f"Ошибка при удалении записи из таблицы {model.__tablename__}: {e}")
            await session.rollback()
            raise

async def remove_records_all(
    model_name: str,
    filters: dict,
) -> bool:
    """
    Универсальная функция для удаления всех записей из таблицы, соответствующих фильтрам.

    :param model_name: Модель (класс таблицы).
    :param filters: Словарь с условиями для поиска записей.
    :return: True, если записи были удалены, False, если их не было.
    """
    # Получаем класс модели по имени
    model = get_model_by_name(model_name)
    if not model:
        logger.error(f"Модель '{model_name}' не найдена.")
        return False
    
    async for session in get_db():
        try:
            # Формируем условия для удаления
            conditions = [getattr(model, key) == value for key, value in filters.items()]
            combined_conditions = and_(*conditions)

            # Удаляем все записи, соответствующие условиям
            result = await session.execute(
                delete(model).where(combined_conditions))
            await session.commit()

            # Проверяем, были ли удалены записи
            if result.rowcount > 0:
                logger.info(f"Удалено {result.rowcount} записей из таблицы {model.__tablename__}.")
                return True
            else:
                logger.info(f"Записи не найдены в таблице {model.__tablename__}.")
                return False

        except Exception as e:
            logger.error(f"Ошибка при удалении записей из таблицы {model.__tablename__}: {e}")
            await session.rollback()
            raise

def get_model_columns(model_name):
    """
    Возвращает список колонок модели SQLAlchemy.
    """
    # Получаем класс модели по имени
    model = get_model_by_name(model_name)
    inspector = sqlalchemy_inspect(model)
    
    return [column.key for column in inspector.mapper.columns]

async def get_record_count(model_name: str, town: str = None) -> int:
    """
    Возвращает количество записей в таблице, соответствующей модели.
    Если указан город, подсчитывает записи только для этого города.

    :param model_name: Имя модели.
    :param town: Название города (опционально).
    :return: Количество записей.
    """
    model = get_model_by_name(model_name)
    if not model:
        logger.warning(f"Модель '{model_name}' не найдена.")
        return 0

    async for session in get_db():
        # Базовый запрос для подсчета записей
        query = select(func.count()).select_from(model)

        # Если указан город и модель имеет атрибут 'town', добавляем фильтр
        if town and hasattr(model, 'town'):
            query = query.where(model.town == town)

        result = await session.execute(query)
        return result.scalar()


async def get_record_counts_for_models(list_model: dict, town: str = None) -> dict:
    """
    Возвращает словарь с количеством записей для каждой модели.
    Если указан город, подсчитывает записи только для этого города.

    :param list_model: Словарь с моделями и их русскими названиями.
    :param town: Название города (опционально).
    :return: Словарь вида {model_name: record_count}.
    """
    
    record_counts = {}
    for model_name in list_model.keys():
        record_counts[model_name] = await get_record_count(model_name, town)
    return record_counts


async def get_tg_ids_from_model(model_name: str) -> set[int]:
    """
    Получает множество tg_id из указанной модели.

    :param model_name: Имя модели, из которой нужно получить tg_id.
    :return: Множество tg_id.
    """
    model = get_model_by_name(model_name)
    async for session in get_db():
        try:
            query = select(model.tg_id)  # Выбираем только tg_id
            result = await session.execute(query)
            return {row[0] for row in result}  # Возвращаем множество tg_id
        except Exception as e:
            logger.error(f"Ошибка при получении данных из модели {model_name}: {e}")
            raise


async def get_record_by_id(model_name: str, record_id: int):
    """
    Получает запись по id из указанной модели.

    :param model_name: Имя модели.
    :param record_id: ID записи.
    :return: Объект записи или None, если запись не найдена.
    """
    # Получаем класс модели
    model = get_model_by_name(model_name)
    if not model:
        return None

    # Формируем запрос для получения записи по id
    async for session in get_db():
        query = select(model).where(model.id == record_id)
        result = await session.execute(query)
        return result.scalar()
    

async def get_record_count_analog(model_name: str, filters: dict = None) -> int:
    """
    Возвращает количество записей в базе данных для указанной модели с учетом фильтров.

    :param model_name: Название модели (например, "Services").
    :param filters: Словарь с фильтрами (например, {"town": "Грязи", "section": "Рестораны"}).
                   Если None, то фильтры не применяются.
    :return: Количество записей, удовлетворяющих фильтрам.
    """
    # Получаем класс модели по имени
    model_class = get_model_by_name(model_name)
    if not model_class:
        raise ValueError(f"Модель с именем {model_name} не найдена.")

    async for session in get_db():
        # Создаем запрос для подсчета записей
        query = select(func.count()).select_from(model_class)

        # Применяем фильтры, если они переданы
        if filters:
            for key, value in filters.items():
                if hasattr(model_class, key):  # Проверяем, что атрибут существует в модели
                    query = query.where(getattr(model_class, key) == value)

        # Выполняем запрос и возвращаем результат
        result = await session.execute(query)
        return result.scalar() or 0
    
async def update_message_status(record_id: int, new_status: str) -> bool:
    """
    Обновляет статус сообщения в таблице SendMessagesUser.

    :param record_id: ID записи (сообщения).
    :param new_status: Новый статус ("прочитано" или "не прочитано").
    :return: True, если обновление прошло успешно, False, если запись не найдена.
    """
    async for session in get_db():
        try:
            # Проверяем, существует ли сообщение с таким ID
            result = await session.execute(
                select(SendMessagesUser).where(SendMessagesUser.id == record_id)
            )
            message = result.scalar()

            if message:
                # Обновляем статус сообщения
                await session.execute(
                    update(SendMessagesUser)
                    .where(SendMessagesUser.id == record_id)
                    .values(status=new_status)
                )
                await session.commit()
                logger.info(f"Статус сообщения с ID {record_id} обновлен на '{new_status}'.")
                return True
            else:
                logger.info(f"Сообщение с ID {record_id} не найдено.")
                return False

        except Exception as e:
            logger.error(f"Ошибка при обновлении сообщения с ID {record_id}: {e}")
            await session.rollback()
            raise

async def get_records_for_user(model_name: str, tg_id: int):
    """
    Получение всех записей данного пользователя.

    :param model_name: Имя модели.
    :param tg_id: переданные данные пользователя.
    """
    async for session in get_db():
        model = get_model_by_name(model_name)
        result = await session.execute(
            select(model).where(model.tgId == tg_id)
        )
        
        records=result.scalars().all()
        # Преобразуем объекты в словари
        record_list = [
            {
                "id": record.id,
                "town": record.town,
                "section": record.section,
                "name": record.name,
                "descriptionSmall": record.descriptionSmall,
                "descriptionFull": record.descriptionFull,
                "schedule": record.schedule,
                "coordinates": record.coordinates,
                "address": record.address,
                "phone": record.phone,
                "website": record.website,
                "nameUser": record.nameUser,
                "tgId": record.tgId,
                "grade": record.grade,
            }
            for record in records
        ]
        return record_list
    
async def remove_table(
    model_name: str,
) -> bool:
    """
    Универсальная функция для очистки всей таблицы

    :param model: Модель (класс модели).
    
    :return: True, если запись была удалена, False, если её не было.
    """
    model = get_model_by_name(model_name)
    if not model:
        logger.error(f"Модель '{model}' не найдена.")
        return False
    
    async for session in get_db():
        try:
            # Проверяем, существует ли запись с указанными фильтрами
            record_to_delete = await session.execute(
                select(model)
            )
            record_to_delete = record_to_delete.scalar()

            if record_to_delete:
                # Удаляем запись
                await session.delete(record_to_delete)
                await session.commit()
                logger.info(f"Запись удалена из таблицы {model.__tablename__}.")
                return True
            else:
                logger.info(f"Запись не найдена в таблице {model.__tablename__}.")
                return False

        except Exception as e:
            logger.error(f"Ошибка при удалении записи из таблицы {model.__tablename__}: {e}")
            await session.rollback()
            raise

async def add_or_update_file_record(
    model_name: str,  
    file_name: str,
    file_data: bytes,
    filters: dict = None,
    additional_data: dict = None,
) -> bool:
    """
    Универсальная функция для добавления или обновления записи с файлом в таблице.

    :param session: Асинхронная сессия SQLAlchemy.
    :param model_name: Модель (класс таблицы).
    :param file_name: Имя файла.
    :param file_data: Бинарные данные файла.
    :param filters: Словарь с условиями для поиска существующей записи (опционально).
    :param additional_data: Дополнительные данные для записи (опционально).
    :return: True, если операция выполнена успешно, иначе False.
    """
    try:
        # Подготовка данных для записи
        data = {
            "file_name": str(file_name),
            "file_data": file_data,
            "createdAt": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        }
        if additional_data:
            data.update(additional_data)

        
        model=get_model_by_name(model_name)

        # Если фильтры переданы, ищем существующую запись
        async for session in get_db():
            if filters:
                existing_record = await session.execute(
                    select(model).filter_by(**filters)
                )
                existing_record = existing_record.scalar()

                if existing_record:
                    # Если запись существует, обновляем её
                    await session.execute(
                        update(model)
                        .where(model.id == existing_record.id)
                        .values(**data)
                    )
                    logger.info(f"Запись обновлена в таблице {model.__tablename__}.")
                    return True

            # Если запись не существует, создаем новую
            new_record = model(**data)
            session.add(new_record)
            await session.commit()
            logger.info(f"Запись добавлена в таблицу {model.__tablename__}.")
            return True
    except Exception as e:
            logger.error(f"Ошибка при добавлении шаблона в таблицу {model.__tablename__}.")
            await session.rollback()
            raise

async def get_template(
    model_name: str,  
) -> bool:
    """
    Функция для получения шаблона из таблицы шаблонов по названию модели.
    :param model_name: Модель .
    """
    try:
        async for session in get_db():
            result = await session.execute(
                select(TemplateModel).filter(TemplateModel.file_name == f"{model_name}.xlsx")
            )
            template = result.scalar()
            return template

    except Exception as e:
        logger.error(f"Ошибка при получении шаблона из таблицы: {e}")
        await session.rollback()
        raise

async def clear_booking_fields(model_name: str, record_id: int) -> bool:
    """
    Очищает поля userName и numberPhone в записи.

    :param model_name: Имя модели (например, "Record").
    :param record_id: ID записи, которую нужно обновить.
    :return: True, если обновление прошло успешно, иначе False.
    """
    model = get_model_by_name(model_name)
    if not model:
        logger.error(f"Модель '{model_name}' не найдена.")
        return False

    async for session in get_db():
        try:
            # Находим запись по ID
            result = await session.execute(select(model).where(model.id == record_id))
            record = result.scalars().first()

            if record:
                # Очищаем поля
                record.userName = ""
                record.numberPhone = ""
                await session.commit()
                return True
            else:
                logger.error(f"Запись с ID {record_id} не найдена.")
                return False
        except Exception as e:
            logger.error(f"Ошибка при очистке полей записи: {e}")
            await session.rollback()
            return False

async def copy_record_with_empty_user_data(model_name: str, record_id: int) -> bool:
    """
    Копирует запись, но оставляет поля userName и numberPhone пустыми.

    :param model_name: Имя модели (например, "Record").
    :param record_id: ID записи, которую нужно скопировать.
    :return: True, если копирование прошло успешно, иначе False.
    """
    model = get_model_by_name(model_name)
    if not model:
        logger.error(f"Модель '{model_name}' не найдена.")
        return False

    async for session in get_db():
        try:
            # Находим запись по ID
            result = await session.execute(select(model).where(model.id == record_id))
            original_record = result.scalars().first()

            if not original_record:
                logger.error(f"Запись с ID {record_id} не найдена.")
                return False

            # Создаем новую запись на основе оригинальной
            new_record = model(
                tgId=original_record.tgId,
                model=original_record.model,
                offerId=original_record.offerId,
                date_booking=original_record.date_booking,
                time_slot_start=original_record.time_slot_start,
                time_slot_finish=original_record.time_slot_finish,
                number_of_seats=original_record.number_of_seats,
                params_1=original_record.params_1,
                params_2=original_record.params_2,
                params_3=original_record.params_3,
                params_4=original_record.params_4,
                params_5=original_record.params_5,
                question_1=original_record.question_1,
                question_2=original_record.question_2,
                question_3=original_record.question_3,
                question_4=original_record.question_4,
                question_5=original_record.question_5,
                userName="",  # Оставляем пустым
                numberPhone="",  # Оставляем пустым
                url_record_my=original_record.url_record_my,
            )

            # Добавляем новую запись в базу данных
            session.add(new_record)
            await session.commit()
            return True

        except Exception as e:
            logger.error(f"Ошибка при копировании записи: {e}")
            await session.rollback()
            return False
        

async def get_numberPhone(numberPhone: str) -> bool:
    """
    Ищем номер телефона в таблице User

    :numberPhone: Переданный номер телефона.
    
    :return: True, если нашли, иначе False.
    """
    
    async for session in get_db():
        try:
            # Находим запись по ID
            result = await session.execute(select(User).where(User.numberphone == numberPhone))
            record = result.scalar_one_or_none()

            if record:
                logger.info(f"Запись с numberPhone {numberPhone} найдена.")
                return True
            else:
                logger.info(f"Запись с numberPhone {numberPhone} не найдена.")
                return False
        except Exception as e:
            logger.error(f"Ошибка при получении номера телефона: {e}")
            await session.rollback()
            return False
        
async def update_numberphone(tg_id: int,numberphone: str) -> bool:
    """
    Обновляет номер телефона.
    
    :param tg_id: ID пользователя.
    :param numberphone: Новое значение для поля numberphone.
    :return: True, если обновление прошло успешно, False, если событие не найдено.
    """
    async for session in get_db():
        try:
            # Проверяем, существует ли событие с таким ID
            result = await session.execute(
                select(User).where(User.tg_id == tg_id)
            )
            event = result.scalar()

            if event:
                # Обновляем поле action
                await session.execute(
                    update(User)
                    .where(User.tg_id == tg_id)
                    .values(numberphone=numberphone)
                )
                await session.commit()
                logger.info(f"Поле numberphone для пользователя с tg_id {tg_id} обновлено на '{numberphone}'.")
                return True
            else:
                logger.info(f"Пользователь с tg_id {tg_id} не найден.")
                return False

        except Exception as e:
            logger.error(f"Ошибка при обновлении номера телефона у пользователя с тг id {tg_id}")
            await session.rollback()
            raise

async def update_book_agree_status(record_id: int, agree_status: bool) -> bool:
    """
    Обновляет статус подтверждения брони.
    
    :param record_id: ID брони.
    :param agree_status: Новый статус agree (True — подверждена, False — не подтверждена).
    :return: True, если операция успешна, иначе False.
    """
    async for session in get_db():
        try:
            # Получаем пользователя по ID
            record = await session.scalar(select(Record).where(Record.id == record_id))
            if record:
                # Меняем статус бана
                record.agree = agree_status
                await session.commit()  # Сохраняем изменения
                return True
            else:
                logger.warning(f"Бронь с ID {record_id} не найден.")
                return False
        except Exception as e:
            logger.error(f"Ошибка при обновлении статуса бана: {e}")
            await session.rollback()  # Откатываем транзакцию в случае ошибки
            return False