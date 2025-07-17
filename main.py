import asyncio
from bots_starting import bot_tg
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import commands, generation_commands, event_commands, account_commands


# <--------------- / Main / --------------->
async def main() -> None:
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(commands.router)
    dp.include_router(generation_commands.router)
    dp.include_router(event_commands.router)
    dp.include_router(account_commands.router)

    await bot_tg.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot_tg)


# <--------------- / Run / --------------->
if __name__ == '__main__':
    print('Bot is ready')
    asyncio.run(main())
