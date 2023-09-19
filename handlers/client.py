from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import md
from config import API_TOKEN, admin, logging
from create_bot import bot, ThrottlingMiddleware, rate_limit
from keyboards import kb_client, kb_menu, kb_adm, kb_back, fun
from file_paths import file_paths
from buttons import buttons
import re, os, requests
import sqlite3

REQUEST_COUNT = 0

connection = sqlite3.connect('data.db')
q = connection.cursor()

class st(StatesGroup):
	item_mailing_list = State()
	item_answer_to_user = State()
	item_ban_list_add = State()
	item_ban_list_delete = State()

def join(chat_id):
    q.execute("SELECT * FROM users WHERE user_id=?", (chat_id,))
    result = q.fetchall()
    if len(result) == 0:
        q.execute("INSERT INTO users (user_id, block) VALUES (?, 0)",(chat_id,))
        connection.commit()

async def send_message(user_id, text, kb):
    await bot.send_message(user_id, text, reply_markup=kb, parse_mode= 'HTML')

@rate_limit(limit=5)
async def start(message: types.Message):
    join(chat_id=message.chat.id)
    q.execute("SELECT block FROM users WHERE user_id=?", (message.chat.id,))
    result = q.fetchone()
    if result[0] == 0:
        if message.chat.id in admin: 
            await send_message(message.from_user.id, 'Добро пожаловать!', kb_menu)
        else:
            text_to_user = open(file_paths['start'], 'r')
            await send_message(message.from_user.id, text_to_user.read(), kb_client)
            requestCountIncrease()
    else:
        await send_message(message.from_user.id, 'Вы были заблокированны',kb_client)

async def admin_main(message: types.Message, state: FSMContext):
	join(chat_id=message.chat.id)
	q.execute("SELECT block FROM users WHERE user_id=?", (message.chat.id,))
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id in admin:
			await send_message(message.from_user.id,'Добро пожаловать в админ-панель',  kb_adm)

async def back_menu(message: types.Message, state: FSMContext):
	await send_message(message.from_user.id,'Добро пожаловать!',  kb_menu)

async def ban_list(message: types.Message, state: FSMContext):
	join(chat_id=message.chat.id)
	q.execute("SELECT block FROM users WHERE user_id=?", (message.chat.id,))
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id in admin:
			q.execute(f"SELECT * FROM users WHERE block == 1")
			result = q.fetchall()
			sl = []
			for index in result:
				i = index[0]
				sl.append(i)

			ids = '\n'.join(map(str, sl))
			await send_message(message.from_user.id,f'ID пользователей находящихся в ЧС:\n{ids}', kb_adm)

async def ban_list_add(message: types.Message, state: FSMContext):
	join(chat_id=message.chat.id)
	q.execute("SELECT block FROM users WHERE user_id=?", (message.chat.id,))
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id in admin:
			await send_message(message.from_user.id,'Введите id пользователя, которого нужно заблокировать.\nДля отмены нажмите кнопку ниже',  kb_back)
			await st.item_ban_list_add.set()

async def ban_list_delete(message: types.Message, state: FSMContext):
	join(chat_id=message.chat.id)
	q.execute("SELECT block FROM users WHERE user_id=?", (message.chat.id,))
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id in admin:
			await send_message(message.from_user.id,'Введите id пользователя, которого нужно разблокировать.\nДля отмены нажмите кнопку ниже',  kb_back)
			await st.item_ban_list_delete.set()

async def mailing_list(message: types.Message, state: FSMContext):
	join(chat_id=message.chat.id)
	q.execute("SELECT block FROM users WHERE user_id=?", (message.chat.id,))
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id in admin:
			await send_message(message.from_user.id,'Введите текст для рассылки.\n\nДля отмены нажмите на кнопку ниже',  kb_back)
			await st.item_mailing_list.set()

