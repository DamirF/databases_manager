from contextlib import closing
from datetime import datetime
import multiprocessing as mp
from tkinter import Tk, ttk
import tkinter as tk
import tkinter.messagebox as mb
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter.font import Font
from tkinter.ttk import Treeview
from typing import List

import psycopg2
from prettytable import PrettyTable
from psycopg2 import sql
from psycopg2.extras import DictCursor
import matplotlib.pyplot as plt
from numpy import exp, array
import numpy as np


def build_chart(x_values: list,
                y_values: list,
                x_label: str,
                y_label: str,
                title: str):
    if len(x_values) != len(y_values):
        return

    values_x = array(x_values)
    values_y = array(y_values)

    for x in values_x:
        plt.axvline(x=x)

    plt.plot(x_values, y_values, "bo")

    p = np.polyfit(values_x, values_y, 1)
    f = np.poly1d(p)
    plt.plot(values_x, f(values_x), 'b--', label='Approximation')

    plt.ylim([0, y_values[len(y_values) - 1] + y_values[0]])
    plt.xlim([0, x_values[len(x_values) - 1] + x_values[0]])

    for xy in zip(x_values, y_values):
        _xy = (xy[0], xy[1] - (y_values[0] / 2))
        plt.annotate('(%.4f)' % xy[1], xy=_xy)

    plt.xlabel(x_label)
    plt.ylabel(y_label)

    plt.title(title)
    plt.grid()
    plt.show()


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

    def refresh_info(self):
        self.tables = self._get_tables()


class Table:
    ALLOWED_SYMBOLS = "abcdefghijklmnopqrstuvwxyz_0123456789"

    def __init__(self, database: Database, table_name: str):
        self.database = database
        self.name = table_name
        self.get_data_timedelta = 0
        self.data_prepare_timedelta = 0
        self.data_insert_timedelta = 0
        self.columns_types = self.get_columns_types()
        print(self.columns_types)
        self.columns = self.get_columns()
        # self.data = self.get_data()

    def get_columns(self):
        with self.database.connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {self.name} LIMIT 1")
                columns = [item[0] for item in cursor.description]
        return columns

    def clear_data(self):
        self.data.clear()

    def get_columns_types(self):
        with self.database.connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS "
                    f"where TABLE_NAME = '{self.name}'"
                )
                ans = [str(item[0]).replace("integer", "int").replace("double precision", "float") for item in
                       cursor.fetchall()]
        return list(reversed(ans))

    def get_data(self) -> list:
        with self.database.connection as conn:
            with conn.cursor() as cursor:
                start_time = datetime.now()
                cursor.execute(f"SELECT * FROM {self.name}")
                data = cursor.fetchall()
                self.get_data_timedelta = (datetime.now() - start_time).total_seconds()
        return data

    def get_rows_count(self) -> int:
        with self.database.connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {self.name}")
                count = len(cursor.fetchall())
        return count

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

    @classmethod
    def value_validate(cls, value: str) -> bool:
        status = True
        if not value:
            status = False
            return status
        for char in value:
            if char not in cls.ALLOWED_SYMBOLS:
                status = False
                break
        return status

    @classmethod
    def create_in_db(cls, table_name: str,
                     table_data: List[dict],
                     database: Database):
        sql_query = "CREATE TABLE {}".format(table_name)
        sql_query += " ("

        for data_item in table_data:
            column = "{} {}".format(
                data_item["name"],
                data_item["type"],
            )
            column += " PRIMARY KEY" if data_item["is_unique"] else ""
            column += " NOT NULL" if data_item["null"] else ""
            column += ", " if table_data.index(data_item) != len(table_data) - 1 else ")"
            sql_query += column
        sql_query += ";"

        with database.connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql_query)
                conn.commit()

        return Table(database, table_name)

    def insert_data(self, data: list[list]) -> bool:
        status = True
        values_str = ""
        self.data_prepare_timedelta = 0
        data_prepare_start_time = datetime.now()
        for i in range(len(data)):
            data_row = "("
            for j in range(len(data[i])):
                if type(data[i][j]) is str or type(data[i][j]) is datetime:
                    data_row += "'{}'".format(str(data[i][j]))
                else:
                    data_row += str(data[i][j])

                if j != len(data[i]) - 1:
                    data_row += ", "
                else:
                    data_row += ")"
            if i % 1000:
                print(i)
            values_str += data_row

            if i != len(data) - 1:
                values_str += ", "
        self.data_prepare_timedelta = (datetime.now() - data_prepare_start_time).total_seconds()

        insert_query = "INSERT INTO {} VALUES".format(self.name) + values_str + ";"
        try:
            with self.database.connection as conn:
                with conn.cursor() as cursor:
                    start_time = datetime.now()
                    cursor.execute(insert_query)
                    conn.commit()
                    self.data_insert_timedelta = (datetime.now() - start_time).total_seconds()
        except Exception as _ex:
            print(_ex)
            status = False
        return status

    def delete_from_db(self):
        with self.database.connection as conn:
            with conn.cursor() as cursor:
                cursor.execute("DROP TABLE {};".format(self.name))
                conn.commit()

    def get_query_time(self, limit: int):
        with self.database.connection as conn:
            with conn.cursor() as cursor:
                start_time = datetime.now()
                cursor.execute(f"SELECT * FROM {self.name} LIMIT {limit}")
                data = cursor.fetchall()
                data_timedelta = round((datetime.now() - start_time).total_seconds(), 6)
        return data_timedelta


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


