from aiogram.utils import executor
from create_bot import dp
from handlers import client

async def on_startup(_):
    print('Бот вышел в онлайн')

async def on_shutdown(_):
    client.connection.close()
    print('Бот завершил работу')

client.register_handlers_client(dp)

while True:
    try:
        executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)   
        break
    except Exception as e:
      print(e)