<!-- # Telegram-бот для аналитики по видео на основе задач на естественном языке

## Основные функции

- принимает текстовые сообщения от пользователя бота на русском (естественный язык);
- по этому тексту строит запрос к данным;
- возвращает пользователю ответ - одно число (счётчик, сумму или прирост в зависимости от запроса).

## Технологии:

- Язык программирования — **Python**
- База — **PostgreSQL**
- Telegram-бот — **aiogram**

## Переменные окружения

Проект использует файл `.env` для хранения конфиденциальных данных. Пример содержимого файла:

```env
TELEGRAM_TOKEN=YOUR_TELEGRAM_BOT_TOKEN

LOGIN=LOGIN_DB
PASSWORD=PASSWORD_DB
HOST=localhost
DB=DB

OPENAI_API_KEY=YOUR_OPENAI_API_KEY

JSON_FILE_PATH=data/videos.json
```

- `TELEGRAM_TOKEN` - токен Telegram-бота.
- `LOGIN` - логин в базе данных.
- `PASSWORD` - пароль в базе данных.
- `HOST` - номер хоста в базе данных.
- `DB` - имя базы данных.
- `OPENAI_API_KEY` - ключ для работы с моделью LLM.
- `JSON_FILE_PATH` - путь к video.json.

## Установка проекта

1. **Склонируйте репозиторий**:

   ```bash
   git clone https://github.com/Viktori77/video_analitics_product_bot.git
   cd video_analitics_product_bot
   ```

2. **Не забудьте установить и активировать виртуальное окружение.**

Для windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. **Установите зависимости**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Создайте файл `.env`** с вашими настройками (см. раздел "Переменные окружения").

5. **Добвавьте в проект файл videos.json, создав папку data. Запишите путь к файлу в файле .env .**

6. **Задайте токен Telegram-бота:**

```text
1. В боте BotFather нажимать "Старт".
2. Создать новый бот
3. Задать имя бота.
4. Задать имя_bot.
5. Получаем токен!
```

7. **Создайте базу данных Postgresql:**

```bash
   CREATE DATABASE name_db;
   \c name_db;
   GRANT ALL ON schema public TO user;
```

8. **Запустите приложение**:
   ```bash
   python main.py
   ```

## Зависимости

Проект использует следующие зависимости:

```text
SQLAlchemy==2.0.45
python-decouple==3.8
asyncpg==0.31.0
openai==2.11.0
aiogram==3.23.0
python-dotenv==1.2.1
```

## Распознавание естественного языка:

Используется бесплатная модель LLM.

## Подход распознавания:

```
Запрос:
- вопрос от пользователя,
- промпт с таблицами бд и правилами создания запроса в бд.
Смотри файл prompt_templates.py

``` -->