class StartWindow:
    def __init__(self, width=300, height=100,
                 maxwidth=300, maxheight=100,
                 minwidth=300, minheight=100):
        self.window = Tk()
        self.window.title("Старт")
        self.window.geometry("{}x{}".format(width, height))
        self.window.minsize(width=minwidth, height=minheight)
        self.window.maxsize(width=maxwidth, height=maxheight)
        for c in range(2):
            self.window.columnconfigure(index=c, weight=1)
        for r in range(2):
            self.window.rowconfigure(index=r, weight=1)

        self.btn1 = ttk.Button(text="Подключиться к БД", command=self.show_login)
        self.btn1.grid(row=0, column=0, columnspan=2, ipadx=70, ipady=6, padx=2, pady=2, sticky=tk.NSEW)

        self.btn2 = ttk.Button(text="Создать БД", command=self.show_create)
        self.btn2.grid(row=1, column=0, columnspan=2, ipadx=70, ipady=6, padx=2, pady=2, sticky=tk.NSEW)
        self.window.mainloop()

    def destroy(self):
        self.window.destroy()

    def show_login(self):
        self.destroy()
        LogInDatabase()

    def show_create(self):
        self.destroy()
        DatabaseCreateWindow()


class LogInDatabase:
    def __init__(self, width=300, height=400,
                 maxwidth=300, maxheight=400,
                 minwidth=300, minheight=400):
        self.window = Tk()
        self.window.title("Подключение к БД")
        self.window.geometry("{}x{}".format(width, height))
        self.window.minsize(width=minwidth, height=minheight)
        self.window.maxsize(width=maxwidth, height=maxheight)
        for c in range(2):
            self.window.columnconfigure(index=c, weight=1)
        for r in range(6):
            self.window.rowconfigure(index=r, weight=1)

        self.username_label = ttk.Label(justify="center", text="Имя пользователя", font=Font(name='Arial', size=16))
        self.username_label.grid(row=0, column=0, columnspan=2, ipadx=20, ipady=6, padx=5, pady=2)

        self.username_input = ttk.Entry(font=Font(name='Arial', size=16))
        self.username_input.grid(row=1, column=0, columnspan=2, ipadx=20, ipady=6, padx=5, pady=2)

        self.password_label = ttk.Label(justify="center", text="Пароль", font=Font(name='Arial', size=16))
        self.password_label.grid(row=2, column=0, columnspan=2, ipadx=20, ipady=6, padx=5, pady=2)

        self.password_input = ttk.Entry(show="*", font=Font(name='Arial', size=16))
        self.password_input.grid(row=3, column=0, columnspan=2, ipadx=20, ipady=6, padx=5, pady=2)

        self.database_label = ttk.Label(justify="center", text="База данных", font=Font(name='Arial', size=16))
        self.database_label.grid(row=4, column=0, columnspan=2, ipadx=20, ipady=6, padx=5, pady=2)

        self.database_input = ttk.Entry(font=Font(name='Arial', size=16))
        self.database_input.grid(row=5, column=0, columnspan=2, ipadx=20, ipady=6, padx=5, pady=2)

        self.btn1 = ttk.Button(text="Подключиться", command=self.login)
        self.btn1.grid(row=6, column=0, columnspan=2, ipadx=70, ipady=6, padx=2, pady=2)
        self.window.mainloop()

    def login(self):
        username = self.username_input.get()
        password = self.password_input.get()
        db_name = self.database_input.get()

        database = Database(user=User(username=username, password=password), db_name=db_name)
        if database.connection:
            self.destroy()
            DatabaseWindow(database=database)
        else:
            self.show_error("Invalid connection")

    def destroy(self):
        self.window.destroy()

    @classmethod
    def show_info(cls, message: str):
        mb.showinfo("Информация", message)

    @classmethod
    def show_warning(cls, message: str):
        mb.showwarning("Предупреждение", message)

    @classmethod
    def show_error(cls, message: str):
        mb.showerror("Ошибка", message)


