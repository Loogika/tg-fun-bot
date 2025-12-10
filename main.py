import asyncio
from aiogram import Bot, Dispatcher
from bot.router import setup_routers
from config import TELEGRAM_BOT_TOKEN
from logger import setup_logger

logger = setup_logger()

async def main():
    bot = Bot(TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    setup_routers(dp)
    logger.info("Бот запускается...")

    try:
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        logger.info("Polling отменён")
    finally:
        await bot.session.close()
        logger.info("Бот завершил работу")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Остановка через Ctrl+C")