@rate_limit(limit=5)
async def get_text(message: types.Message, state: FSMContext):
	join(chat_id=message.chat.id)
	q.execute("SELECT block FROM users WHERE user_id=?", (message.chat.id,))
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id in admin:
			pass
		else:
			await message.answer('Сообщение успешно отправлено')
			logging.info('Сообщение отправлено: ' + message.text)
			requestCountIncrease()
			for admin_id in admin:
				await send_message(admin_id, f"<b>Получен новый вопрос</b>\n<b>От:</b>{md.quote_html(message.from_user.mention)}\n<b>ID:</b> {message.chat.id}\n<b>Сообщение:</b> {md.quote_html(message.text)}", fun(message.chat.id))
	else:
		await send_message(message.from_user.id,'Вы заблокированы в боте. Попробуйте отправить сообщение чуть позже.',kb_client)

@rate_limit(limit=5)
async def get_photo(message: types.Message, state: FSMContext):
	join(chat_id=message.chat.id)
	q.execute("SELECT block FROM users WHERE user_id=?", (message.chat.id,))
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id in admin:
			pass
		else:
			await message.answer('Фотография успешно отправлена')
			logging.info('Фотография успешно отправлена')				
			requestCountIncrease()
			for admin_id in admin:
				await send_message(admin_id, f"<b>Получен новый вопрос</b>\n<b>От:</b>{md.quote_html(message.from_user.mention)}\n<b>ID:</b> {message.chat.id}\n<b>Фото (подпись):</b> {md.quote_html(message.caption)}", fun(message.chat.id))
				await bot.send_photo(admin_id, message.photo[-1].file_id)
	else:
		await send_message(message.from_user.id,'Вы заблокированы в боте. Попробуйте отправить сообщение чуть позже.',kb_client)


async def answer_to_user(call, state: FSMContext):
	if 'ans' in call.data:
		a = call.data.index('-ans')
		ids = call.data[:a]
		await send_message(call.message.chat.id,'Введите ответ:', kb_back)
		await st.item_answer_to_user.set() # администратор отвечает пользователю
		await state.update_data(uid=ids)
	elif 'ignor' in call.data:
		logging.info('Сообщение удалено: ' + call.message.text)			
		await send_message(call.message.chat.id,'Удалено', kb_back)
		await bot.delete_message(call.message.chat.id, call.message.message_id)
		await state.finish()

async def send_to_user(message: types.Message, state: FSMContext):
	if message.text == '⏪ Отмена':
		await send_message(message.from_user.id,'Отмена. Возвращаю назад.', kb_menu)
		await state.finish()
	else:
		logging.info('Ответ от администратора: ' + message.text)		
		await send_message(message.from_user.id,'Сообщение отправлено.', kb_menu)
		data = await state.get_data()
		id = data.get("uid")
		await state.finish()
		await bot.send_message(id, 'Вам поступил ответ от администратора:\n\nТекст: {}'.format(message.text))

async def mailing_user(message: types.Message, state: FSMContext):
	q.execute(f'SELECT user_id FROM users')
	row = q.fetchall()
	connection.commit()
	text = message.text
	if message.text == '⏪ Отмена':
		await send_message(message.from_user.id,'Отмена. Возвращаю назад.', kb_adm)
		await state.finish()
	else:
		info = row
		count = len(info)
		logging.info('Рассылка начата: (count users: ' + str(count) + ' )' + str(text))				
		await send_message(message.from_user.id,'Рассылка начата', kb_adm)
		for i in range(count):
			try:
				await bot.send_message(info[i][0], str(text))
			except:
				pass
		await send_message(message.from_user.id,'Рассылка завершена', kb_adm)
		await state.finish()


async def ban_user(message: types.Message, state: FSMContext):
	if message.text == '⏪ Отмена':
		await send_message(message.from_user.id,'Отмена. Возвращаю назад.', kb_adm)
		await state.finish()
	else:
		if message.text.isdigit():
			q.execute("SELECT block FROM users WHERE user_id=?", (message.text,))
			result = q.fetchall()
			connection.commit()
			if len(result) == 0:
				await send_message(message.from_user.id,'Такой пользователь не найден в базе данных.', kb_adm)
				await state.finish()
			else:
				a = result[0]
				id = a[0]
				if id == 0:
					q.execute("UPDATE users SET block = 1 WHERE user_id=?", (message.text,))	
					connection.commit()
					logging.info('Пользователь успешно заблокирован: ' + message.text)					
					await send_message(message.from_user.id,'Пользователь успешно заблокирован.', kb_adm)
					await state.finish()
					await bot.send_message(message.text, 'Вы были заблокированны администрацией')
				else:
					await send_message(message.from_user.id,'Данный пользователь уже заблокирован', kb_adm)
					await state.finish()
		else:
			await message.answer('Не вводите буквы, нужен ID.\nВведите ID')

