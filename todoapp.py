# encoding='utf-8'
# encoding=utf-8

import requests
import logging
import json
import re

from todo_config import MONGO_PATH, API_TOKEN, SECRET, URL, WEBHOOK_HOST
from flask import Flask, Response, request
from sqldatabase import SQLdatabase, Todo


# Starting server
app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='logtodo.log', encoding='utf-8', level=logging.DEBUG)

# Initialize sqlite database
db = SQLdatabase()


@app.route('/')
def hello_world():
    return "Welcome"


@app.route(f'/{SECRET}', methods=['POST', 'GET'])
def telegram_webhook():
    if request.method == 'POST':
        update = request.get_json()  # types of update: https://core.telegram.org/bots/api#update
        message = update['message']['text'] if 'message' in update else None
        chat_id = 789561316  # update['message']['from']['id'] if 'message' in update else None
        callback_query = update['callback_query']['data'] if 'callback_query' in update else None
        callback_query_id = update['callback_query']['id'] if 'callback_query' in update else None
        
        # if re.fullmatch('/\w+\s?', message, flags=re.IGNORECASE):  # one-word command is matched (example "/start")
        
        if message and re.fullmatch('/today', message, flags=re.IGNORECASE):
            todos = db.show_today()
            payload = {
                    'chat_id': chat_id,
                    'text': todos,
                    'parse_mode': 'HTML',
                    }
            requests.post(URL + '/sendMessage', json=payload)
            #  todos = db.show_today()
            #  for todo in todos:
            
                #  payload = {
                        #  'chat_id': chat_id,
                        #  'text': todo[0],
                        #  'parse_mode': 'HTML',
                        #  'reply_markup': {'inline_keyboard': [[{'text':'mark as', 'callback_data': f'done {todo[1]}'}]]}
                        #  }
                #  m = requests.post(URL + '/sendMessage', json=payload)

                #  mj = m.json()
                #  message_text = mj['result']['text']
                #  message_id = mj['result']['message_id']
                #  message_reply_markup = mj['result']['reply_markup']
                #  message_reply_markup['inline_keyboard'][0][0]['callback_data'] += f' {message_id}'
                #  message_reply_markup['inline_keyboard'][0][0]['text'] += f' complete'
                
                #  params = {
                        #  'chat_id': chat_id,
                        #  'message_id': message_id,
                        #  'reply_markup': message_reply_markup,
                        #  }

                #  requests.post(URL + '/editMessageReplyMarkup', json=params)

        elif message and re.fullmatch('/all', message, flags=re.IGNORECASE):
            todos = db.get_pending()
            for todo in todos:
                
                payload = {
                        'chat_id': chat_id,
                        'text': todo[0],
                        'parse_mode': 'HTML',
                        'reply_markup': {'inline_keyboard': [
                            [{'text':'mark for today', 'callback_data': f'today {todo[1]}'}, {'text':'mark as', 'callback_data': f'done {todo[1]}'}]
                            ]}
                        }
                m = requests.post(URL + '/sendMessage', json=payload)

                mj = m.json()
                message_text = mj['result']['text']
                message_id = mj['result']['message_id']
                message_reply_markup = mj['result']['reply_markup']
                message_reply_markup['inline_keyboard'][0][0]['callback_data'] += f' {message_id}'
                message_reply_markup['inline_keyboard'][0][-1]['callback_data'] += f' {message_id}'
                message_reply_markup['inline_keyboard'][0][-1]['text'] += f' complete'
                
                params = {
                        'chat_id': chat_id,
                        'message_id': message_id,
                        'reply_markup': message_reply_markup,
                        }

                requests.post(URL + '/editMessageReplyMarkup', json=params)

        elif message and re.fullmatch('/completed', message, flags=re.IGNORECASE):
            todos = db.show_completed()
                
            payload = {
                    'chat_id': chat_id,
                    'text': todos,
                    'parse_mode': 'HTML',
                    'reply_markup': {'inline_keyboard': [
                        [{'text':'show 10 more', 'callback_data': 'completed 20'}]
                        ]}
                    }
            m = requests.post(URL + '/sendMessage', json=payload)

        elif message and re.fullmatch('/clear', message, flags=re.IGNORECASE):
                
            payload = {
                    'chat_id': chat_id,
                    'text': "Are you sure you want to clear today's to-do list",
                    'parse_mode': 'HTML',
                    'reply_markup': {'inline_keyboard': [
                        [{'text':'confirm', 'callback_data': 'confirm'}, {'text':'cancel', 'callback_data': 'cancel'}]
                        ]}
                    }
            m = requests.post(URL + '/sendMessage', json=payload)

        elif callback_query and re.match('(done|undone)', callback_query, flags=re.IGNORECASE):
            todo_id, msg_id = [w for w in str(callback_query).split()[1:]]
            msg_id = int(msg_id)
            msg_text = update['callback_query']['message']['text']
            msg_reply_markup = update['callback_query']['message']['reply_markup']

            params1 = {'callback_query_id': callback_query_id,}
            requests.post(URL + '/answerCallbackQuery', json=params1)

            db.toggle_completed(todo_id)

            #\U0001F3AF :dart: today;   \U00002611 :ballot_box_with_check: done;   \U0001F536 :large_orange_diamond: all todos
            if re.match('done', callback_query, flags=re.IGNORECASE):
                msg_reply_markup['inline_keyboard'][0][-1]['callback_data'] = f'undone {todo_id} {msg_id}'
                msg_reply_markup['inline_keyboard'][0][-1]['text'] = 'mark as pending' 
                params2 = {'chat_id': chat_id, 'message_id': msg_id, 'text': f'<s>{msg_text}</s>', 'parse_mode': 'HTML', 'reply_markup': msg_reply_markup}
            else:
                msg_reply_markup['inline_keyboard'][0][-1]['callback_data'] = f'done {todo_id} {msg_id}'
                msg_reply_markup['inline_keyboard'][0][-1]['text'] = 'mark as complete' 
                params2 = {'chat_id': chat_id, 'message_id': msg_id, 'text': f'<b>{msg_text}</b>', 'parse_mode': 'HTML', 'reply_markup': msg_reply_markup}
            requests.post(URL + '/editMessageText', json=params2)

        elif callback_query and re.match('today', callback_query, flags=re.IGNORECASE):
            todo_id, msg_id = [w for w in str(callback_query).split()[1:]]
            msg_id = int(msg_id)
            db.toggle_today(todo_id)
            
            params = {'callback_query_id': callback_query_id,}
            requests.post(URL + '/answerCallbackQuery', json=params)

        elif callback_query and re.match('completed', callback_query, flags=re.IGNORECASE):
            quantity = int(str(callback_query).split()[1])
            msg_id = update['callback_query']['message']['message_id']
            msg_reply_markup = update['callback_query']['message']['reply_markup']
            
            params1 = {'callback_query_id': callback_query_id,}
            requests.post(URL + '/answerCallbackQuery', json=params1)

            todos = db.show_completed(quantity)

            msg_reply_markup['inline_keyboard'][0][0]['callback_data'] = f'completed {quantity + 10}'
            params2 = {'chat_id': chat_id, 'message_id': msg_id, 'text': todos, 'parse_mode': 'HTML', 'reply_markup': msg_reply_markup}
            requests.post(URL + '/editMessageText', json=params2)
            
        elif callback_query and re.match('(confirm|cancel)', callback_query, flags=re.IGNORECASE):
            if callback_query == 'confirm':
                db.clear_today()
                params = {'callback_query_id': callback_query_id, 'text': f"items were cleared from today's to-do list", 'show_alert': True}
            else:
                params = {'callback_query_id': callback_query_id, 'text': 'operation was cancelled', 'show_alert': True}
            requests.post(URL + '/answerCallbackQuery', json=params)

        else:
            todo = Todo.process_input(message)
            db.add_record(todo.description, todo.notify_date, todo.notify_time, todo.is_today, todo.category)
            payload = {
                    'chat_id': chat_id,
                    'text': '<b>new to-do was added</b>',
                    'parse_mode': 'HTML',
                    }
            requests.post(URL + '/sendMessage', json=payload)

    return Response('OK', status=200)






if __name__ == "__main__":
    app.run(host='0.0.0.0')
