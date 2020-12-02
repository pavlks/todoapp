# encoding='utf-8'
# encoding=utf-8
import requests
import datetime
import logging
import json
import time
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
        chat_id = update['message']['from']['id']
        
        # if re.fullmatch('/\w+\s?', message, flags=re.IGNORECASE):  # when 1 word command is matched (example "/start")
        if re.fullmatch('/today', message, flags=re.IGNORECASE):
            todos = db.get_today()
<<<<<<< HEAD
            for todo in todos:
                
                payload = {
                        'chat_id': chat_id,
                        'text': todo[0],
                        'parse_mode': 'HTML',
                        'reply_markup': {'inline_keyboard': [[{'text':'mark as ', 'callback_data': {'_id': todo[1]}}]]}
                        }
                m = requests.post(URL + '/sendMessage', data=payload)
=======
            for todo in todos[:1]:
            
                payload = {
                        'chat_id': chat_id,
                        'text': str(todo[0]),
                        'parse_mode': 'HTML',
                        'reply_markup': {'inline_keyboard': [[{'text':'mark as', 'callback_data': todo[1]}]]}
                        }
                m = requests.post(URL + '/sendMessage', json=payload)

>>>>>>> conf
                mj = m.json()
                message_text = mj['result']['text']
                message_id = mj['result']['message_id']
                message_chat_id = mj['result']['chat']['id']
                message_reply_markup = mj['result']['reply_markup']
                message_reply_markup['inline_keyboard'][0][0]['callback_data'] += f' {message_id}'
                message_reply_markup['inline_keyboard'][0][0]['text'] += f' complete'
<<<<<<< HEAD
                # t = request.post(URL + '/editMessageText')
=======
                
>>>>>>> conf
                params = {
                        'chat_id': message_chat_id,
                        'message_id': message_id,
                        'reply_markup': message_reply_markup,
<<<<<<< HEAD
                }
                time.sleep(3)
                r = request.post(URL + '/editMessageReplyMarkup', data=params)

        elif re.fullmatch('/all', message, flags=re.IGNORECASE):  # when 1 word command is matched (example "/start")
            todos = db.get_pending()
            for todo in todos:
=======
                        }

                requests.post(URL + '/editMessageReplyMarkup', json=params)








        elif re.fullmatch('/all', message, flags=re.IGNORECASE):  # when 1 word command is matched (example "/start")
            todos = db.get_pending()
            for todo in todos[:2]:
>>>>>>> conf
                
                payload = {
                        'chat_id': chat_id,
                        'text': todo,
                        'parse_mode': 'HTML',
                        'reply_markup': {'inline_keyboard': [[{'text':'schedule for today', 'callback_data': {'_id':todo}}]]}
                        }
                m = requests.post(URL + '/sendMessage', json=payload)

        else:
            payload = {
                    'chat_id': chat_id,
                    'text': 'SOME text to strikethrough',
                    'parse_mode': 'HTML',
                    'reply_markup': {'inline_keyboard': [[{'text':'mark as processed', 'callback_data': {'record _id':'12345678'}}]]}
                    }
            requests.post(URL + '/sendMessage', json=payload)

        requests.post(URL + '/sendMessage', data={'chat_id': chat_id, 'text': '\U00002611'})
    return Response('OK', status=200)






if __name__ == "__main__":
    app.run(host='0.0.0.0')
