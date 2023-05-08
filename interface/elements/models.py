from tkinter import Tk, ttk
import tkinter as tk
import tkinter.messagebox as mb
from tkinter.filedialog import asksaveasfilename
from tkinter.font import Font
from tkinter.ttk import Treeview
from typing import Dict, List

from postgres.models import Database, User, QueryManager, Table


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

        for row in self.table.data:
            tree.insert("", tk.END, values=row)

        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        return_btn = tk.Button(canvas, text="Назад", command=self.return_to_database, font=("Arial", 16, "bold"))
        return_btn.pack(side="bottom", ipadx=70, ipady=10, fill=tk.X)

        save_btn = tk.Button(canvas, text="Сохранить в файл", command=self.save_table, font=("Arial", 16, "bold"))
        save_btn.pack(side="bottom", ipadx=70, ipady=10, fill=tk.X)

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

    def save_table(self):
        file_name = asksaveasfilename(defaultextension=".txt")
        if file_name:
            self.table.record_data(file_name)
            self.show_info("Таблица успешно сохранена.")
        else:
            self.show_error("Необходимо выбрать файл!")


class ColumnElement:
    COLUMN_TYPES = {
        "Число": "int",
        "Число с запятой": "float",
        "Строка": "text",
        "Дата/время": "datetime"
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
        CreateTableDataWindow(table_name, columns_info, self.database)


class CreateTableDataWindow:
    def __init__(self, table_name: str,
                 table_conf: List[dict[str, str | str, int]],
                 database: Database,
                 width=800, height=600,
                 maxwidth=800, maxheight=600,
                 minwidth=800, minheight=600):
        self.window = Tk()
        self.database = database
        self.table_name = table_name
        self.table_conf = table_conf
        self.window.title("Создание таблицы в БД: " + str(self.database.db_name) + ": Импорт данных")
        self.window.geometry("{}x{}".format(width, height))
        self.window.minsize(width=minwidth, height=minheight)
        self.window.maxsize(width=maxwidth, height=maxheight)

        Table.create_in_db(self.table_name, self.table_conf)

        self.window.mainloop()







