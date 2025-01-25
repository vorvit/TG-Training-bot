import asyncio
from aiogram import Bot, Dispatcher
from config_reader import config
from handlers import router

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()
dp.include_router(router)

async def main():
    print('Бот запущен!')
    await dp.start_polling(bot)


if __name__ == "__main__":
    
    try:
        asyncio.run(main())
    finally:
        asyncio.run(bot.session.close())
