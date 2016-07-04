#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, sys
import subprocess
import psycopg2
import tkinter as tk

sys.exit(1)

user_name     = ''
user_password = ''

def set_window_center(obj):
    obj.update_idletasks()
    ws = obj.winfo_screenwidth()
    hs = obj.winfo_screenheight()
    
    w = obj.winfo_width()
    h = obj.winfo_height()
    
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    
    obj.geometry('+%d+%d' % (x, y,))


class Page1(object):
    def __init__(self, master):
        self.page2  = ''
        self.master = master
        set_window_center(self.master)
        self.master.title('Severcart installer GUI')
        self.welcome = tk.Label(self.master, text='Приветственное слово инсталлятора')
        self.welcome.pack(fill=tk.X)
        self.install_button = tk.Button(self.master, text='Далее', command=self.new_window)
        self.install_button.pack(fill=tk.X)
        self.install_exit = tk.Button(self.master, text='Выход', command=(lambda : sys.exit(1)))
        self.install_exit.pack(fill=tk.X)

    def new_window(self):
        self.app = Page2(parent=self.master)

class Page2(object):
    def __init__(self, parent):
        self.parent = parent
        self.page2 = tk.Toplevel(self.parent) # создаём дочернее окно
        self.page2.protocol('WM_DELETE_WINDOW', lambda: sys.exit(1))
        self.page2.geometry('350x200')
        self.parent.withdraw() # скрываем родительское окно
        set_window_center(self.page2)  # центрируем по середине
        self.L1 = tk.Label(self.page2, text='Логин')
        self.L1.pack()
        self.login = tk.Entry(self.page2)
        self.login.pack()
        self.L2 = tk.Label(self.page2, text='Пароль')
        self.L2.pack()
        self.password = tk.Entry(self.page2)
        self.password.pack()
        self.page2_next = tk.Button(self.page2, text='Далее', command=self.new_window)
        self.page2_next.pack(fill=tk.X)
        self.page2_exit = tk.Button(self.page2, text='Назад', command=self.back)
        self.page2_exit.pack(fill=tk.X)

    def back(self):
        #self.parent.update()
        self.parent.deiconify() # возвращаем показ родительского окна
        self.page2.destroy()

    def new_window(self):
        global user_name
        user_name = self.login.get()
        global user_password
        user_password = self.password.get()
        self.app = Page3(parent=self.page2)

