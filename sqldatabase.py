import datetime
import logging
import re

from sqlalchemy import create_engine, types
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Sequence
from sqlalchemy.sql import select


class SQLdatabase:
    def __init__(self):
        self.engine = create_engine('sqlite:///local.db', echo=True, echo_pool='debug')
        metadata = MetaData()
        self.todos = Table(
            'todos', metadata,
            Column('id', types.INTEGER, Sequence('todo_id_seq'), primary_key=True),
            # Compatibility with sqlite3 “native” date and datetime types (https://docs.sqlalchemy.org/en/13/dialects/sqlite.html?highlight=parse_decltypes#compatibility-with-sqlite3-native-date-and-datetime-types)
            Column('created', types.DATETIME),  
            Column('chat_id', types.INTEGER, nullable=False),  
            Column('description', types.TEXT),
            Column('notify_date', types.DATE),
            Column('notify_time', types.TIME),
            Column('is_today', types.BOOLEAN),
            Column('category', types.TEXT(60)),
            Column('completed', types.DATETIME)
        )
        metadata.create_all(self.engine, checkfirst=True)  # Defaults to True, won’t issue CREATEs for tables already present in the target database. To be aware of this option.:

    def add_record(self, description, notify_date, notify_time, is_today, category, chat_id):
        ins = self.todos.insert().values(
            description=description,
            created=datetime.datetime.utcnow(),
            notify_date=notify_date,
            notify_time=notify_time,
            is_today=is_today,
            category=category,
            chat_id=chat_id,
            completed=None
        )
        connection = self.engine.connect()
        with connection.begin():
            res = connection.execute(ins)
            id = res.inserted_primary_key
            logging.info("  " + str(datetime.datetime.now()) + "  " + ">" * 20 + "     " + F"TODO CREATED id: {id}, description: [{description}]" + "     " + "<" * 20)
        return id

    def show_today(self, chat_id):
        logging.info("  " + str(datetime.datetime.now()) + "  " + ">" * 20 + "     " + "GETTING TODAY TODOS" + "     " + "<" * 20)
        sel = select([self.todos]).where(self.todos.c.is_today == True).where(self.todos.c.completed == None).where(self.todos.c.chat_id == chat_id)
        connection = self.engine.connect()
        res = connection.execute(sel)
        ts = str()
        nl = "\n"
        for row in res:  #\U0001F3AF :dart: today;   \U00002611 :ballot_box_with_check: done;   \U0001F536 :large_orange_diamond: all todos
            ts += f"\U0001F3AF <b>{str(row['description']).upper()}</b>{nl}{nl}"
        return ts

    def get_pending(self, chat_id):
        logging.info("  " + str(datetime.datetime.now()) + "  " + ">" * 20 + "     " + "GETTING PENDING TODOS" + "     " + "<" * 20)
        sel = select([self.todos]).where(self.todos.c.completed == None).where(self.todos.c.chat_id == chat_id)
        connection = self.engine.connect()
        res = connection.execute(sel)
        tl = list()
        for row in res:
            rec = tuple((f"\U0001F536 <b>{str(row['description']).upper()}</b>", str(row['id'])))
            tl.append(rec)
        return tl

    def clear_today(self, chat_id):
        logging.info("  " + str(datetime.datetime.now()) + "  " + ">" * 20 + "     " + "CLEARING TODAY TODOS" + "     " + "<" * 20)
        stmt = self.todos.update().\
                    where(self.todos.c.is_today == True).where(self.todos.c.completed == None).where(self.todos.c.chat_id == chat_id).\
                    values(is_today=False)
        connection = self.engine.connect()
        res = connection.execute(stmt)
        return True

    def toggle_today(self, id, chat_id):
        sel = select([self.todos]).where(self.todos.c.id == id).where(self.todos.c.chat_id == chat_id)
        connection = self.engine.connect()
        res = connection.execute(sel)
        row = res.fetchone()
        status = row['is_today']
        if status is True:
            logging.info("  " + str(datetime.datetime.now()) + "  " + ">" * 20 + "     " + F"TODO MOVED TO PENDING (id: {id}, description: {row['description']})" + "     " + "<" * 20)
            stmt = self.todos.update().\
                        where(self.todos.c.id == id).where(self.todos.c.chat_id == chat_id).\
                        values(is_today=False)
        else:
            logging.info("  " + str(datetime.datetime.now()) + "  " + ">" * 20 + "     " + F"TODO MOVED TO TODAY (id: {id}, description: {row['description']})" + "     " + "<" * 20)
            stmt = self.todos.update().\
                        where(self.todos.c.id == id).where(self.todos.c.chat_id == chat_id).\
                        values(is_today=True)
        connection = self.engine.connect()
        res = connection.execute(stmt)
        return not status

    def toggle_completed(self, id, chat_id):
        sel = select([self.todos]).where(self.todos.c.id == id).where(self.todos.c.chat_id == chat_id)
        connection = self.engine.connect()
        res = connection.execute(sel)
        row = res.fetchone()
        status = row['completed']
        if status is True:
            logging.info("  " + str(datetime.datetime.now()) + "  " + ">" * 20 + "     " + F"TODO SET AS PENDING (id: {id}, description: {row['description']})" + "     " + "<" * 20)
            stmt = self.todos.update().\
                        where(self.todos.c.id == id).where(self.todos.c.chat_id == chat_id).\
                        values(completed=None)
        else:
            logging.info("  " + str(datetime.datetime.now()) + "  " + ">" * 20 + "     " + F"TODO SET AS COMPLETED (id: {id}, description: {row['description']})" + "     " + "<" * 20)
            stmt = self.todos.update().\
                        where(self.todos.c.id == id).where(self.todos.c.chat_id == chat_id).\
                        values(completed=datetime.datetime.utcnow())
        res = connection.execute(stmt)
        return not status

    def show_completed(self, chat_id, quantity=10):
        logging.info("  " + str(datetime.datetime.utcnow()) + "  " + ">" * 20 + "     " + "GETTING COMPLETED TODOS" + "     " + "<" * 20)
        sel = select([self.todos]).where(self.todos.c.completed != None).where(self.todos.c.chat_id == chat_id)
        connection = self.engine.connect()
        res = connection.execute(sel)
        ts = str()
        nl = "\n"
        for row in res.fetchmany(size=quantity):
            ts += f"\U00002611 <b>{str(row['description']).upper()}</b>{nl}{nl}"
        return ts