class DatabaseCreateWindow:
    def __init__(self, width=300, height=400,
                 maxwidth=300, maxheight=400,
                 minwidth=300, minheight=400):
        self.window = Tk()
        self.window.title("Создание БД")
        self.window.geometry("{}x{}".format(width, height))
        self.window.minsize(width=minwidth, height=minheight)
        self.window.maxsize(width=maxwidth, height=maxheight)
        for c in range(2):
            self.window.columnconfigure(index=c, weight=1)
        for r in range(6):
            self.window.rowconfigure(index=r, weight=1)

        self.username_label = ttk.Label(justify="center", text="Имя пользователя", font=Font(name='Arial', size=16))
        self.username_label.grid(row=0, column=0, columnspan=2, ipadx=20, ipady=6, padx=5, pady=2)

        self.username_input = ttk.Entry(font=Font(name='Arial', size=16))
        self.username_input.grid(row=1, column=0, columnspan=2, ipadx=20, ipady=6, padx=5, pady=2)

        self.password_label = ttk.Label(justify="center", text="Пароль", font=Font(name='Arial', size=16))
        self.password_label.grid(row=2, column=0, columnspan=2, ipadx=20, ipady=6, padx=5, pady=2)

        self.password_input = ttk.Entry(show="*", font=Font(name='Arial', size=16))
        self.password_input.grid(row=3, column=0, columnspan=2, ipadx=20, ipady=6, padx=5, pady=2)

        self.password_conf_label = ttk.Label(justify="center", text="Подтвердите пароль",
                                             font=Font(name='Arial', size=16))
        self.password_conf_label.grid(row=4, column=0, columnspan=2, ipadx=20, ipady=6, padx=5, pady=2)

        self.password_conf_input = ttk.Entry(show="*", font=Font(name='Arial', size=16))
        self.password_conf_input.grid(row=5, column=0, columnspan=2, ipadx=20, ipady=6, padx=5, pady=2)

        self.database_label = ttk.Label(justify="center", text="Имя БД", font=Font(name='Arial', size=16))
        self.database_label.grid(row=6, column=0, columnspan=2, ipadx=20, ipady=6, padx=5, pady=2)

        self.database_input = ttk.Entry(font=Font(name='Arial', size=16))
        self.database_input.grid(row=7, column=0, columnspan=2, ipadx=20, ipady=6, padx=5, pady=2)

        self.btn1 = ttk.Button(text="Создать", command=self.create)
        self.btn1.grid(row=8, column=0, columnspan=2, ipadx=70, ipady=6, padx=2, pady=2)
        self.window.mainloop()

    def create(self):
        username = self.username_input.get()
        password = self.password_input.get()
        pass_conf = self.password_conf_input.get()
        db_name = self.database_input.get()

        if password != pass_conf:
            self.show_error("Пароли не совпадают")
            return
        else:
            try:
                database = QueryManager.create_database(
                    db_name=db_name,
                    username=username,
                    password=password
                )
                self.destroy()
                DatabaseWindow(database)
            except Exception as _ex:
                self.show_error(str(_ex))

    def destroy(self):
        self.window.destroy()

    @classmethod
    def show_info(cls, message: str):
        mb.showinfo("Информация", message)

    @classmethod
    def show_warning(cls, message: str):
        mb.showwarning("Предупреждение", message)

    @classmethod
    def show_error(cls, message: str):
        mb.showerror("Ошибка", message)


