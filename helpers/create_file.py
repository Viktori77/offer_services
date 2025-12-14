from openpyxl import Workbook

async def create_excel_file(data: list, headers: list, filename: str, sheet_title: str = "Данные") -> str:
    """
    Создает Excel-файл с данными.

    :param data: Список данных (каждый элемент — это список значений для строки).
    :param headers: Заголовки столбцов.
    :param filename: Имя файла для сохранения.
    :param sheet_title: Название листа в Excel.
    :return: Имя сохраненного файла.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_title

    # Добавляем заголовки
    ws.append(headers)

    # Добавляем данные
    for row in data:
        ws.append(row)

    # Сохраняем файл
    wb.save(filename)
    return filename

