#!/usr/bin/env python
# -*- coding:utf-8 -*-

import platform
import os, sys, pip

def install(package):
    pip.main(['install', package])


if __name__ == '__main__':
    # Производим активацию virtualenv
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ACTIVATE_SCRIPT = os.path.join(BASE_DIR, 'Scripts', 'activate_this.py')
    activate_env=os.path.expanduser(ACTIVATE_SCRIPT)
    with open(activate_env) as f:
        code = compile(f.read(), activate_env, 'exec')
        exec(code, dict(__file__=activate_env))

    
    CPU_ARCH = platform.architecture()[0]
    print('-------------------------------------------------')
    print('--------Установка пакетов зависимостей-----------')
    print('-------------------------------------------------')
    try:
        if CPU_ARCH == '64bit':
            print('Установка пакетов зависимостей для 64 битной Windows')
            install('Django==1.9.4')
            install('Noarch/django-mptt-0.8.0.tar.gz')
            install('Win64/lxml-3.4.4-cp34-none-win_amd64.whl')
            install('Win64/Pillow-3.1.0-cp34-none-win_amd64.whl')
            install('Win64/psycopg2-2.6.1-cp34-none-win_amd64.whl')
            install('Noarch/python-docx-0.8.5.tar.gz')
        elif CPU_ARCH == '32bit':
            print('Установка пакетов зависимостей для 32 битной Windows')
            install('Django==1.9.4')
            install('Noarch/django-mptt-0.8.0.tar.gz')
            install('Win32/lxml-3.4.4-cp34-none-win32.whl')
            install('Win32/Pillow-3.1.0-cp34-none-win32.whl')
            install('Win32/psycopg2-2.6.1-cp34-none-win32.whl')
            install('Noarch/python-docx-0.8.5.tar.gz')
        else:
            print('Поддержка данных процессоров не релизована.')
    except:
        print('Дальнейшее продолжение установки невозможно!')
    else:
        # производим запуск миграции схемы Severcart и Django        
        sys.path.append(os.path.join(BASE_DIR, 'Severcart'))
        sys.path.append(os.path.join(BASE_DIR, 'Severcart', 'newskald_ru'))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newskald_ru.settings')

        import django
        from django.conf import settings
        from django.core.management import execute_from_command_line

        django.setup()

        print('-------------------------------------------------')
        print('-----------------Миграция схемы------------------')
        print('-------------------------------------------------')
        try:
            execute_from_command_line(['manage.py', 'migrate'])
        except:
            print('В процессе миграции произошла ошибка.')
        else:
            print('Схема успешно мигрирована.')
        
        # создаём суперпользователя admin
        from accounts.models import AnconUser
        from django.db import IntegrityError
        print('-------------------------------------------------')
        print('--------------Создание пользователя--------------')
        print('-------------------------------------------------')
        flag = True
        while flag:
            u = input('Ввведите имя пользователя: ')
            u = u.strip()
            user = AnconUser(username=u, is_admin = True)
            m1 = AnconUser.objects.filter(username=u)
            if m1:
                print('Пользователь с именем %s уже существует. Повторите ввод.' % (u,))
            else:
                flag = False

        flag = True
        while flag:
            p1 = input('Введите пароль:   ')
            p2 = input('Повторите пароль: ')

            if p1 == p2:
                user.set_password(p1)
                user.save()
                print('Пользователь %s успешно создан.' % (u,))
                flag = False
            else:
                print('Пароли не совпадают. Повторите ввод.')
                # возвращаемся к началу цикла
                flag = True

        print('-------------------------------------------------')
        print('----------Установка успешно завершена------------')
        print('-------------------------------------------------')
