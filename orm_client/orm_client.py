import records
import structlog
import uuid
from sqlalchemy import create_engine

structlog.configure(
    processors=[  # набор процессоров форматируют наш код в консоли. Процессоры лежат в либе structlog
        structlog.processors.JSONRenderer(indent=4, sort_keys=True, ensure_ascii=False)
    ]  # параметры процессора: indent - отступ в джсоне, ensure_ascii=False - для работы с русской кодировкой
)


class OrmClient:  # обёртка логирующая запросы
    def __init__(self, user, password, host, database, isolation_level='AUTOCOMMIT'):
        connection_string = f'postgresql://{user}:{password}@{host}/{database}'  # для подключения к БД
        print(connection_string)
        self.engine = create_engine(connection_string, isolation_level=isolation_level)
        self.db = self.engine.connect()
        self.log = structlog.get_logger(self.__class__.__name__).bind(service='db')  # создали логгер

    def close_connection(self):
        self.db.close()

    def send_query(self, query):  # метод-обёртка, который будет логировать запрос
        print(query)  # query - строка с sql-запросом
        log = self.log.bind(event_id=str(uuid.uuid4()))  # сделали также как в restclient для хранения event_id
        log.msg(  # формирование логирующего сообщения
            event='request',  # запрос в БД
            query=str(query)  # сюда выводится запрос
        )
        dataset = self.db.execute(statement=query)  # execute для выполнения запроса
        result = [row for row in dataset]
        log.msg(  # логирование полученного датасета
            event='response',
            dataset=[dict(row) for row in result]  # Списковое включение (List comprehension)
        )
        return result

    def send_bulk_query(self, query):  # метод-обёртка, для выполнения запросов delete, update
        print(query)  # query - строка с sql-запросом
        log = self.log.bind(event_id=str(uuid.uuid4()))  # сделали также как в restclient для хранения event_id
        log.msg(  # формирование логирующего сообщения
            event='request',  # запрос в БД
            query=str(query)  # сюда выводится запрос
        )
        self.db.execute(statement=query)  # возвращаемый датасет в виде словаря



# if __name__ == '__main__':
#     db = DbClient(user='postgres', password='admin', host='localhost', database='dm3.5')
#     query = 'select * from "public"."Users"'
#     db.send_query(query)
