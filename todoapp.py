# encoding='utf-8'
# encoding=utf-8

import requests
import logging
import json
import re

from todo_config import MONGO_PATH, API_TOKEN, SECRET, URL, WEBHOOK_HOST
from flask import Flask, Response, request
from sqldatabase import SQLdatabase, Todo
from tgupdate import Update


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
        posted = request.get_json()  # types of update: https://core.telegram.org/bots/api#update
        upd = Update(posted)

        # if re.fullmatch('/\w+\s?', message, flags=re.IGNORECASE):  # one-word command is matched (example "/start")
        
        if upd.type == 'message' and re.fullmatch('/start', upd.msg_text, flags=re.IGNORECASE):
            payload = {
                    'chat_id': upd.from_id,
                    'text': "Привет, давай, создавай свой ту-ду лист \nHey, go ahead and start creating your to-do's",
                    'parse_mode': 'HTML',
                    }
            requests.post(URL + '/sendMessage', json=payload)

        elif upd.type == 'message' and re.fullmatch('/someday', upd.msg_text, flags=re.IGNORECASE):
            todos = db.show_today(upd.from_id)
            payload = {
                    'chat_id': upd.from_id,
                    'text': todos,
                    'parse_mode': 'HTML',
                    }
            requests.post(URL + '/sendMessage', json=payload)

        elif upd.type == 'message' and re.fullmatch('/today', upd.msg_text, flags=re.IGNORECASE):
            todos = db.show_today(upd.from_id)
            payload = {
                    'chat_id': upd.from_id,
                    'text': todos,
                    'parse_mode': 'HTML',
                    }
            requests.post(URL + '/sendMessage', json=payload)

        elif upd.type == 'message' and re.fullmatch('/all', upd.msg_text, flags=re.IGNORECASE):
            todos = db.get_pending(upd.from_id)
            for todo in todos:
                
                payload = {
                        'chat_id': upd.from_id,
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
                        'chat_id': upd.from_id,
                        'message_id': message_id,
                        'reply_markup': message_reply_markup,
                        }

                requests.post(URL + '/editMessageReplyMarkup', json=params)

        elif upd.type == 'message' and re.fullmatch('/completed', upd.msg_text, flags=re.IGNORECASE):
            todos = db.show_completed(upd.from_id)
                
            payload = {
                    'chat_id': upd.from_id,
                    'text': todos,
                    'parse_mode': 'HTML',
                    'reply_markup': {'inline_keyboard': [
                        [{'text':'show 10 more', 'callback_data': 'completed 20'}]
                        ]}
                    }
            m = requests.post(URL + '/sendMessage', json=payload)

        elif upd.type == 'message' and re.fullmatch('/clear', upd.msg_text, flags=re.IGNORECASE):
                
            payload = {
                    'chat_id': upd.from_id,
                    'text': "Are you sure you want to clear today's to-do list",
                    'parse_mode': 'HTML',
                    'reply_markup': {'inline_keyboard': [
                        [{'text':'confirm', 'callback_data': 'confirm'}, {'text':'cancel', 'callback_data': 'cancel'}]
                        ]}
                    }
            m = requests.post(URL + '/sendMessage', json=payload)

        elif upd.type == 'callback_query' and re.match('(done|undone)', upd.cbq_data, flags=re.IGNORECASE):
            todo_id, msg_id = [w for w in str(callback_query).split()[1:]]
            msg_id = int(msg_id)
            msg_text = upd.msg_text
            msg_reply_markup = upd.reply_mu

            params1 = {'callback_query_id': upd.cbq_id,}
            requests.post(URL + '/answerCallbackQuery', json=params1)

            db.toggle_completed(todo_id, upd.from_id)

            #\U0001F3AF :dart: today;   \U00002611 :ballot_box_with_check: done;   \U0001F536 :large_orange_diamond: all todos
            if re.match('done', upd.cbq_data, flags=re.IGNORECASE):
                msg_reply_markup['inline_keyboard'][0][-1]['callback_data'] = f'undone {todo_id} {msg_id}'
                msg_reply_markup['inline_keyboard'][0][-1]['text'] = 'mark as pending' 
                params2 = {'chat_id': upd.from_id, 'message_id': msg_id, 'text': f'<s>{msg_text}</s>', 'parse_mode': 'HTML', 'reply_markup': msg_reply_markup}
            else:
                msg_reply_markup['inline_keyboard'][0][-1]['callback_data'] = f'done {todo_id} {msg_id}'
                msg_reply_markup['inline_keyboard'][0][-1]['text'] = 'mark as complete' 
                params2 = {'chat_id': upd.from_id, 'message_id': msg_id, 'text': f'<b>{msg_text}</b>', 'parse_mode': 'HTML', 'reply_markup': msg_reply_markup}
            requests.post(URL + '/editMessageText', json=params2)

        elif upd.type == 'callback_query' and re.match('today', upd.cbq_data, flags=re.IGNORECASE):
            todo_id, msg_id = [w for w in str(callback_query).split()[1:]]
            msg_id = int(msg_id)
            db.toggle_today(todo_id, upd.from_id)
            
            params = {'callback_query_id': upd.cbq_id,}
            requests.post(URL + '/answerCallbackQuery', json=params)

        elif upd.type == 'callback_query' and re.match('completed', upd.cbq_id, flags=re.IGNORECASE):
            quantity = int(str(upd.cbq_data).split()[1])
            msg_id = upd.msg_id
            msg_reply_markup = upd.reply_mu
            
            params1 = {'callback_query_id': upd.cbq_id,}
            requests.post(URL + '/answerCallbackQuery', json=params1)

            todos = db.show_completed(quantity, upd.from_id)

            msg_reply_markup['inline_keyboard'][0][0]['callback_data'] = f'completed {quantity + 10}'
            params2 = {'chat_id': upd.from_id, 'message_id': msg_id, 'text': todos, 'parse_mode': 'HTML', 'reply_markup': msg_reply_markup}
            requests.post(URL + '/editMessageText', json=params2)
            
        elif upd.type == 'callback_query' and re.match('(confirm|cancel)', upd.cbq_data, flags=re.IGNORECASE):
            if upd.cbq_data == 'confirm':
                db.clear_today(upd.from_id)
                params = {'callback_query_id': upd.cbq_id, 'text': f"items were cleared from today's to-do list", 'show_alert': True}
            else:
                params = {'callback_query_id': upd.cbq_id, 'text': 'operation was cancelled', 'show_alert': True}
            requests.post(URL + '/answerCallbackQuery', json=params)

        else:
            todo = Todo.process_input(upd.msg_text)
            db.add_record(todo.description, todo.notify_date, todo.notify_time, todo.is_today, todo.category, upd.from_id)
            payload = {
                    'chat_id': upd.from_id,
                    'text': '<b>new to-do was added</b>',
                    'parse_mode': 'HTML',
                    }
            requests.post(URL + '/sendMessage', json=payload)

    return Response('OK', status=200)






if __name__ == "__main__":
    app.run(host='0.0.0.0')
