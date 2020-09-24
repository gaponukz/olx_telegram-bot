from aiogram import (
    Bot, Dispatcher, executor, types
)
import asyncio, os

from db import Database
from utils import parse_urls, parse, get_heading

bot = Bot(token = '1011547803:AAGVi0ilCkXixUF5--uArNYa5oy0oW3p5_k')
bot_name = 'OlxUpdateCheckBot'
dp = Dispatcher(bot)
db = Database.connect('db.db')
DIR = 'C:\\Users\\admin\\Desktop\\py\\olx_checker\\urls'

@dp.message_handler(commands = ['start'])
async def start_bot(message: types.Message):
    if not await db.user_exists(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.username)
    
    await bot.send_message(message.from_user.id, 
        f'Вас приветствует {bot_name}!' \
        + 'Чтобы увидеть все команды введите /help')

@dp.message_handler(commands = ['help'])
async def help_list(message: types.Message):
    await bot.send_message(message.from_user.id, \
        '/subscribe - подписаться на рассылку\n'
        + '/unsubscribe - отписаться от рассылки\n'
        + '/set [url] - ввести ссылку, из которой будут приходит уведомления.')

@dp.message_handler(commands = ['set', 'set_url'])
async def set_url(message: types.Message) -> None:
    commands = message.get_args().split()
    await db.update_url(message.from_user.id, commands[0])

    if (heading := await get_heading(commands[0])):
        await bot.send_message(message.from_user.id, \
            f'Рубрика уведомлений - {heading}.')

@dp.message_handler(commands = ['subscribe'])
async def subscribe(message: types.Message):
	if not await db.user_exists(message.from_user.id):
		await db.add_user(message.from_user.id, message.from_user.username)
	else:
		await db.update_user(message.from_user.id, True)

	await message.answer("Вы успешно подписались на рассылку!")

@dp.message_handler(commands = ['unsubscribe'])
async def unsubscribe(message: types.Message):
	if not await db.user_exists(message.from_user.id):
		await db.add_user(message.from_user.id, message.from_user.username)
	else:
		await db.update_user(message.from_user.id, False)
		await message.answer("Вы успешно отписаны от рассылки!")

async def sheduler(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        users = await db.get_users()

        for user in users:
            if not os.path.exists(f'{DIR}\\{user[1]}.csv'):
                open(f'{DIR}\\{user[1]}.csv', 'x').close()
            
            with open(f'{DIR}\\{user[1]}.csv', 'r', encoding = 'utf-8') as data_file:
                data = data_file.read().split('\n')

            urls = await parse_urls(user[4])

            difference = [item for item in urls if item not in data]

            if difference:
                with open(f'{DIR}\\{user[1]}.csv', 'w', encoding = 'utf-8') as data_file:
                    for url in urls:
                        data_file.write(f'{url}\n')

                post = await parse(difference[0])
                media = types.InputMediaPhoto(post['img'], caption = (
                    post['title'] + '\n' + post['description'][:300] + '...' + '\n' + post['price']
                ))

                inline = types.InlineKeyboardMarkup(row_width = 2)

                await bot.send_media_group(user[1], [media])
                await bot.send_message(user[1], 'Полностью можно посмотреть по ссылке', reply_markup = inline.add(
                    types.InlineKeyboardButton('Перейти к объявлению', url = post['url'])
                ))

if __name__ == '__main__':
	dp.loop.create_task(sheduler(60))
	executor.start_polling(dp, skip_updates = True)