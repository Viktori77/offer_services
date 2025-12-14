from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup)
from utils import  remove_settings_prefix, get_day_week
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from typing import List
from struction import all_town_name
from datetime import date, datetime
from bot.create_bot import url_recording
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

main_admin = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Посмотреть предложения", callback_data="offers_new")],
    [InlineKeyboardButton(text="Действия с данными", callback_data="do_data")],
    [InlineKeyboardButton(text="Сообщения", callback_data="do_messages")],
    [InlineKeyboardButton(text="Кнопки для user", callback_data="do_users")],
], row_width=6)


do_admin_kb_data=InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Добавить данные", callback_data="section_for_add")],
    [InlineKeyboardButton(text="Загрузить данные", callback_data="section_for_upload")],
    [InlineKeyboardButton(text="Удалить данные", callback_data="section_for_remove")], 
    [InlineKeyboardButton(text="Изменить статус события", callback_data="update_action")],
    [InlineKeyboardButton(text="Изменить грейд показа", callback_data="update_grade")],
    [InlineKeyboardButton(text="Забанить или разбанить пользователя", callback_data="ban_action")],
    [InlineKeyboardButton(text="Посмотреть", callback_data="section_for_get")],
    [InlineKeyboardButton(text="Посмотреть всех юзеров", callback_data="view_User_all")],
    [InlineKeyboardButton(text="Добавить шаблон", callback_data="addTemplate")],
], row_width=8)

do_admin_kb_messages = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Написать", callback_data="send_messages")],
    [InlineKeyboardButton(text="Входящие", callback_data="mes_SendMessagesUser")],
    [InlineKeyboardButton(text="Отправленные", callback_data="mes_SendMessagesAdmin")],
], row_width=3)

main_users = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🏙️ Зайти в город...", callback_data="choose_сity")],
    [InlineKeyboardButton(text="✅ Предложить добавить", callback_data="offers_suggest")],
    [InlineKeyboardButton(text="📁 Mои предложения", callback_data="MyOffers")],
    [InlineKeyboardButton(text="✔️ Mои брони/записи", callback_data="MyBooking")],
    [InlineKeyboardButton(text="✏️ Связаться с админом", callback_data="send_messages")],
], row_width=3)

# Создаем клавиатуру для выбора получателя
send_admin_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Всем", callback_data="send_to_all")],
    [InlineKeyboardButton(text="Одному", callback_data="send_to_one")],
])

def create_towns_keyboard(towns: list[str], prefix: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками для каждого города.
    
    :param towns: Список названий городов.
    :return: Объект InlineKeyboardMarkup.
    """
    # Создаем список кнопок
    buttons = [
        [InlineKeyboardButton(text=town, callback_data=f"town_{prefix}_{town}")] for town in towns
    ]

    # Создаем клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons, row_width=4)
    return keyboard


def create_settings_keyboard(models: list[str], settings_model_names) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками для моделей, начинающихся на 'settings'.
    
    :param models: Список названий моделей.
    :return: Объект InlineKeyboardMarkup.
    """
    buttons = []  # Создаем пустой список для кнопок


    for model in models:
        # Убираем "settings_" из названия модели
        model_name_without_settings = remove_settings_prefix(model)
        # Получаем перевод названия модели из словаря
        model_name_translate = settings_model_names.get(model_name_without_settings, model_name_without_settings) 
        
        # Создаем кнопку и добавляем ее в список
        button = [InlineKeyboardButton(text=model_name_translate, callback_data=f"settings_{model}")]
        buttons.append(button)
    
    # Добавляем кнопку "Отключить все уведомления" в начало списка
    buttons.append([InlineKeyboardButton(
                                        text="ВЫКЛ/ВКЛ все уведомления", 
                                        callback_data="disable_all_notifications"
                                        )
                    ])

    # Возвращаем клавиатуру со всеми кнопками
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def create_on_off_keyboard(model_name: str, event_id: int=None) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками "ВКЛ" и "ВЫКЛ".

    :param model_name: Название модели (таблицы).
    :event_id: для получения места
    :return: Объект InlineKeyboardMarkup.
    """
    if event_id:
        buttons = [
        [InlineKeyboardButton(text="ВКЛ", callback_data=f"toggle_{model_name}_on_{event_id}")],
        [InlineKeyboardButton(text="ВЫКЛ", callback_data=f"toggle_{model_name}_off_{event_id}")],
    ]
    else:
        buttons = [
            [InlineKeyboardButton(text="ВКЛ", callback_data=f"toggle_{model_name}_on")],
            [InlineKeyboardButton(text="ВЫКЛ", callback_data=f"toggle_{model_name}_off")],
        ]
        # Проверяем, является ли модель городом
        if model_name in all_town_name:
            # Добавляем кнопку "Выбрать Место" как отдельную строку
            buttons.append([InlineKeyboardButton(text="Выбрать Место", callback_data=f"selectLocation_{model_name}")])


    return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_models_keyboard(models: list[str], all_model_names: dict, prefix:str, record_counts: dict = None) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками для каждой модели.
    
    :param models: Список названий моделей.
    :param all_model_names: Словарь с переводами названий моделей.
    :return: Объект InlineKeyboardMarkup.
    """
    if record_counts:
        buttons = [
            [InlineKeyboardButton(text=f"{all_model_names.get(model, model)} ({record_counts.get(model, 0)})", 
            callback_data=f"{prefix}_{model}")]
            for model in models
        ]
        logger.info(f'record_counts.get(model, 0): {record_counts}')
    else:
        # Создаем список кнопок с переведенными названиями моделей
        buttons = [
            [InlineKeyboardButton(text=all_model_names.get(model, model), callback_data=f"{prefix}_{model}")]
            for model in models
        ]
        logger.info(f'prefix: {prefix}')
    

    # Создаем клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def create_action_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру с кнопками для выбора статуса.
    
    :return: Объект ReplyKeyboardMarkup.
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="активно")],
            [KeyboardButton(text="отменено")],
            [KeyboardButton(text="перенесено")],
        ],
        resize_keyboard=True,  # Клавиатура подстраивается под размер экрана
        one_time_keyboard=True,  # Клавиатура скрывается после выбора
    )
    return keyboard

