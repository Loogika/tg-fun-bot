import time
import logging
import gspread
from google.oauth2.service_account import Credentials
from config import SPREADSHEET_ID, SERVICE_ACCOUNT_FILE

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

logger.info("Инициализация Google Sheets...")
creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)
gclient = gspread.authorize(creds)
sheet = gclient.open_by_key(SPREADSHEET_ID).sheet1
logger.info("Google Sheets инициализированы успешно.")


def add_user_if_not_exists(user_id: int, username: str | None) -> None:
    str_user_id = str(user_id)
    col_user_ids = sheet.col_values(1)

    if str_user_id in col_user_ids:
        return

    sheet.append_row([
        str_user_id,
        username or "",
        time.strftime("%Y-%m-%d %H:%M:%S")
    ])


def get_all_user_ids() -> list[int]:
    col_user_ids = sheet.col_values(1)
    result = []

    for value in col_user_ids:
        try:
            result.append(int(value))
        except ValueError:
            pass

    return result