class DatabaseWindow:
    def __init__(self, database: Database,
                 width=800, height=600,
                 maxwidth=800, maxheight=600,
                 minwidth=800, minheight=600
                 ):
        self.window = Tk()
        self.database = database
        self.database.refresh_info()
        self.window.title("Подключено к " + str(self.database.db_name))
        self.window.geometry("{}x{}".format(width, height))
        self.window.minsize(width=minwidth, height=minheight)
        self.window.maxsize(width=maxwidth, height=maxheight)
        for c in range(1):
            self.window.columnconfigure(index=c, weight=1)
        for r in range(6):
            self.window.rowconfigure(index=r, weight=1)

        canvas = tk.Canvas(self.window, borderwidth=0, background="#ffffff")
        frame = tk.Frame(canvas, background="#ffffff")
        vsb = tk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((4, 4), window=frame, anchor="nw")

        table_btns = [tk.Button(frame, text=table, command=lambda i=str(table): self.get_table_data(i))
                      for table in self.database.tables]

        for btn in table_btns:
            btn.pack(fill="x", ipadx=70, ipady=6, padx=2, pady=2)

        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        to_start_btn = tk.Button(self.window, text="Начало", font=("Arial", 16, "bold"), command=self.to_start)
        to_start_btn.pack(fill=tk.X, side=tk.BOTTOM)

        to_start_btn = tk.Button(self.window, text="Создать таблицу", font=("Arial", 16, "bold"),
                                 command=self.create_table)
        to_start_btn.pack(fill=tk.X, side=tk.BOTTOM)
        self.window.mainloop()

    def destroy(self):
        self.window.destroy()

    def get_table_data(self, table_name: str):
        self.destroy()
        TableDataWindow(self.database, table_name)

    def to_start(self):
        self.destroy()
        StartWindow()

    def create_table(self):
        self.destroy()
        CreateTableConfigurationWindow(self.database)


