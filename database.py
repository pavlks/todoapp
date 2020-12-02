# encoding='utf-8'
# encoding=utf-8
import pymongo
import logging
import re
import datetime

from pymongo import MongoClient
from bson.objectid import ObjectId


class Mongodb:
    def __init__(self, path):
        # connect to database
        self.client = MongoClient(path)
        # choose database
        self.db = self.client.todoapp
        # choose collection
        self.collection = self.db.todos
        # create index if none
        print(list(self.collection.index_information()))
        if not len(list(self.collection.index_information())) > 1:
            self.collection.create_index([('timestamp', pymongo.DESCENDING), ('description', pymongo.ASCENDING)], name='todo_id')
        logging.info("  " + str(datetime.datetime.now()) + "  " + ">" * 20 + "     " + "DATABASE INITIATED" + "     " + "<" * 20)

    def __str__(self):
        return 'Total number of records: ' + str(self.collection.count_documents({}))  # Maybe in some future will use database info printing
    
    def add_record(self, description, today, date, time):
        todo = {
        "description": description,
        "today": today,
        "date": datetime.datetime.today(),  # It'd be great to implement reminder in future
        "time": time,  # It'd be great to implement reminder in future
        "date-created": datetime.datetime.now(),
        "done": False,
        "date-done": None
        }
        _id = self.collection.insert_one(todo).inserted_id
        logging.info("  " + str(datetime.datetime.now()) + "  " + ">" * 20 + "     " + F"TODO CREATED (_id: {_id}, description: {description})" + "     " + "<" * 20)
        return _id

    def get_today(self):
        todos = self.collection.find({'today': True, 'done': False})
        todolist = list()
        for todo in todos:  #:dart: today;   :ballot_box_with_check: done;   :large_orange_diamond: all todos
            # todolist.append(f":dart: <b>{str(todo['description']).upper()}</b>")
            line = tuple((f"\U0001F3AF <b>{str(todo['description']).upper()}</b>", str(todo['_id'])))
            todolist.append(line)
        logging.info("  " + str(datetime.datetime.now()) + "  " + ">" * 20 + "     " + "GETTING TODAY TODOS" + "     " + "<" * 20)
        return todolist

    def get_pending(self):
        todos = self.collection.find({'done': False})
        todolist = list()
        for todo in todos:  #:dart: today;   :ballot_box_with_check: done;   :large_orange_diamond: all todos
            # todolist.append(f":large_orange_diamond: <b>{str(todo['description']).upper()}</b>")
            todolist.append(f"\U0001F536 <b>{str(todo['description']).upper()}</b>")
        todos_as_text = "\n\n".join(todolist)
        logging.info("  " + str(datetime.datetime.now()) + "  " + ">" * 20 + "     " + "GETTING PENDING TODOS" + "     " + "<" * 20)
        return todolist

    def clear_today(self):
        result = self.collection.update_many({'today': True, 'done': False}, {'$set': {'today': False}})
        matched = result.matched_count
        modified = result.modified_count
        logging.info("  " + str(datetime.datetime.now()) + "  " + ">" * 20 + "     " + F"CLEARING TODAY TODOS (MATCHED: {matched}, CHANGED: {modified})" + "     " + "<" * 20)
        return matched, modified

    def toggle_today(self, _id):
        record = self.collection.find_one({'_id': ObjectId(_id)})
        status = record['today']
        if status is True:
            self.collection.update_one({'_id': ObjectId(_id)}, {'$set': {'today': False}})
            logging.info("  " + str(datetime.datetime.now()) + "  " + ">" * 20 + "     " + F"TODO MOVED TO UPCOMMING (_id: {_id}, description: {description})" + "     " + "<" * 20)
            return False
        else:
            self.collection.update_one({'_id': ObjectId(_id)}, {'$set': {'today': True}})
            logging.info("  " + str(datetime.datetime.now()) + "  " + ">" * 20 + "     " + F"TODO MOVED TO TODAY (_id: {_id}, description: {description})" + "     " + "<" * 20)
            return True

    def set_done(self, _id):
        record = self.collection.find_one({'_id': ObjectId(_id)})
        self.collection.update_one({'_id': ObjectId(_id)}, {'$set': {'done': True}})
        logging.info("  " + str(datetime.datetime.now()) + "  " + ">" * 20 + "     " + F"TODO SET AS COMPLETED (_id: {_id}, description: {description})" + "     " + "<" * 20)
        return True

    def get_completed(self, quantity=10):
        todos = self.collection.find({'done': True})
        quantity = min(quantity, len(todos))
        todolist = list()
        for todo in todos[-quantity:]:  #:dart: today;   :ballot_box_with_check: done;   :large_orange_diamond: all todos
            todolist.append(f"\U00002611 <b>{str(todo['description']).upper()}</b>")
        todos_as_text = "\n\n".join(todolist)
        logging.info("  " + str(datetime.datetime.now()) + "  " + ">" * 20 + "     " + "GETTING COMPLETED TODOS" + "     " + "<" * 20)
        return todos_as_text


class Todo:
    def __init__(self, description, today=True, date=None, time=None):
        self.today = today
        self.done = False
        self.date_done = None
        self.date_created = datetime.datetime.now()
        self.date = date
        self.time = time
        self.description = description

    def __str__(self):
        return self.description
        
    @classmethod
    def process_input(cls, user_input):
        today = True
        date = None
        time = None
        if re.search('(today|hoy|сегодня)', user_input, flags=re.IGNORECASE):
            print('HERE: today')
            today = True
            date = datetime.date.today()
        elif re.search('(tomorrow|manana|manaña|завтра)', user_input, flags=re.IGNORECASE):
            print('HERE: tomorrow')
            today = False
            date = datetime.date.today() + datetime.timedelta(days=1)
        elif re.search('(day after tomorrow|pasado manana|pasado manaña|послезавтра)', user_input, flags=re.IGNORECASE):
            today = False
            date = datetime.date.today() + datetime.timedelta(days=2)
        elif re.search(r'(in \d+ days?|en \d+ d[ií]as?|через \d+ де?н(я|ей|ь))', user_input, flags=re.IGNORECASE):
            today = False
            td = re.search(r'(in \d+ days?|en \d+ d[ií]as?|через \d+ де?н(я|ей|ь))', user_input, flags=re.IGNORECASE).group(0)
            date = datetime.date.today() + datetime.timedelta(days=int(td))

        # добавить обработку прибавления даты на 1 и более месяцев, если есть упоминание в сообщении 'через месяц' или 'через 3 месяца'

        if re.search(r'(?<=at\s)\d{1,2}([:.,-;\/]\d{0,2})?([ap]m)?', user_input, flags=re.IGNORECASE):  # finds 'at 14 pm' or 'at 6:45'
            string = re.search(r'(?<=at\s)\d{1,2}([:.,-;\/]\d{0,2})?([ap]m)?', user_input, flags=re.IGNORECASE).group(0)
            hh = string[:2]
            time = string[2:]

        print('todo info: ', user_input, 'today: ', today, 'date: ', date, 'time: ', time)
        return cls(description=user_input, today=today, date=date, time=time)
    