def create_towns_text_keyboard(towns: list[str]):
    """
    Создает клавиатуру с кнопками городов.
    
    :param towns: Список названий городов.
    :return: Объект клавиатуры.
    """
    builder = ReplyKeyboardBuilder()
    for town in towns:
        builder.button(text=town)  # Добавляем кнопку с названием города
    builder.adjust(2)  # Указываем, сколько кнопок будет в одном ряду (например, 2)
    return builder.as_markup(resize_keyboard=True)  # Возвращаем клавиатуру


def create_ban_unban_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками "Забанить" и "Разбанить".
    
    :return: Объект InlineKeyboardMarkup.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Забанить", callback_data="ban_user")],
        [InlineKeyboardButton(text="Разбанить", callback_data="unban_user")],
    ])
    return keyboard


def create_models_for_users_keyboard(town: str, list_model: dict, record_counts: dict) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками для выбора модели (например, "Мероприятия").
    В текст кнопки добавляется количество записей в модели.

    :param town: Название выбранного города.
    :param list_model: Словарь с моделями и их русскими названиями.
    :param record_counts: Словарь с количеством записей для каждой модели.
    :return: Объект InlineKeyboardMarkup.
    """
    buttons = [
        [InlineKeyboardButton(text=f"{model_rus} ({record_counts.get(model, 0)})", callback_data=f"model_{model}_{town}")]
        for model, model_rus in list_model.items()
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def create_event_periods_keyboard(town: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками для выбора периода мероприятий.

    :param town: Название выбранного города.
    :return: Объект InlineKeyboardMarkup.
    """
    buttons = [
        [InlineKeyboardButton(text="На сегодня", callback_data=f"event_today_{town}")],
        [InlineKeyboardButton(text="На завтра", callback_data=f"event_tomorrow_{town}")],
        [InlineKeyboardButton(text="Будущие мероприятия", callback_data=f"event_future_{town}")],
        [InlineKeyboardButton(text="Посмотреть Все мероприятия", callback_data=f"Event_all_{town}")]
        
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_download_excel_keyboard(town: str, model_name: str, section: str = None) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой для скачивания Excel-файла.
    """
    builder = InlineKeyboardBuilder()
    if section:
        builder.button(text="Скачать Excel", callback_data=f"download_excel_{town}_{model_name}_{section}")
    else:
        builder.button(text="Скачать Excel", callback_data=f"download_excel_{town}_{model_name}")

    return builder.as_markup()


def create_section_keyboard(prefix: str, section: dict, town: str, model_name: str = "BusSchedule", counts: dict = None) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру с кнопками для выбора раздела.
    Кнопки отображаются в столбец (одна под другой).

    :param prefix: Префикс для callback_data.
    :param section: Словарь, где ключи — идентификаторы разделов, а значения — названия кнопок.
    :param town: Название города.
    :param model_name: Название модели.
    :param counts: Словарь, где ключ — это идентификатор раздела, а значение — количество записей.
                  Если None, количество записей не отображается.
    :return: Объект InlineKeyboardMarkup с кнопками.
    """
    buttons = []
    for key, value in section.items():
        # Формируем текст кнопки
        if counts is not None:
            button_text = f"{value} ({counts.get(key, 0)})"  # Текст кнопки с количеством записей
        else:
            button_text = f"{value}"  # Текст кнопки без количества записей

        # Создаем кнопку
        button = [InlineKeyboardButton(
            text=button_text,
            callback_data=f'{prefix}_{key}_{town}_{model_name}'  # Callback_data
        )]
        buttons.append(button)

    # Создаем инлайн-клавиатуру и добавляем кнопки
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def create_list_in_analog_models_keyboard(records, model_name):
    """
    Создает клавиатуру с кнопками на основе переданных записей.

    :param records: Список записей, каждая из которых содержит name.
    :param model_name: Название модели, используемое в callback_data.
    :return: Объект InlineKeyboardMarkup с кнопками.
    """
    buttons = [
        [InlineKeyboardButton(
            text=f"{record.name}" + (f" - {record.descriptionSmall}" if record.descriptionSmall else ""),  # Текст кнопки
            callback_data=f"details_{model_name}_{record.id}"  # Callback_data
        )]
        for record in records
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_list_in_messages_keyboard(records, model_name):
    """
    Создает клавиатуру с кнопками на основе переданных записей по сообщениям.

    :param records: Список записей, каждая из которых содержит name.
    :param model_name: Название модели, используемое в callback_data.
    :return: Объект InlineKeyboardMarkup с кнопками.
    """
    buttons = [
        [InlineKeyboardButton(
            text=f"{record.status}: {record.topic} - {record.tgId}",  # Текст кнопки
            callback_data=f"messageDetail_{model_name}_{record.id}"  # Callback_data
        )]
        for record in records
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Создаем клавиатуру с кнопками "Верно" и "Редактировать"
confirmation_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Верно")],  # Первая строка с кнопкой "Верно"
        [KeyboardButton(text="Редактировать")],  # Вторая строка с кнопкой "Редактировать"
    ],
    resize_keyboard=True,  # Автоматически изменять размер клавиатуры
    one_time_keyboard=True,  # Скрыть клавиатуру после выбора
)

def create_approval_keyboard(model_name: str, record_id: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками "Согласовать" и "Отменить".

    :param model_name: Название модели.
    :param record_id: Идентификатор записи.
    :return: Объект InlineKeyboardMarkup с кнопками.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Согласовать",
                    callback_data=f"approve_{model_name}_{record_id}"
                ),
                InlineKeyboardButton(
                    text="Отменить",
                    callback_data=f"reject_{model_name}_{record_id}"
                ),
            ]
        ]
    )
    return keyboard

