from sqlalchemy import BigInteger, String, Boolean, INTEGER, LargeBinary, Date, Numeric, Text, Float, Integer

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy.ext.asyncio import AsyncAttrs
from typing import Optional
from datetime import date

from struction import analog_model_names

class Base(AsyncAttrs, DeclarativeBase):
  pass


class User(Base):
  __tablename__="User"

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  
  tg_id: Mapped[int] = mapped_column(BigInteger)
  tg_name: Mapped[str] = mapped_column(String(150)) 
  time_reg: Mapped[str] = mapped_column(String(150))
  ban: Mapped[bool] = mapped_column(Boolean, default=False)
  numberphone: Mapped[str] = mapped_column(String(15), nullable=True)

class Town(Base):
  __tablename__="Town"

  id: Mapped[int] = mapped_column(primary_key=True)    
  town: Mapped[str] = mapped_column(String(150)) 
  grade: Mapped[int] = mapped_column(default=1)

  def __repr__(self):
        return f"Town(id={self.id}, town='{self.town}', grade={self.grade})"

class Place_settings(Base):
  __tablename__="Place_settings"

  id: Mapped[int] = mapped_column(primary_key=True)    
  town: Mapped[str] = mapped_column(String(150)) 
  place_name: Mapped[str] = mapped_column(String(150))
  tgId: Mapped[int] = mapped_column(BigInteger)
  
class Event(Base):
  __tablename__="Event"

  id: Mapped[int] = mapped_column(primary_key=True) 
  town:  Mapped[str] = mapped_column(String(150))  # Город
  event: Mapped[str] = mapped_column(String(150))  # Мероприятие
  description: Mapped[str] = mapped_column(String(350))  # Описание мероприятие
#   date: Mapped[str] = mapped_column(String(35)) # Дата
  event_date: Mapped[date] = mapped_column(Date) 
  time: Mapped[str] = mapped_column(String(35)) # Время
  link_to_source: Mapped[str] = mapped_column(String(150)) #Ссылка на источник
  price: Mapped[str] = mapped_column(String(150)) #Ссылка на источник
  place: Mapped[str] = mapped_column(String(150)) #Ссылка на источник
  action: Mapped[str] = mapped_column(String(150)) #/активно или отмена/перенос
  grade: Mapped[int] = mapped_column(default=1)

class EventCheck(Base):
  __tablename__="EventCheck"
    #Модель нужна, чтобы из парсеров по событиям добавлять сюда его результаты, чтобы админ мог потом только нужные строки добавить в основную таблицу Event
  id: Mapped[int] = mapped_column(primary_key=True) 
  town:  Mapped[str] = mapped_column(String(150))  # Город
  event: Mapped[str] = mapped_column(String(150))  # Мероприятие
  description: Mapped[str] = mapped_column(String(350))  # Описание мероприятие
#   date: Mapped[str] = mapped_column(String(35)) # Дата
  event_date: Mapped[date] = mapped_column(Date)
  time: Mapped[str] = mapped_column(String(35)) # Время
  link_to_source: Mapped[str] = mapped_column(String(150)) #Ссылка на источник
  price: Mapped[str] = mapped_column(String(150)) #Ссылка на источник
  place: Mapped[str] = mapped_column(String(150)) #Ссылка на источник
  action: Mapped[str] = mapped_column(String(150)) #/активно или отмена/перенос
  grade: Mapped[int] = mapped_column(default=1)



class BusSchedule(Base):
  __tablename__="BusSchedule"

  id: Mapped[int] = mapped_column(primary_key=True) 
  town:  Mapped[str] = mapped_column(String(150))  # Город
  section: Mapped[str] = mapped_column(String(150))  # Раздел
  number:  Mapped[str] = mapped_column(String(150), nullable=True, default="")  # Номер маршрута
  start_place:  Mapped[str] = mapped_column(String(150))  # Откуда идет
  finish_place: Mapped[str] = mapped_column(String(150))  # Куда идет
  time_start: Mapped[str] = mapped_column(String(150), nullable=True, default="") # Время старта
  time_finish: Mapped[Optional[str]] = mapped_column(String(150), nullable=True, default="")
  days: Mapped[str] = mapped_column(String(150),default="Ежедневно") # Дни, когда ездеет
  link_to_source: Mapped[Optional[str]] = mapped_column(String(150)) #Ссылка на источник
  


def create_analog_model(model_name: str) -> type:
    """
    Создает модель с полями: Название, Описание, график работы, координаты, адрес, телефон, сайт, Кто предложил, грейд.

    :param model_name: Имя модели (ключ из словаря analog_model_names).
    :return: Класс модели.
    """
    class_name = model_name  # Используем имя модели как имя класса
    table_name = f"{model_name}"  # Имя таблицы

    # Создаем класс модели
    model_class = type(
        class_name,
        (Base,),
        {
            "__tablename__": table_name,
            "id": mapped_column(INTEGER, primary_key=True, autoincrement=True),
            "town": mapped_column(String(150)),  # Название
            "section": mapped_column(String(150)),  # Название
            "name": mapped_column(String(150)),  # Название
            "descriptionSmall": mapped_column(String(500)),  # Описание краткое
            "descriptionFull": mapped_column(String(1500)),  # Описание полное
            "schedule": mapped_column(String(150)),  # График работы
            "coordinates": mapped_column(String(150)),  # Координаты
            "address": mapped_column(String(150)),  # Адрес
            "phone": mapped_column(String(50)),  # Телефон
            "website": mapped_column(String(150)),  # Сайт
            "nameUser": mapped_column(String(150)),  # Кто предложил
            "tgId": mapped_column(BigInteger, default=1),  # Кто предложил
            "grade": mapped_column(INTEGER, default=1),  # Грейд (по умолчанию 1)
        }
    )
    return model_class