class Page3(object):
    """Main class.
    """
    def __init__(self, parent):
        self.no_errors = False
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.django_base_path = os.path.join(self.base_path, 'ancon', 'conf')
        self.postgresql_db_path = ''
        self.postgresql_bin_path = ''
        self.proc = ''
        self.parent = parent
        self.page3 = tk.Toplevel(self.parent) # создаём дочернее окно
        self.page3.protocol('WM_DELETE_WINDOW', lambda: self.oexit())
        self.page3.geometry('600x400')
        self.parent.withdraw()
        set_window_center(self.page3)
        # скролл бар для пролистывания сообщений
        self.scroll = tk.Scrollbar(self.page3)
        # текстовое поле отображения диагностических сообщений
        self.text = tk.Text(self.page3, width=60, height=10, padx=5, pady=5) # state=tk.DISABLED
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.pack(side=tk.LEFT, fill=tk.Y)
        self.scroll.config(command=self.text.yview)
        self.text.config(yscrollcommand=self.scroll.set)
        self.page3_exit = tk.Button(self.page3, text='Назад', command=self.back)
        self.page3_exit.pack(fill=tk.X)
        self.action()

    def back(self):
        self.parent.deiconify()
        self.page3.destroy()

    def oexit(self):
        self.proc = subprocess.Popen([self.postgresql_bin_path, 'stop', '-D', self.postgresql_db_path])
        sys.exit(1)

    def action(self):
        # основные манипуляции по установке ПП Severcart
        # запуск базы данных
        self.postgresql_db_path = os.path.join(self.base_path,
                                            'userdata',
                                            'PostgreSQL-9.4')
        self.postgresql_bin_path = os.path.join(self.base_path,
                                            'modules',
                                            'database',
                                            'PostgreSQL-9.4',
                                            'bin',
                                            'pg_ctl.exe')

        # start postgresql        
        db_ready = False
        try:
            conn = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password=''")
        except:
            pass
        else:
            db_ready = True
        if  not db_ready:
            try:
                self.proc = subprocess.Popen([self.postgresql_bin_path, 'start', '-D', self.postgresql_db_path])
            except:
                self.text.insert(tk.END, 'PostgreSQL not start.' + '\n')
            else:
                self.text.insert(tk.END, 'Start PostgreSQL success.' + '\n')
                db_ready = True

        if db_ready:
            # create db severcart
            try:
                conn = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password=''")
            except:
                self.text.insert(tk.END, 'I am unable to connect to the database.' + '\n')
            else:
                self.text.insert(tk.END, 'Connect PostgreSQL success.' + '\n')

            sql_create_base = """
                CREATE DATABASE severcart
                WITH OWNER = postgres
                ENCODING = 'UTF8'
                TABLESPACE = pg_default
                LC_COLLATE = 'Russian_Russia.1251'
                LC_CTYPE = 'Russian_Russia.1251'
                CONNECTION LIMIT = -1;
            """
            try:
                cur = conn.cursor()
                conn.set_isolation_level(0)
                cur.execute(sql_create_base)
                conn.set_isolation_level(1)
            except psycopg2.ProgrammingError as e:
                self.text.insert(tk.END, str(e) + '\n')
            else:
                self.text.insert(tk.END, 'Database severcart created.' + '\n')

            # migrate python schema
            sys.path.append(os.path.join(self.base_path, 'ancon'))
            sys.path.append(os.path.join(self.base_path, 'ancon', 'conf'))
            sys.path.append(os.path.join(self.base_path, 'venv', 'Scripts'))
            # Activate your virtual env
            activate_env=os.path.expanduser(os.path.join(self.base_path, 'venv', 'Scripts', 'activate_this.py'))
            with open(activate_env) as f:
                code = compile(f.read(), activate_env, 'exec')
                exec(code, dict(__file__=activate_env))

            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings-prod')
            from django.core.management import execute_from_command_line
            migrate_ok = False
            try:
                execute_from_command_line(['manage.py', 'migrate'])
            except:
                self.text.insert(tk.END, 'В процессе миграции произошла ошибка.' + '\n')
            else:
                self.text.insert(tk.END, 'Схема успешно мигрирована.' + '\n')
                migrate_ok = True

            if migrate_ok:
                # создание нового административного пользователя
                from accounts.models import AnconUser
                try:
                    user = AnconUser(username=user_name, is_admin = True)
                    user.set_password(user_password)
                    user.save()
                except:
                    self.text.insert(tk.END, 'В процессе создания пользователя возникли ошибки.' + '\n')
                else:
                    self.text.insert(tk.END, 'Пользователь успешно создан.' + '\n')
                    self.page3_next = tk.Button(self.page3, text='Далее', command=self.new_window)
                    self.page3_next.pack(fill=tk.X)


    def new_window(self):
        self.app = Page4(parent=self.page3)


class Page4(object):
    def __init__(self, parent):
        self.parent = parent
        self.page4 = tk.Toplevel(self.parent)
        self.page4.protocol('WM_DELETE_WINDOW', lambda: sys.exit(1))
        self.parent.withdraw()
        set_window_center(self.page4)
        self.page4_finish = tk.Button(self.page4, text='Финиш', command=(lambda : sys.exit(1)))
        self.page4_finish.pack(fill=tk.X)
        self.page4_exit = tk.Button(self.page4, text='Назад', command=self.back)
        self.page4_exit.pack(fill=tk.X)
        self.finish = tk.Label(self.page4, text='Программа установлена. Для продолжения откройте в браузере http://127.0.0.1:80')
        self.finish.pack(fill=tk.X)

    def back(self):
        self.parent.deiconify()
        self.page4.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('350x200')
    root.protocol('WM_DELETE_WINDOW', lambda: sys.exit(1))
    my_gui = Page1(root)
    root.mainloop()
    
