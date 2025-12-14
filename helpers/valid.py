import re
from datetime import datetime

def is_valid_date(date_str: str) -> bool:
    """
    Проверяет, соответствует ли строка формату YYYY-MM-DD.
    """
    # Регулярное выражение для формата YYYY-MM-DD
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    
    # Проверяем, соответствует ли строка шаблону
    if not re.match(pattern, date_str):
        return False
    
    # Пытаемся преобразовать строку в объект datetime
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False
    

def is_valid_time(time_str: str) -> bool:
    """
    Проверяет, соответствует ли строка формату ЧЧ:ММ.
    """
    pattern = r"^\d{2}:\d{2}$"
    if not re.match(pattern, time_str):
        return False
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False
    

def is_valid_price(price_str: str) -> bool:
    """
    Проверяет, является ли цена числом или строкой "бесплатно".
    """
    if price_str.lower() == "бесплатно":
        return True
    try:
        float(price_str)
        return True
    except ValueError:
        return False