# Динамически создаем модели для analog_model_names
for model_name in analog_model_names:
    model_class = create_analog_model(model_name)
    globals()[model_class.__name__] = model_class  # Добавляем класс в глобальное пространство имен

# Динамически создаем резервные модели для analog_model_names, чтобы предложения от юзеров записывались в эти модели сначала
for model_name in analog_model_names:
    model_class = create_analog_model(f'{model_name}Reserv')
    globals()[model_class.__name__] = model_class  # Добавляем класс в глобальное пространство имен

#Модель для хранения сообщений от пользователя Админу (для меня это входящие сообщения)
class SendMessagesUser(Base):
  __tablename__="SendMessagesUser"

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  
  tgId: Mapped[int] = mapped_column(BigInteger) #От кого пришло письма
  topic: Mapped[str] = mapped_column(String(150)) #Тема письма
  body: Mapped[str] = mapped_column(String(150))#Тело письма(текст)
  createdAt: Mapped[str] = mapped_column(String(150))#Когда создано
  status: Mapped[str] = mapped_column(String(150))#Статус письма (прочитано/не прочитано)


#Модель для хранения сообщений от Админа (для меня это исходящие, отправленные)
class SendMessagesAdmin(Base):
  __tablename__="SendMessagesAdmin"

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  
  tgId: Mapped[int] = mapped_column(BigInteger) #Кому отправляется письмо
  topic: Mapped[str] = mapped_column(String(150)) #Тема письма
  body: Mapped[str] = mapped_column(Text)
  createdAt: Mapped[str] = mapped_column(String(150))#Когда создано
  status: Mapped[str] = mapped_column(String(150))#Статус письма (новость/ответ)

# Модель для хранения информации о картинке с кинотеатра
class ImageModel(Base):
    __tablename__ = 'ImageModel'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    town:  Mapped[str] = mapped_column(String(150))  # Город
    site: Mapped[str] = mapped_column(String(150))  # Раздел
    file_name:  Mapped[str] = mapped_column(String(150))  # Откуда идет
    file_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)  # Бинарные данные файла (JPEG)

# Модель для хранения информации о картинке с кинотеатра
class TemplateModel(Base):
    __tablename__ = 'TemplateModel'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_name:  Mapped[str] = mapped_column(String(150))  # Откуда идет
    file_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)  # Бинарные данные файла (xlsx)
    createdAt: Mapped[str] = mapped_column(String(150)) #Когда создано

class Record(Base):
  __tablename__="Record"

  id: Mapped[int] = mapped_column(primary_key=True) 
  tgId: Mapped[int] = mapped_column(BigInteger) # Кто создал расписание
  # town:  Mapped[str] = mapped_column(String(150))  # Город
  model:  Mapped[str] = mapped_column(String(150)) # модель
  # section:  Mapped[str] = mapped_column(String(150))  # раздел
  offerId: Mapped[int] = mapped_column(BigInteger) # id предложения
  date_booking: Mapped[date] = mapped_column(Date)
  time_slot_start: Mapped[str] = mapped_column(String(35)) # Время старта
  time_slot_finish: Mapped[str] = mapped_column(String(35)) # Время финиша
  number_of_seats: Mapped[int] = mapped_column(BigInteger, nullable=True, default=1)
  params_1: Mapped[str] = mapped_column(String(350), nullable=True, default="")
  params_2: Mapped[str] = mapped_column(String(350), nullable=True, default="")
  params_3: Mapped[str] = mapped_column(String(350), nullable=True, default="")
  params_4: Mapped[str] = mapped_column(String(350), nullable=True, default="")
  params_5: Mapped[str] = mapped_column(String(350), nullable=True, default="")
  question_1: Mapped[str] = mapped_column(String(350), nullable=True, default="")
  question_2: Mapped[str] = mapped_column(String(350), nullable=True, default="")
  question_3: Mapped[str] = mapped_column(String(350), nullable=True, default="")
  question_4: Mapped[str] = mapped_column(String(350), nullable=True, default="")
  question_5: Mapped[str] = mapped_column(String(350), nullable=True, default="")
  userName: Mapped[str] = mapped_column(String(350), nullable=True, default="") # Кто забронировал дату
  numberPhone: Mapped[str] = mapped_column(String(350), nullable=True, default="") # Номер телефона в формате +79042848969
  url_record_my: Mapped[str] = mapped_column(String(350), nullable=True, default="")
  agree: Mapped[bool] = mapped_column(Boolean, default=False)
  

# async def async_main():
#   async with engine.begin() as conn:
#     await conn.run_sync(Base.metadata.create_all)  
