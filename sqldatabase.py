import datetime

from sqlalchemy import create_engine, types
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Sequence

class SQLdatabase:
    def __init__(self):
        engine = create_engine('sqlite:///local.db', echo=True, echo_pool='debug')
        metadata = MetaData()
        self.todos = Table(
            'Todos', metadata,
            Column('id', types.INTEGER, Sequence('todo_id_seq'), primary_key=True),
            Column('created', types.TIMESTAMP),
            Column('description', types.TEXT)
        )
        metadata.create_all(engine, checkfirst=True)  # Defaults to True, don’t issue CREATEs for tables already present in the target database. To be aware of this option.:
        self.connection = engine.connect()





new = SQLdatabase()

ins = new.todos.insert().values(created=datetime.datetime.utcnow(), description='we are glad you are here')

res = new.connection.execute(ins)
print(res.inserted_primary_key)