async def unban_user(message: types.Message, state: FSMContext):
	if message.text == '⏪ Отмена':
		await send_message(message.from_user.id,'Отмена. Возвращаю назад.', kb_adm)
		await state.finish()
	else:
		if message.text.isdigit():
			q.execute("SELECT block FROM users WHERE user_id=?", (message.text,))
			result = q.fetchall()
			connection.commit()
			if len(result) == 0:
				await send_message(message.from_user.id,'Такой пользователь не найден в базе данных.', kb_adm)
				await state.finish()
			else:
				a = result[0]
				id = a[0]
				if id == 1:
					q.execute("UPDATE users SET block = 0 WHERE user_id=?", (message.text,))	
					connection.commit()
					logging.info('Пользователь успешно разблокирован: ' + message.text)
					await send_message(message.from_user.id,'Пользователь успешно разблокирован.', kb_adm)
					await state.finish()
					await bot.send_message(message.text, 'Вы были разблокированы администрацией.')
				else:
					await send_message(message.from_user.id,'Данный пользователь не заблокирован.', kb_adm)
					await state.finish()
		else:
			await message.answer('Не вводите буквы, нужен ID.\nВведи ID')

@rate_limit(limit=5)
async def client_contact(message : types.Message):
    text = message.text.lower()
    for msg, path in zip(buttons, file_paths):
        if text == msg:
            text_to_user = open(file_paths[path], 'r')
            await send_message(message.from_user.id, text_to_user.read(), kb_client)
            requestCountIncrease()
            break

@rate_limit(limit=5)
async def client_work(message : types.Message):
    text = message.text.lower()
    for msg, path in zip(buttons, file_paths):
        if text == msg:
            text_to_user = open(file_paths[path], 'r')
            await send_message(message.from_user.id, text_to_user.read(), kb_client)
            requestCountIncrease()
            break

def register_handlers_client(dp : Dispatcher):
    dp.middleware.setup(ThrottlingMiddleware())
    dp.register_message_handler(start, commands=['start', 'help'])
    dp.register_message_handler(client_contact, content_types=['text'], text='Контакты')
    dp.register_message_handler(client_work, content_types=['text'], text='Режим работы')
    dp.register_message_handler(admin_main, content_types=['text'], text='Админ-панель')
    dp.register_message_handler(back_menu,content_types=['text'], text='⏪ Назад')
    dp.register_message_handler(ban_list,content_types=['text'], text='✘ Чёрный список')
    dp.register_message_handler(ban_list_add,content_types=['text'], text='✅ Добавить в ЧС')
    dp.register_message_handler(ban_list_delete,content_types=['text'], text='❎ Убрать из ЧС')
    dp.register_message_handler(mailing_list,content_types=['text'], text='💬 Рассылка')    
    dp.register_message_handler(get_text,content_types=['text'])
    dp.register_message_handler(get_photo,content_types=['photo'])
    dp.register_callback_query_handler(answer_to_user,lambda call: True)
    dp.register_message_handler(send_to_user,state=st.item_answer_to_user)
    dp.register_message_handler(mailing_user,state=st.item_mailing_list)
    dp.register_message_handler(ban_user,state=st.item_ban_list_add)
    dp.register_message_handler(unban_user,state=st.item_ban_list_delete)  

def requestCountIncrease():
    global REQUEST_COUNT
    REQUEST_COUNT = REQUEST_COUNT + 1
    os.system('clear')
    print("Телеграм-бот tgk-14_feedback\nКоличество запросов к боту: ", REQUEST_COUNT)