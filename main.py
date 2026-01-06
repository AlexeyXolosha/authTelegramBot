import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from app.config import config

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout
    )

async def main():
    setup_logging()

    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()

    logging.info("Бот запущен и готов к работе")
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try: 
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")