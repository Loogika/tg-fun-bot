import json
import logging
import time
from typing import Optional, List

import gspread
from google.oauth2.service_account import Credentials

from config import SPREADSHEET_ID, SERVICE_ACCOUNT_FILE

logger = logging.getLogger("bot")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

HEADERS = ["user_id", "username", "created_at", "packs_json"]


def _init_sheet():
    logger.info("Инициализация Google Sheets...")
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
    )
    gclient = gspread.authorize(creds)
    sh = gclient.open_by_key(SPREADSHEET_ID)
    ws = sh.sheet1
    logger.info("Google Sheets инициализированы успешно.")
    return ws


sheet = _init_sheet()


def _ensure_headers() -> None:
    """
    Если в таблице нет заголовков, вставляет HEADERS первой строкой.
    Логика определения простая:
    - если первая строка совпадает с HEADERS -> ок
    - если в A1 число (похоже на user_id) -> считаем, что заголовков нет
    - если таблица пустая -> добавляем заголовки
    """
    try:
        first_row = sheet.row_values(1)  # может быть []
        if not first_row:
            sheet.insert_row(HEADERS, 1)
            return

        normalized = [c.strip() for c in first_row[: len(HEADERS)]]
        if normalized == HEADERS:
            return

        a1 = (first_row[0] or "").strip()
        if a1.isdigit():
            sheet.insert_row(HEADERS, 1)
            logger.info("Добавили заголовки в таблицу (insert_row в первую строку).")
            return

        # Если A1 не число и заголовки не совпали — оставляем как есть,
        # чтобы не сломать таблицу неожиданной вставкой.
        logger.warning(
            "Первая строка не похожа на данные (user_id) и не совпадает с HEADERS. "
            "Заголовки не вставлял автоматически."
        )
    except Exception:
        logger.exception("Ошибка при проверке/вставке заголовков.")


def _col_index(header: str) -> int:
    """
    Возвращает 1-based индекс колонки по заголовку.
    Требует, чтобы заголовки уже существовали.
    """
    row1 = sheet.row_values(1)
    if not row1 or row1[: len(HEADERS)] != HEADERS:
        raise RuntimeError("Заголовки не инициализированы или отличаются от ожидаемых.")
    return HEADERS.index(header) + 1


def _find_user_row(user_id: int) -> Optional[int]:
    """
    Ищет строку с user_id в колонке user_id.
    Возвращает номер строки (1-based) или None.
    """
    str_user_id = str(user_id)
    col = sheet.col_values(_col_index("user_id"))
    # col[0] = header
    for i, val in enumerate(col[1:], start=2):
        if val.strip() == str_user_id:
            return i
    return None


def add_user_if_not_exists(user_id: int, username: Optional[str]) -> None:
    _ensure_headers()

    row = _find_user_row(user_id)
    if row is not None:
        # опционально обновим username, если он пустой
        if username:
            username_col = _col_index("username")
            current = (sheet.cell(row, username_col).value or "").strip()
            if not current:
                sheet.update_cell(row, username_col, username)
        return

    sheet.append_row([
        str(user_id),
        username or "",
        time.strftime("%Y-%m-%d %H:%M:%S"),
        "[]",  # packs_json
    ])


def get_all_user_ids() -> List[int]:
    _ensure_headers()
    col = sheet.col_values(_col_index("user_id"))
    result: List[int] = []

    for value in col[1:]:  # пропускаем header
        value = (value or "").strip()
        if not value:
            continue
        try:
            result.append(int(value))
        except ValueError:
            pass

    return result


def get_user_packs(user_id: int) -> List[str]:
    _ensure_headers()
    row = _find_user_row(user_id)
    if row is None:
        return []

    packs_col = _col_index("packs_json")
    raw = (sheet.cell(row, packs_col).value or "").strip()
    if not raw:
        return []

    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except Exception:
        logger.warning("packs_json битый JSON у user_id=%s: %r", user_id, raw)
        return []


def add_pack_to_user(user_id: int, pack_name: str) -> List[str]:
    _ensure_headers()
    add_user_if_not_exists(user_id, None)

    row = _find_user_row(user_id)
    if row is None:
        return []

    pack_name = (pack_name or "").strip()
    if not pack_name:
        return get_user_packs(user_id)

    packs = get_user_packs(user_id)

    # уникализация с сохранением порядка
    if pack_name not in packs:
        packs.append(pack_name)

    packs_col = _col_index("packs_json")
    sheet.update_cell(row, packs_col, json.dumps(packs, ensure_ascii=False))
    logger.info("GS: add_pack_to_user ok user_id=%s", user_id)
    return packs