def create_read_or_answer_keyboard(model_name: str,record_id: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками "Прочитано" и "Ответить".

    :param model_name: Название модели.
    :param record_id: Идентификатор записи - сообщения.
    :return: Объект InlineKeyboardMarkup с кнопками.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Прочитано",
                    callback_data=f"read_{model_name}_{record_id}"
                ),
                InlineKeyboardButton(
                    text="Ответить",
                    callback_data=f"answer_{model_name}_{record_id}"
                ),
            ]
        ]
    )
    return keyboard


def my_offers_main_kb(approved_count: int, pending_count: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для &laquo;Mои предложения&raquo; с кнопками:
    [Согласованные (X)] [На согласовании (Y)]
    """
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"Согласованные ({approved_count})",
                callback_data="myoffers_approved"
            ),
            InlineKeyboardButton(
                text=f"На согласовании ({pending_count})",
                callback_data="myoffers_pending"
            )
        ]
    ])
    return kb

def my_offers_records_kb(records: List[dict], is_reserv: bool) -> InlineKeyboardMarkup:
    """
    Генерирует клавиатуру со списком записей пользователя.
    :param records: список словарей вида {"model_name": ..., "record_id": ..., "button_text": ...}
    :param is_reserv: True, если это записи из резервных моделей
    """
    buttons = []
    for r in records:
        buttons.append([InlineKeyboardButton(
            text=r["button_text"],
            callback_data=f"myoffers_item:{r['model_name']}:{r['record_id']}:{r['record_tgId']}"
        )])
    # Можно добавить кнопку "Назад" или "Закрыть" в конце
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb

def my_offers_detail_kb(model_name: str, record_id: int, record_tgId: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для конкретной записи: [Редактировать] [Удалить] [Личный кабинет]
    """
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            # InlineKeyboardButton(text="Редактировать", 
            #                      callback_data=f"myoffers_edit:{model_name}:{record_id}"),
        InlineKeyboardButton(text="Удалить", 
                            callback_data=f"myoffers_delete:{model_name}:{record_id}:{record_tgId}"),
        InlineKeyboardButton(text="Личный кабинет", 
                            callback_data=f"my_room:{model_name}:{record_id}:{record_tgId}")
        ]
    ])
    return kb

