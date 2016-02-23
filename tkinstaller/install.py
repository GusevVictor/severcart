#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, sys
import subprocess
import psycopg2
import tkinter as tk

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
        self.app = Page3(parent=self.page2)

class Page3(object):
    """Main class.
    """
    def __init__(self, parent):
        self.no_errors = False
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
        self.proc.terminate()
        self.proc.kill()
        sys.exit(1)

    def action(self):
        # некоторые действия
        self.no_errors = True
        if self.no_errors:
            self.page3_next = tk.Button(self.page3, text='Далее', command=self.new_window)
            self.page3_next.pack(fill=tk.X)
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
        #C:\work\OpenServer\modules\database\PostgreSQL-9.4\bin\pg_ctl
         #start -D "c:/work/openserver/userdata/PostgreSQL-9.4"
        self.text.insert(tk.END, 'Start PostgreSQL' + '\n')
        db_ready = False
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
            

          
        #for i in range(100):
        #    self.text.insert(tk.END, str(i)+ '\n')
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
    
