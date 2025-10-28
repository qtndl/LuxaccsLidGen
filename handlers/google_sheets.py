import gspread_asyncio
import gspread
from google.oauth2.service_account import Credentials
import os

def get_creds():
    creds = Credentials.from_service_account_file(rf'{os.getcwd()}\config\google_keys.json')
    scoped = creds.with_scopes([
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ])
    return scoped

# Создаем глобальный менеджер клиента
agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)

async def add_record_to_sheet(
    spreadsheet_name: str,
    worksheet_name: str,
    values: list
):
    """
    Добавляет запись в указанную таблицу и лист
    Первый столбец автоматически заполняется порядковым номером

    Args:
        spreadsheet_name (str): Название Google таблицы
        worksheet_name (str): Название листа в таблице
        values (list): Список значений для записи в строку (без порядкового номера)
    """
    try:
        # Авторизуемся
        agc = await agcm.authorize()

        # Открываем таблицу по названию
        spreadsheet = await agc.open(spreadsheet_name)

        try:
            # Открываем лист по названию
            worksheet = await spreadsheet.worksheet(worksheet_name)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = await spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=26)
            new_worksheet_values = [
                'п/п',
                'tg_id',
                'Контакт',
                'Дата регистрации',
                'Закрыт',
                'Ссылка на чат'
            ]
            await worksheet.append_row(new_worksheet_values)


        # Получаем все данные из листа
        all_data = await worksheet.get_all_values()

        # Определяем следующий порядковый номер
        if not all_data:
            # Если лист пустой, начинаем с 1
            next_number = 1
        else:
            # Ищем максимальный номер в первом столбце (игнорируем заголовки если они есть)
            max_number = 0
            for i, row in enumerate(all_data):
                if i == 0 and any(cell.strip() for cell in row):
                    # Пропускаем возможную строку заголовков
                    continue
                if row and row[0].isdigit():
                    current_num = int(row[0])
                    if current_num > max_number:
                        max_number = current_num

            next_number = max_number + 1

        # Добавляем порядковый номер в начало списка значений
        values_with_id = []
        values_with_id.append(next_number)
        for value in values:
            values_with_id.append(value)

        # Добавляем новую строку с данными
        result = await worksheet.append_row(values_with_id)

        # print(f"✅ Данные успешно добавлены (ID: {next_number}): {values}")
        return result

    except Exception as e:
        print(f'❌ Ошибка с таблицами: {e}')
        raise

async def find_and_update_by_column_name(
    spreadsheet_name: str,
    worksheet_name: str,
    search_column_name: str,  # Название столбца для поиска
    search_value: str,
    update_column_name: str,  # Название столбца для обновления
    new_value: str
) -> bool:
    """
    Находит строку по значению в указанном столбце и обновляет ячейку в другом столбце
    используя названия столбцов вместо букв

    Args:
        spreadsheet_name: Название таблицы
        worksheet_name: Название листа
        search_column_name: Название столбца для поиска
        search_value: Значение для поиска
        update_column_name: Название столбца для обновления
        new_value: Новое значение для записи

    Returns:
        bool: True если обновление успешно, False если строка не найдена
    """
    try:
        # Авторизуемся и открываем таблицу/лист
        agc = await agcm.authorize()
        spreadsheet = await agc.open(spreadsheet_name)
        worksheet = await spreadsheet.worksheet(worksheet_name)

        # Получаем все данные для анализа структуры
        all_data = await worksheet.get_all_values()

        if not all_data:
            print("❌ Таблица пуста")
            return False

        # Первая строка - заголовки столбцов
        headers = all_data[0]

        # Находим индексы нужных столбцов
        try:
            search_col_index = headers.index(search_column_name) + 1  # +1 т.к. gspread индексирует с 1
            update_col_index = headers.index(update_column_name) + 1
        except ValueError as e:
            print(f"❌ Столбец не найден: {e}")
            available_columns = [h for h in headers if h]
            print(f"📋 Доступные столбцы: {available_columns}")
            return False

        # Ищем строку с нужным значением в указанном столбце
        found_row = None
        for row_idx, row in enumerate(all_data[1:], start=2):  # start=2 т.к. пропускаем заголовок
            if row_idx - 1 < len(all_data) and search_col_index - 1 < len(row):
                if str(row[search_col_index - 1]).strip() == str(search_value).strip():
                    found_row = row_idx
                    break

        if not found_row:
            print(f"❌ Значение '{search_value}' не найдено в столбце '{search_column_name}'")
            return False

        # Обновляем ячейку
        await worksheet.update_cell(found_row, update_col_index, new_value)

        # print(f"✅ Строка {found_row}, столбец '{update_column_name}' обновлен: '{new_value}'")
        return True

    except Exception as e:
        print(f"❌ Ошибка при поиске и обновлении: {e}")
        return False