class TableDataWindow:
    def __init__(self, database: Database, table_name: str,
                 width=800, height=600,
                 maxwidth=800, maxheight=600,
                 minwidth=800, minheight=600
                 ):
        self.window = Tk()
        self.database = database
        print(database.connection)
        self.table_name = table_name
        self.table = database.get_table(self.table_name)
        self.data = self.table.get_data()
        self.rows_count = self.table.get_rows_count()
        print(self.table.columns)
        self.window.title(database.db_name + ": " + table_name + "(view)")
        self.window.geometry("{}x{}".format(width, height))
        self.window.state('zoomed')

        # Create view area with scrollbars
        canvas = tk.Canvas(self.window, width=1000, height=800, borderwidth=0, background="#ffffff")
        frame = tk.Frame(canvas, width=1000, height=800, background="#ffffff")
        canvas.pack(side="top", fill="both", expand=True)
        canvas.create_window((0, 0), window=frame, anchor=tk.CENTER)

        tree = Treeview(frame, columns=self.table.columns, show="headings")
        tree.pack(fill=tk.X, expand=1)

        for column in self.table.columns:
            tree.heading(column, text=column, anchor=tk.W)

        for row in self.data:
            tree.insert("", tk.END, values=row)

        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        return_btn = tk.Button(canvas, text="Назад",
                               command=self.return_to_database, font=("Arial", 16, "bold"))
        return_btn.pack(side="bottom", ipadx=70, ipady=10, fill=tk.X)

        save_btn = tk.Button(canvas, text="Сохранить в файл",
                             command=self.save_table, font=("Arial", 16, "bold"))
        save_btn.pack(side="bottom", ipadx=70, ipady=10, fill=tk.X)

        add_data_btn = tk.Button(canvas, text="Импортировать данные",
                                 command=self.add_data_to_table, font=("Arial", 16, "bold"))
        add_data_btn.pack(side="bottom", ipadx=70, ipady=10, fill=tk.X)

        add_data_btn = tk.Button(canvas, text="Построить график",
                                 command=self.get_chart, font=("Arial", 16, "bold"))
        add_data_btn.pack(side="bottom", ipadx=70, ipady=10, fill=tk.X)

        get_data_timedelta_label = tk.Label(canvas,
                                            text="Время получения данных: " + str(self.table.get_data_timedelta),
                                            font=("Arial", 16, "bold")
                                            )
        get_data_timedelta_label.pack(side="bottom", ipadx=70, ipady=10, fill=tk.X)

        data_rows_count_label = tk.Label(canvas,
                                         text="Кол-во записей: " + str(len(self.data)),
                                         font=("Arial", 16, "bold")
                                         )
        data_rows_count_label.pack(side="bottom", ipadx=70, ipady=10, fill=tk.X)

        self.window.mainloop()

    def destroy(self):
        self.window.destroy()

    @classmethod
    def show_info(cls, message: str):
        mb.showinfo("Информация", message)

    @classmethod
    def show_error(cls, message: str):
        mb.showerror("Ошибка", message)

    def return_to_database(self):
        self.destroy()
        DatabaseWindow(self.database)

    def get_counts_for_chart(self):
        counter = int(self.rows_count / 10)
        return [i * counter for i in range(1, 11)]

    def get_chart(self):
        counts = self.get_counts_for_chart()
        times = [self.table.get_query_time(count) for count in counts]
        print(counts)
        print(times)
        build_chart(counts, times, "Rows count", "Query Time", self.table.name)

    def save_table(self):
        file_name = asksaveasfilename(defaultextension=".txt")
        if file_name:
            self.table.record_data(file_name)
            self.show_info("Таблица успешно сохранена.")
        else:
            self.show_error("Необходимо выбрать файл!")

    def add_data_to_table(self):
        self.destroy()
        CreateTableDataWindow(self.table_name, self.database,
                              types_list=self.table.columns_types,
                              create_table=False)


class ColumnElement:
    COLUMN_TYPES = {
        "Число": "int",
        "Число с запятой": "float",
        "Строка": "text",
        "Дата/время": "timestamp"
    }

    COLUMN_TYPES_RUS = [
        "Число",
        "Число с запятой",
        "Строка",
        "Дата/время"
    ]

    ALLOWED_SYMBOLS = "abcdefghijklmnopqrstuvwxyz_0123456789"

    def __init__(self, container: tk.Frame):
        self.container = container
        self.frame = tk.Frame(self.container, border=5)
        self.entry = tk.Entry(self.frame,
                              font=("Arial", 16, "normal"),
                              border=4)
        self.types = ttk.Combobox(self.frame,
                                  values=self.COLUMN_TYPES_RUS,
                                  state="readonly")
        self.types.current(0)
        self.is_unique_var = tk.IntVar()
        self.is_null_var = tk.IntVar(value=1)
        self.is_unique = tk.Checkbutton(self.frame, text="Уникальное значение", variable=self.is_unique_var)
        self.is_null = tk.Checkbutton(self.frame, text="Разрешено пустое значение", variable=self.is_null_var)

    def pack(self):
        self.frame.pack(fill=tk.X, anchor="se", ipady=10)
        self.entry.pack(fill=tk.X, padx=10, pady=5, ipady=3, anchor="center")
        self.types.pack(fill=tk.X, padx=10, pady=5, ipady=3, anchor="center")
        self.is_unique.pack(fill=tk.X, padx=10, pady=5, ipady=3, anchor="center")
        self.is_null.pack(fill=tk.X, padx=10, pady=5, ipady=3, anchor="center")

    def destroy(self):
        self.types.destroy()
        self.entry.destroy()
        self.is_unique.destroy()
        self.frame.destroy()

    def to_dict(self) -> dict:
        return {
            "name": self.entry.get(),
            "is_unique": bool(self.is_unique_var.get()),
            "type": self.COLUMN_TYPES[self.types.get()],
            "null": bool(self.is_null_var.get())
        }

    def name_validate(self) -> bool:
        status = True
        name = self.entry.get()
        for char in name:
            if char not in self.ALLOWED_SYMBOLS:
                status = False
                break
        return status