def confirm_delete_kb(model_name: str, record_id: int, record_tgId: int) -> InlineKeyboardMarkup:
    """
    Кнопки подтверждения/отмены удаления
    """
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да, удалить", 
                callback_data=f"myoffers_confirm_delete:{model_name}:{record_id}:{record_tgId}"),
            InlineKeyboardButton(text="Нет, отменить", 
                callback_data="myoffers_cancel_delete")
        ]
    ])
    return kb

def create_parsers_keyboard(parsers: dict, town: str):
    """
    Создает клавиатуру с кнопками парсеров для выбранного города.
    
    :param parsers: Словарь с парсерами для города.
    :param town: Название города.
    :return: Объект клавиатуры.
    """
    builder = InlineKeyboardBuilder()
    for parser_key, parser_data in parsers.items():
        builder.button(text=parser_data["name"], callback_data=f"parser_{town}_{parser_key}")
    builder.adjust(1)  # Указываем, сколько кнопок будет в одном ряду
    return builder.as_markup()

def create_plus_event_keyboard(event_id: int):
    """
    Создание клавиатуры для добавления мероприятий из таблицы для проверки в основную базу 
    """
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Добавить", 
                callback_data=f"plus_event_{event_id}"),
            InlineKeyboardButton(text="Скрыть запись", 
                callback_data=f"hide_event_{event_id}"),
        ]
    ])
    return kb

def create_filters_events_keyboard(town: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками "Календарь" и "Место проведения".

    :return: Объект InlineKeyboardMarkup с кнопками.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Календарь",
                    callback_data=f"filter_date_{town}"
                ),
                InlineKeyboardButton(
                    text="Место проведения",
                    callback_data=f"filter_place_{town}"
                ),
            ]
        ]
    )
    return keyboard

def create_events_one_place_keyboard(places: dict, town: str, action: str=None) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками мест проведения мероприятий. 
    :action - для настроек
    :return: Объект InlineKeyboardMarkup с кнопками.
    """
    keyboard = InlineKeyboardBuilder()
    for place, event_ids in places.items():
        # В callback_data передаем id мероприятий через запятую
        place_name_adress=place.split('(')
        place_name=place_name_adress[0]
        # event_ids[0]
        if action:
            model_name="Place"
            callback_data=f"settings_{model_name}_{event_ids[0]}_{town}"
        else:
            callback_data=f"place_{event_ids[0]}_{town}"

        keyboard.add(InlineKeyboardButton(
            text=f"({len(event_ids)}) {place_name}",  # Количество мероприятий в скобках
            callback_data=callback_data  # Передаем id мероприятия одного первого
            # callback_data=f"place_{event_id}"
            
        ))
    keyboard.adjust(1)  # Одна кнопка в строке
    
    return keyboard

def create_suggest_downloads_send_kb(model_name: str, record_id: int = None, record_tgId: int = None) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками для скачивания образца, отправление файла админу. После Предложить добавить - меропиятия и расписание автобусов

    :param model_name: Модель, которая пришла - это мероприятия или расписание автобусов.
    :return: Объект InlineKeyboardMarkup.
    """
    buttons = [
        [InlineKeyboardButton(text="Скачать шаблон", callback_data=f"template_{model_name}")],
        [InlineKeyboardButton(text="Отправить на согласование", callback_data=f"sendForApproval")],
    ]

    url = f'{url_recording}/{model_name}/{record_id}'
    # url = "https://dolgopolovav.ru"

    # Если переданы record_id и record_tgId, изменяем клавиатуру
    if record_id is not None and record_tgId is not None:
        buttons = [
            [InlineKeyboardButton(text="Инструкция", callback_data=f"instruction_{url}")],
            [InlineKeyboardButton(text="Сайт с расписанием", url=url)],
            [InlineKeyboardButton(text="Скачать шаблон", callback_data="template_recording")],
            [InlineKeyboardButton(text="Отправить", callback_data=f"pushRecording_{model_name}_{record_id}_{record_tgId}")],
            [InlineKeyboardButton(text="Расписание", callback_data=f"viewMyRecording_{model_name}_{record_id}_{record_tgId}")],
            [InlineKeyboardButton(text="Брони/записи", callback_data=f"filtersDataBookings_{model_name}_{record_id}_{record_tgId}")],
        ]
    # buttons = [
    #     [InlineKeyboardButton(text="Скачать шаблон", callback_data=f"template_{model_name}")],
    #     [InlineKeyboardButton(text="Отправить на согласование", callback_data=f"sendForApproval_{model_name}")],
    # ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)



