import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.extras import DictCursor
from contextlib import closing

from prettytable import PrettyTable


class User:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


class Database:
    def __init__(self, user: User, db_name):
        self.db_name = db_name
        self.user = user
        self.connection = self.connect()
        self.tables = self._get_tables() if self.connection else []
        print(self.tables)

    def connect(self):
        connection = None
        try:
            connection = psycopg2.connect(
                database=self.db_name, user=self.user.username,
                password=self.user.password,
                host='localhost'
            )
        except psycopg2.Error as err:
            print(err)
        return connection

    def _get_tables(self) -> list:
        tables = []
        with self.connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT * FROM information_schema.tables WHERE table_schema='public'")
            tables = [item[2] for item in cursor.fetchall()]
        return tables

    def get_table(self, table_name: str):
        return Table(
            self,
            table_name
        )


class Table:
    def __init__(self, database: Database, table_name: str):
        self.database = database
        self.name = table_name
        self.columns = self.get_columns()
        self.data = self.get_data()

    def get_columns(self):
        with self.database.connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {self.name}")
                columns = [item[0] for item in cursor.description]
        return columns

    def get_data(self):
        with self.database.connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {self.name}")
                data = cursor.fetchall()
        return data

    def record_data(self, file_name: str):
        mytable = PrettyTable()
        mytable.field_names = self.columns
        mytable.add_rows(
            self.data
        )
        with open(file_name, "w") as file:
            table = mytable.get_string()
            file.write(table)
            file.write('\n')


class QueryManager:
    @staticmethod
    def create_database(db_name: str, username: str, password: str) -> Database:
        with closing(psycopg2.connect(user=username, password=password)) as conn:
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(db_name))
                )
        database = Database(
            user=User(username=username, password=password),
            db_name=db_name
        )
        return database