class CreateTableConfigurationWindow:
    def __init__(self, database: Database,
                 width=800, height=600,
                 maxwidth=800, maxheight=600,
                 minwidth=800, minheight=600
                 ):
        self.window = Tk()
        self.database = database
        self.window.title("Создание таблицы в БД: " + str(self.database.db_name) + ": Конфигурация")
        self.window.geometry("{}x{}".format(width, height))
        self.window.minsize(width=minwidth, height=minheight)
        self.window.maxsize(width=maxwidth, height=maxheight)

        for c in range(4):
            self.window.columnconfigure(index=c, weight=1)
        for r in range(1):
            self.window.rowconfigure(index=r, weight=1)

        self.left_frame = tk.Frame(self.window)
        self.left_frame.grid(columnspan=3, column=0, ipadx=6, ipady=6, padx=5, pady=5, sticky="NSEW")
        self.right_frame = tk.Frame(self.window, border=5)
        self.right_frame.grid(row=0, column=3, ipadx=6, ipady=6, padx=5, pady=5, sticky="NSEW")

        self.canvas = tk.Canvas(self.left_frame, borderwidth=0, background="#ffffff")
        self.columns_container = tk.Frame(self.canvas, background="#ffffff")
        self.vsb = tk.Scrollbar(self.left_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.columns_container, anchor="nw")

        self.columns = [ColumnElement(self.columns_container)]

        for column in self.columns:
            column.pack()

        # Controllers area

        self.name_entry_label = tk.Label(self.right_frame, font=("Arial", 16, "bold"), text="Имя таблицы")

        self.name_entry = tk.Entry(self.right_frame, font=("Arial", 16, "bold"))

        self.name_entry_label.pack(fill=tk.X, side=tk.TOP)
        self.name_entry.pack(fill=tk.X, side=tk.TOP)

        self.add_column_btn = tk.Button(self.right_frame, text="Добавить столбец", font=("Arial", 16, "bold"),
                                        command=self.add_column)

        self.delete_column_btn = tk.Button(self.right_frame, text="Удалить столбец", font=("Arial", 16, "bold"),
                                           command=self.delete_column)

        self.next_step_btn = tk.Button(self.right_frame, text="Далее", font=("Arial", 16, "bold"),
                                       command=self.to_next_step)

        self.columns_counter = tk.Label(self.right_frame,
                                        text="Количество: " + str(len(self.columns)),
                                        font=("Arial", 16, "bold"))

        self.next_step_btn.pack(fill=tk.X, side=tk.BOTTOM)
        self.delete_column_btn.pack(fill=tk.X, side=tk.BOTTOM)
        self.add_column_btn.pack(fill=tk.X, side=tk.BOTTOM)
        self.columns_counter.pack(fill=tk.X, side=tk.BOTTOM)

        self.update_canvas()
        self.window.mainloop()

    def destroy(self):
        self.window.destroy()

    @classmethod
    def show_info(cls, message: str):
        mb.showinfo("Информация", message)

    @classmethod
    def show_error(cls, message: str):
        mb.showerror("Ошибка", message)

    def to_start(self):
        self.destroy()
        StartWindow()

    def update_canvas(self):
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def add_column(self):
        column = ColumnElement(self.columns_container)
        self.columns.append(column)
        column.pack()
        self.columns_counter.config(text="Количество: " + str(len(self.columns)))
        self.update_canvas()

    def delete_column(self):
        if len(self.columns) <= 1:
            return
        to_delete_entry = self.columns[len(self.columns) - 1]
        to_delete_entry.destroy()
        self.columns.remove(to_delete_entry)
        self.columns_counter.config(text="Количество: " + str(len(self.columns)))
        self.update_canvas()

    def check_columns(self):
        status = True
        for column_elem in self.columns:
            if column_elem.entry.get() == "":
                status = False
                break
        return status

    def have_repeated_columns(self):
        column_names = [column_elem.entry.get() for column_elem in self.columns]
        setarr = set(column_names)
        if len(column_names) == len(setarr):
            return False
        else:
            return True

    def to_next_step(self):
        table_name = self.name_entry.get()
        if not Table.value_validate(table_name):
            self.show_error("Недопустимое имя таблицы")
            return
        if table_name in self.database.tables:
            self.show_error("Таблица с таким именем уже существует!")
            return
        if not self.check_columns():
            self.show_error("Заполните все поля!")
            return
        if self.have_repeated_columns():
            self.show_error("Имеются дублирующиеся имена!")
            return

        for column_elem in self.columns:
            if not column_elem.name_validate():
                self.show_error("В имени {} имеются неразрешенные символы".format(column_elem.entry.get()))
                return

        columns_info = [column_elem.to_dict() for column_elem in self.columns]

        for column in columns_info:
            if column["is_unique"] and column["null"]:
                self.show_error("Уникальное значение не может быть пустым ({})".format(column["name"]))
                return

        self.destroy()
        CreateTableDataWindow(table_name, self.database, columns_info)


