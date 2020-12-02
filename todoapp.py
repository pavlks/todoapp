# encoding='utf-8'
# encoding=utf-8

import requests
import datetime
import logging
import json
import re

from todo_config import MONGO_PATH, API_TOKEN, SECRET, URL, WEBHOOK_HOST
from flask import Flask, Response, request
from database import Mongodb, Todo


# Starting server
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize mongodb
db = Mongodb(MONGO_PATH)


@app.route('/')
def hello_world():
    return "Welcome"


@app.route(f'/{SECRET}', methods=['POST', 'GET'])
def telegram_webhook():
    if request.method == 'POST':
        update = request.get_json()  # types of update: https://core.telegram.org/bots/api#update
        message = update['message']['text']
        callback_query = update['callback_query']['data']
        callback_query_id = update['callback_query']['id']
        chat_id = update['message']['from']['id']
        
        # if re.fullmatch('/\w+\s?', message, flags=re.IGNORECASE):  # one-word command is matched (example "/start")
        if update['message'] and re.fullmatch('/today', message, flags=re.IGNORECASE):
            todos = db.get_today()
            for todo in todos[:1]:
            
                payload = {
                        'chat_id': chat_id,
                        'text': str(todo[0]),
                        'parse_mode': 'HTML',
                        'reply_markup': {'inline_keyboard': [[{'text':'mark as', 'callback_data': f'done {todo[1]}'}]]}
                        }
                m = requests.post(URL + '/sendMessage', json=payload)

                mj = m.json()
                message_text = mj['result']['text']
                message_id = mj['result']['message_id']
                message_reply_markup = mj['result']['reply_markup']
                message_reply_markup['inline_keyboard'][0][0]['callback_data'] += f' {message_id}'
                message_reply_markup['inline_keyboard'][0][0]['text'] += f' complete'
                
                params = {
                        'chat_id': chat_id,
                        'message_id': message_id,
                        'reply_markup': message_reply_markup,
                        }

                requests.post(URL + '/editMessageReplyMarkup', json=params)

        elif update['message'] and re.fullmatch('/all', message, flags=re.IGNORECASE):  # when 1 word command is matched (example "/start")
            todos = db.get_pending()
            for todo in todos[:2]:
                
                payload = {
                        'chat_id': chat_id,
                        'text': todo,
                        'parse_mode': 'HTML',
                        'reply_markup': {'inline_keyboard': [[{'text':'add to today', 'callback_data': 'temp123'}]]}
                        }
                requests.post(URL + '/sendMessage', json=payload)

        elif update['callback_query'] and re.match('done', callback_query):
            todo_id, msg_id = [x for x in str(callback_query).split()[1:]]
            msg_id = int(msg_id)
            db.set_done(todo_id)

            payload = {
                    'callback_query_id': callback_query_id,
            }
            
            requests.post(URL + '/answerCallbackQuery', json=payload)




        else:
            payload = {
                'chat_id': chat_id,
                'text': 'regular text',
                }
        requests.post(URL + '/sendMessage', data={'chat_id': chat_id, 'text': '\U00002611'})
    return Response('OK', status=200)






if __name__ == "__main__":
    app.run(host='0.0.0.0')
