from aiogram import BaseMiddleware
from aiogram.types import Message,  CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from database.db_handlers import get_user_by_tg_id

class BanMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        # Проверяем, является ли событие сообщением или callback_query
        if not isinstance(event, Message) and not isinstance(event, CallbackQuery):
            return await handler(event, data)

        # Получаем ID пользователя
        user_id = event.from_user.id

        # Проверяем, забанен ли пользователь
        user = await get_user_by_tg_id(user_id)
        if user and user.ban:
            # Если пользователь забанен, отправляем сообщение и прерываем выполнение
            if isinstance(event, Message):
                await event.answer("⛔ Вы забанены и не можете использовать бота.")
            elif isinstance(event, CallbackQuery):
                await event.answer("⛔ Вы забанены и не можете использовать бота.", show_alert=True)
            return  # Прерываем выполнение

        # Если пользователь не забанен, продолжаем выполнение обработчика
        return await handler(event, data)



# class BanMiddleware(BaseMiddleware):
#     async def __call__(
#         self,
#         handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
#         event: TelegramObject,
#         data: Dict[str, Any],
#     ) -> Any:
#         # Проверяем, является ли событие сообщением или callback_query
#         if not isinstance(event, Message) and not hasattr(event, "from_user"):
#             return await handler(event, data)

#         # Получаем ID пользователя
#         user_id = event.from_user.id

#         # Проверяем, забанен ли пользователь
        
#         user = await get_user_by_id(user_id)
#         if user and user.ban:
#             # Если пользователь забанен, отправляем сообщение и прерываем выполнение
#             if isinstance(event, Message):
#                 await event.answer("⛔ Вы забанены и не можете использовать бота.")
#             return  # Прерываем выполнение

#         # Если пользователь не забанен, продолжаем выполнение обработчика
#         return await handler(event, data)

# class BanMiddleware(BaseMiddleware):
#     async def __call__(
#         self,
#         handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
#         event: TelegramObject,
#         data: Dict[str, Any],
#     ) -> Any:
#         # Исключаем команду /start из проверки
#         if isinstance(event, Message) and event.text == "/start":
#             return await handler(event, data)

#         # Проверяем, является ли событие сообщением или callback_query
#         if not isinstance(event, Message) and not hasattr(event, "from_user"):
#             return await handler(event, data)

#         # Получаем ID пользователя
#         user_id = event.from_user.id

#         # Проверяем, забанен ли пользователь
#         async with async_session() as session:
#             user = await get_user_by_id(session, user_id)
#             if user and user.ban:
#                 # Если пользователь забанен, отправляем сообщение и прерываем выполнение
#                 if isinstance(event, Message):
#                     await event.answer("⛔ Вы забанены и не можете использовать бота.")
#                 return  # Прерываем выполнение

#         # Если пользователь не забанен, продолжаем выполнение обработчика
#         return await handler(event, data)
    

