from tkinter import Tk, ttk
import tkinter as tk
import tkinter.messagebox as mb
from tkinter.filedialog import asksaveasfilename
from tkinter.font import Font
from tkinter.ttk import Treeview

from postgres.models import Database, User, QueryManager


class StartWindow:
    def __init__(self, width=300, height=100,
                 maxwidth=300, maxheight=100,
                 minwidth=300, minheight=100):
        self.window = Tk()
        self.window.title("Старт")
        self.window.geometry("%dx%d".format(width, height))
        self.window.minsize(width=minwidth, height=minheight)
        self.window.maxsize(width=maxwidth, height=maxheight)
        for c in range(2):
            self.window.columnconfigure(index=c, weight=1)
        for r in range(2):
            self.window.rowconfigure(index=r, weight=1)

        self.btn1 = ttk.Button(text="Подключиться к БД", command=self.show_login)
        self.btn1.grid(row=0, column=0, columnspan=2, ipadx=70, ipady=6, padx=2, pady=2)

        self.btn2 = ttk.Button(text="Создать БД", command=self.show_create)
        self.btn2.grid(row=1, column=0, columnspan=2, ipadx=70, ipady=6, padx=2, pady=2)
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
        self.window.geometry("%dx%d".format(width, height))
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
        self.window.geometry("%dx%d".format(width, height))
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
        self.window.geometry("%dx%d".format(width, height))
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

        to_start_btn = tk.Button(self.window, text="Создать таблицу", font=("Arial", 16, "bold"), command=self.to_start)
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
        self.window.geometry("%dx%d".format(width, height))
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