class Todo:
    def __init__(self, description, notify_date, notify_time, is_today, category):
        self.created = datetime.datetime.utcnow()
        self.description = description
        self.notify_date = notify_date
        self.notify_time = notify_time
        self.is_today = is_today
        self.category = category
        self.completed = False

    def __str__(self):
        return self.description
        
    @classmethod
    def process_input(cls, user_input):
        notify_date = None
        notify_time = None
        is_today = True
        category = None
        if re.search('(today|hoy|сегодня)', user_input, flags=re.IGNORECASE):
            is_today = True
            notify_date = datetime.date.today()
        elif re.search('(tomorrow|manana|manaña|завтра)', user_input, flags=re.IGNORECASE):
            is_today = False
            notify_date = datetime.date.today() + datetime.timedelta(days=1)
        elif re.search('(day after tomorrow|pasado manana|pasado manaña|послезавтра)', user_input, flags=re.IGNORECASE):
            is_today = False
            notify_date = datetime.date.today() + datetime.timedelta(days=2)
        elif re.search(r'(in \d+ days?|en \d+ d[ií]as?|через \d+ де?н(я|ей|ь))', user_input, flags=re.IGNORECASE):
            is_today = False
            td = re.search(r'(in \d+ days?|en \d+ d[ií]as?|через \d+ де?н(я|ей|ь))', user_input, flags=re.IGNORECASE).group(0)
            notify_date = datetime.date.today() + datetime.timedelta(days=int(td))

        # добавить обработку прибавления даты на 1 и более месяцев, если есть упоминание в сообщении 'через месяц' или 'через 3 месяца'

        if re.search(r'(?<=at\s)\d{1,2}([:.,-;\/]\d{0,2})?([ap]m)?', user_input, flags=re.IGNORECASE):  # finds 'at 14 pm' or 'at 6:45'
            string = re.search(r'(?<=at\s)\d{1,2}([:.,-;\/]\d{0,2})?([ap]m)?', user_input, flags=re.IGNORECASE).group(0)
            hh = string[:2]
            time = string[2:]

        #  return cls(user_input)
        return cls(user_input, notify_date, notify_time, is_today, category)