def create_events_one_days_keyboard(events_by_date: dict, town: str=None, model_name: str=None, record_id: str=None, record_tgId: str=None) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками дат проведения мероприятий. 
    :action - для настроек
    :return: Объект InlineKeyboardMarkup с кнопками.
    """
    keyboard = InlineKeyboardBuilder()
    # Добавляем кнопки для каждой даты
    for event_date, events_list in events_by_date.items():
        # Преобразуем строку даты в объект datetime
        date_obj = datetime.strptime(event_date, "%d.%m.%Y")

        # Получаем день недели на русском языке(например, "Понедельник")
        day_of_week = get_day_week(date_obj)

        # Формируем текст кнопки: "Дата (День недели)"
        if town:
            button_text = f"{event_date} ({day_of_week})"
            callback_data=f"show_events_{town}_{event_date}"
        else:
            button_text = f"{event_date} ({day_of_week})"
            callback_data=f"viewAllBookings_{model_name}_{record_id}_{record_tgId}_{event_date}"

        keyboard.button(
            text=button_text,
            callback_data=callback_data
        )

    keyboard.adjust(2)  # Одна кнопка в строке
    
    return keyboard

def create_action_get_record_kb(model_name: str, record_id: int, record_tgId: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками для просмотра или скачивания своего расписания

    :param model_name: Модель, которая пришла - это мероприятия или расписание автобусов.
    :return: Объект InlineKeyboardMarkup.
    """
    buttons = [
        # [InlineKeyboardButton(text="Посмотреть здесь", callback_data=f"getRecords_{model_name}_{record_id}_{record_tgId}")],
        [InlineKeyboardButton(text="Скачать файлом", callback_data=f"downloadRecord_{model_name}_{record_id}_{record_tgId}")],
        [InlineKeyboardButton(text="Удалить всё расписание", callback_data=f"removeRecord_{model_name}_{record_id}_{record_tgId}")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_remove_record_kb(model_name: str, record_id: int, record_tgId: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру при удалении всего расписания для брони

    :param model_name: Модель, которая пришла - это мероприятия или расписание автобусов.
    :return: Объект InlineKeyboardMarkup.
    """
    buttons = [
        # [InlineKeyboardButton(text="Посмотреть здесь", callback_data=f"getRecords_{model_name}_{record_id}_{record_tgId}")],
        [InlineKeyboardButton(text="Удалить, да!", callback_data=f"removeYes_{model_name}_{record_id}_{record_tgId}")],
        [InlineKeyboardButton(text="Загрузить себе файл", callback_data=f"downloadRecord_{model_name}_{record_id}_{record_tgId}")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def create_booking_keyboard(records: list) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками для записей.

    :param records: Список записей.
    :return: Объект InlineKeyboardMarkup.
    """
    builder = InlineKeyboardBuilder()
    today = date.today()

    for record in records:
        # Проверяем, что есть userName и date_booking сегодняшняя или будущая
        if record.userName and record.date_booking >= today:
            button_text = f"{record.time_slot_start} - {record.userName}"
            builder.button(text=button_text, callback_data=f"bookingInfo_{record.id}_{record.tgId}")

    builder.adjust(2)  # Располагаем кнопки по одной в строке
    return builder.as_markup()

def create_records_keyboard(model_name: str, record_id: int, record_tgId: int ) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками дат - время -клиент 
    :action - для настроек
    :return: Объект InlineKeyboardMarkup с кнопками.
    """
    # Создаем клавиатуру с кнопками действий
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        # [InlineKeyboardButton(text="Связаться с пользователем", callback_data=f"contactUser_{record_id}")],
        [InlineKeyboardButton(text="Отменить запись/бронь", callback_data=f"cancelRecord_{model_name}_{record_id}_{record_tgId}")],
        [InlineKeyboardButton(text="Удалить запись/бронь", callback_data=f"myoffers_delete:{model_name}:{record_id}:{record_tgId}")],
        [InlineKeyboardButton(text="Добавить такой же слот (окошко)", callback_data=f"addRecord_{model_name}_{record_id}_{record_tgId}")],
    ])
    
    return keyboard

def create_yes_or_no_cancel_booking_keyboard(model_name: str, record_id: int, record_tgId: int ) -> InlineKeyboardMarkup:
    """
    Создаем клавиатуру с подтверждением отмены брони/записи 
    :action - для настроек
    :return: Объект InlineKeyboardMarkup с кнопками.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Да, отменить", callback_data=f"confirmCancel_{model_name}_{record_id}_{record_tgId}")],
                [InlineKeyboardButton(text="Нет, оставить", callback_data="myoffers_cancel_delete")]
            ])
    
    
    
    return keyboard

def booking_kb(model_name: str, record_id: int) -> InlineKeyboardMarkup:
    """
    Создаем клавиатуру с кнопкой записаться/посмотреть расписание
    :action - для настроек
    :return: Объект InlineKeyboardMarkup с кнопками.
    """
    # Формируем URL
    # url = f'{url_recording}/{model_name}/{record_id}'
    url = "https://dolgopolovav.ru"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Записаться/Посмотреть расписание", url=url)]
            ])
    
    return keyboard


