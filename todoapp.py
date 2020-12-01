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
        chat_id = update['message']['from']['id']
        
        # if re.fullmatch('/\w+\s?', message, flags=re.IGNORECASE):  # when 1 word command is matched (example "/start")
        if re.fullmatch('/today', message, flags=re.IGNORECASE):  # when 1 word command is matched (example "/start")
            todos = db.get_today()
            for todo in todos[:3]:
                
                payload = {
                        'chat_id': chat_id,
                        'text': todo,
                        'parse_mode': 'HTML',
                        'reply_markup': {'inline_keyboard': [[{'text':'add to today', 'callback_data': 'temp123'}]]}
                        }
                requests.post(URL + '/sendMessage', json=payload)

        elif re.fullmatch('/all', message, flags=re.IGNORECASE):  # when 1 word command is matched (example "/start")
            todos = db.get_pending()
            for todo in todos[:3]:
                
                payload = {
                        'chat_id': chat_id,
                        'text': todo,
                        'parse_mode': 'HTML',
                        'reply_markup': {'inline_keyboard': [[{'text':'add to today', 'callback_data': 'temp123'}]]}
                        }
                requests.post(URL + '/sendMessage', json=payload)

        else:
            payload = {
                'chat_id': chat_id,
                'text': 'regular text',
                }
        requests.post(URL + '/sendMessage', data={'chat_id': chat_id, 'text': '\U00002611'})
    return Response('OK', status=200)






if __name__ == "__main__":
    app.run(host='0.0.0.0')