class CreateTableDataWindow:
    def __init__(self, table_name: str,
                 database: Database,
                 table_conf=None,
                 types_list: List[str] = None,
                 create_table=True,
                 width=400, height=400,
                 maxwidth=400, maxheight=400,
                 minwidth=400, minheight=400):
        self.window = Tk()
        self.database = database
        self.table_name = table_name
        self.table_conf = table_conf
        self.create_table = create_table
        self.types_list = types_list
        self.insert_data = []
        self.import_status = False
        self.window.title("Создание таблицы в БД: " + str(self.database.db_name) + ": Импорт данных")
        self.window.geometry("{}x{}".format(width, height))
        self.window.minsize(width=minwidth, height=minheight)
        self.window.maxsize(width=maxwidth, height=maxheight)

        self.table_name_label = tk.Label(self.window, text="Имя таблицы: {}".format(self.table_name),
                                         font=("Arial", 16, "bold"))
        self.table_name_label.pack(fill=tk.X)

        self.import_btn = tk.Button(self.window, border=5, text="Импорт из файла",
                                    font=("Arial", 16, "bold"), command=self.get_insert_data)
        self.import_btn.pack(fill=tk.X, ipady=10, padx=10)

        self.import_status_label = tk.Label(self.window, text="Статус импорта: Нет",
                                            font=("Arial", 12, "bold"))
        self.import_status_label.pack(fill=tk.X)

        self.table_save_btn = tk.Button(self.window, border=5, text="Сохранить таблицу",
                                        font=("Arial", 16, "bold"), command=self.save_table, state="disabled")
        self.table_save_btn.pack(fill=tk.X, ipady=10, padx=10)

        self.import_info_label = tk.Label(self.window, text="Информация по импорту",
                                          font=("Arial", 12, "bold"))
        self.import_info_label.pack(fill=tk.X)

        self.import_info_data_count_label = tk.Label(self.window, text="Количество строк: -",
                                                     font=("Arial", 12, "bold"))
        self.import_info_data_count_label.pack(fill=tk.X)

        self.import_info_data_prepare_label = tk.Label(self.window, text="Подготовка данных \nдля запроса: -",
                                                       font=("Arial", 12, "bold"))
        self.import_info_data_prepare_label.pack(fill=tk.X)

        self.import_info_data_insert_label = tk.Label(self.window, text="Время выполнения запроса: -",
                                                      font=("Arial", 12, "bold"))
        self.import_info_data_insert_label.pack(fill=tk.X)

        self.move_to_table_btn = tk.Button(self.window, border=5, text="Перейти к таблице",
                                           font=("Arial", 16, "bold"), command=self.move_to_table, state="disabled")
        self.move_to_table_btn.pack(fill=tk.X, ipady=10, padx=10)

        self.window.mainloop()

    def destroy(self):
        self.window.destroy()

    @classmethod
    def show_info(cls, message: str):
        mb.showinfo("Информация", message)

    @classmethod
    def show_error(cls, message: str):
        mb.showerror("Ошибка", message)

    def get_types_list(self) -> List[str]:
        return [column.get("type") for column in self.table_conf]

    @staticmethod
    def types_parse(types: List[str], data: List[str]) -> list:
        if len(types) != len(data):
            raise Exception("Incorrect data")
        parsed_data = []
        for i in range(len(data)):
            if types[i] == "int":
                try:
                    parsed_data.append(int(data[i]))
                except Exception as _ex:
                    raise _ex
            elif types[i] == "float":
                try:
                    parsed_data.append(float(data[i]))
                except Exception as _ex:
                    raise _ex
            elif types[i] == "text":
                try:
                    parsed_data.append(str(data[i]))
                except Exception as _ex:
                    raise _ex
            elif types[i] == "timestamp":
                try:
                    parsed_data.append(datetime.strptime(data[i], "%Y-%m-%d %H:%M:%S.%f"))
                except Exception as _ex:
                    raise _ex
        return parsed_data

    @staticmethod
    def open_file(filepath: str, types: list[str]):
        data = []
        if filepath != "":
            with open(filepath, "r", encoding="utf-8") as file:

                for line in file:
                    data.append(line.split("\t"))

        typed_data = [CreateTableDataWindow.types_parse(types, item) for item in data]
        return typed_data

    def get_insert_data(self):
        filepath = askopenfilename(filetypes=(('text files', 'txt'),))
        preapared_data = []
        types = self.get_types_list() if self.create_table else self.types_list
        line_counter = 0
        pool = mp.Pool(5)
        jobs = []
        try:
            typed_data = self.open_file(filepath, types)

            self.import_status_label.configure(text="Статус импорта: Успех")
            self.import_status = True
            self.table_save_btn.configure(state="normal")
            self.insert_data = typed_data
            self.import_info_data_count_label.configure(text="Количество строк: " + str(len(self.insert_data)))
        except Exception as _ex:
            print(_ex)
            self.show_error("Невозможно прочитать файл!")
            self.import_status_label.configure(text="Статус импорта: Ошибка")
            self.import_status = False
            self.table_save_btn.configure(state="disabled")

    def save_table(self):
        table = Table.create_in_db(self.table_name, self.table_conf, self.database) \
            if self.create_table else self.database.get_table(self.table_name)
        insert_status = table.insert_data(self.insert_data)
        if insert_status:
            self.move_to_table_btn.configure(state="normal")
            self.import_info_data_prepare_label.configure(text="Подготовка данных \nдля запроса: " +
                                                               str(table.data_prepare_timedelta) + " секунд")
            self.import_info_data_insert_label.configure(text="Время выполнения запроса: " +
                                                              str(table.data_insert_timedelta) + " секунд")
        else:
            if self.create_table:
                table.delete_from_db()
            self.show_error("Ошибка")

    def move_to_table(self):
        self.destroy()
        TableDataWindow(self.database, self.table_name)


def main():
    app = StartWindow()


if __name__ == "__main__":
    main()