def create_bookings_my(count_booking: int = 0) -> InlineKeyboardMarkup:
    """
    Создаем клавиатуру с кнопками: Привязать номер телефона и Посмотреть брони/записи
    count_booking: количесвто броней, если есть
    
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Привязать номер телефона", callback_data=f"numberphoneAdd")],
                [InlineKeyboardButton(text=f"Брони/записи ({count_booking})", callback_data="viewsBooking")]
            ])
    
    return keyboard

# from aiogram.utils.keyboard import InlineKeyboardBuilder
# from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def info_booking(records: list) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками для отображения бронирований.

    :param records: Список записей из таблицы Record.
    :return: InlineKeyboardMarkup с кнопками.
    """
    builder = InlineKeyboardBuilder()

    for record in records:
        # Формируем текст кнопки: дата - время - модель
        button_text = f"{record.date_booking} - {record.time_slot_start} - {record.model}"
        
        # Добавляем кнопку с callback_data = id записи
        builder.button(text=button_text, callback_data=f"booking_{record.id}")
    
    builder.adjust(1)  # Располагаем кнопки в один столбец
    return builder.as_markup()

def cancel_booking(record_id: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками дат - время -клиент 
    
    :return: Объект InlineKeyboardMarkup с кнопками.
    """
    # Создаем клавиатуру с кнопками действий
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        
        [InlineKeyboardButton(text="Отменить запись/бронь", callback_data=f"cancelRecord_{record_id}")],
        
    ])
    
    
    return keyboard

def user_yes_or_no_cancel_booking_keyboard(record_id: int) -> InlineKeyboardMarkup:
    """
    Создаем клавиатуру с подтверждением отмены брони/записи 
    :action - для настроек
    :return: Объект InlineKeyboardMarkup с кнопками.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Да, отменить", callback_data=f"confirmCancel_{record_id}")],
                [InlineKeyboardButton(text="Нет, оставить", callback_data="myoffers_cancel_delete")]
            ])
    
    
    
    return keyboard

def yes_or_cancel_booking(record_id: int) -> InlineKeyboardMarkup:
    """
    Создаем клавиатуру с подтверждением Да или Отмена 
    
    :return: Объект InlineKeyboardMarkup с кнопками.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Подтвердить", callback_data=f"yesBooking_{record_id}")],
                [InlineKeyboardButton(text="Отменить", callback_data=f"confirmCancel_{record_id}")]
            ])
     
    return keyboard