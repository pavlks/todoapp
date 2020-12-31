import datetime
import logging

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
            Column('created', types.TIMESTAMP),
            Column('description', types.TEXT),
            Column('notify_date', types.DATE),
            Column('notify_time', types.TIME),
            Column('is_today', types.BOOLEAN),
            Column('category', types.VARCHAR(60)),
            Column('completed', types.TIMESTAMP)
        )
        metadata.create_all(self.engine, checkfirst=True)  # Defaults to True, won’t issue CREATEs for tables already present in the target database. To be aware of this option.:

    def add_record(self, description, created=datetime.datetime.utcnow(), notify_date=None, notify_time=None, is_today=True, category=None, completed=None):
        ins = self.todos.insert().values(
            description=description,
            created=created,
            notify_date=notify_date,
            notify_time=notify_time,
            is_today=is_today,
            category=category,
            completed=completed
        )
        connection = self.engine.connect()
        with connection.begin():
            res = connection.execute(ins)
            id = res.inserted_primary_key
            logging.info("  " + str(datetime.datetime.now()) + "  " + ">" * 20 + "     " + F"TODO CREATED (id: {id}, description: {description})" + "     " + "<" * 20)
        return id

    def get_today(self):
       sel = select([self.todos]).where(self.todos.c.is_today == True)
       connection = self.engine.connect()
       res = connection.execute(sel)
       for row in res:
           print(row)










########################################################
new = SQLdatabase()
new.add_record('hello pipl')
new.get_today()
