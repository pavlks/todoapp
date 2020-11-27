import requests
import datetime
import logging
import json

from todo_config import PATH, API_TOKEN, PROXY_URL, PROXY_PORT, SECRET, URL, WEBHOOK_HOST
from flask import Flask, Response, request
from database import Mongodb, Todo


# Starting server
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize mongodb
db = Mongodb(PATH)
print(db)

@app.route('/')
def hello_world():
    return "Welcome"



@app.route(f'/{SECRET}', methods=['POST', 'GET'])
def telegram_webhook():
    if request.method == 'POST':
        update = request.get_json()  # types of update: https://core.telegram.org/bots/api#update
        message = update['message']['text']
        chat_id = update['message']['from']['id']
        if re.fullmatch('/\D+'):
        payload = {
            'chat_id': chat_id,
            'text': 'it was a command',
            'parse_mode': 'HTML',
            'reply_markup': {
                'inline_keyboard':[
                    [{
                        'text': 'just testin',
                        'callback_data': 'code123'
                    }]
                ]
            }
        }
        else:
            todo = Todo.process_input(message)
            db.add_record(todo.description, todo.today, todo.date, todo.time)
            payload = {
                'chat_id': chat_id,
                'text': 'regular text',
                'parse_mode': 'HTML',
                'reply_markup': {
                    'inline_keyboard':[
                        [{
                            'text': 'just testin',
                            'callback_data': 'code123'
                        }]
                    ]
                }
            }
        requests.post(URL + '/sendMessage', json=payload)
        return Response('OK', status=200)
    else:
        return Response('OK', status=200)




"""
@dp.message_handler(regexp='today')
async def get_today(message: types.Message):
    await message.delete()
    inline_kb_all = InlineKeyboardMarkup()
    inline_kb_all.row(InlineKeyboardButton(emojize('Убрать задание'), callback_data='courses'))
    inline_kb_all.insert(InlineKeyboardButton(emojize(':point_up: Done'), callback_data='faq'))
    todolist = db.get_today()
    for msg in todolist[:2]:
        await message.answer(emojize(msg), 'html', reply_markup=inline_kb_all)
        await asyncio.sleep(0.5)





@dp.message_handler(regexp='welcome')
async def testing(message: types.Message):
    await message.edit_text
    inline_kb_all = InlineKeyboardMarkup()
    inline_kb_all.row(InlineKeyboardButton(emojize('Убрать задание'), callback_data='courses'))
    inline_kb_all.insert(InlineKeyboardButton(emojize(':point_up: Done'), callback_data='faq'))
    todolist = db.get_today()
    for msg in todolist[:2]:
        await message.answer(emojize(msg), 'html', reply_markup=inline_kb_all)
        await asyncio.sleep(0.5)




@dp.message_handler(regexp='all')
async def get_pending(message: types.Message):
    inline_kb_all = InlineKeyboardMarkup()
    inline_kb_all.row(InlineKeyboardButton(emojize('Добавить на СЕГОДНЯ'), callback_data='courses'))
    # inline_kb_all.row(InlineKeyboardButton(emojize(':point_up: Ответы на часто задаваемые вопросы'), callback_data='faq'))
    todolist = db.get_pending()
    msg = '\n\n'.join(todolist[0:8])
    await message.answer(emojize(msg), 'html')


@dp.message_handler(regexp='clear')
async def clear_today(message: types.Message):
    msg = db.clear_today()
    await message.answer(msg, 'html')


@dp.message_handler(regexp='gg')
async def gg(message: types.Message):
    db.show_today()
    await message.answer('toggle: DONE')


@dp.message_handler()
async def send_welcome(message: types.Message):
    td = Todo.process_input(message.text)
    post_id = db.add_record(td.description, td.today, td.date, td.time)
    await message.answer('hello: ' + td.description)

"""
















if __name__ == "__main__":
    app.run(host='0.0.0.0')
