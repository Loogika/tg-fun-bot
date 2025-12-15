import asyncio
from aiogram import Bot, Dispatcher
from bot.router import setup_routers
from config import TELEGRAM_BOT_TOKEN
from logger import setup_logger

# Подключаем логирование
logger = setup_logger()

async def main():
    # Создаём объекты бота и диспетчера (диспетчер направляет апдейты в хендлеры)
    bot = Bot(TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    #Устанавливаем роутеры для диспетчера(наборы хендлеров для сообщений и )
    setup_routers(dp)

    logger.info("Бот запускается...")
    try:
        #Попытка запуска бота
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