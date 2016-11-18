#!/usr/bin/env python
# -*- coding:utf-8 -*-

import platform
import os, sys
from multiprocessing import Process
import http.client
import subprocess
from helpers import tr


class ConsoleOut(object):
    def __init__(self, stream):
        self.stream = stream
        self.switch = True

    def write(self, data):
        if self.switch:
            self.stream.write(data)
            self.stream.flush()
        else:
            pass

    def off(self):
        self.switch = False

    def on(self):
        self.switch = True

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


def install(package):
    #pip.main(['install', package])
    output = subprocess.check_output(['pip', 'install'] + package)
    sys.stdout.write(output.decode('utf-8'))


def prompt_exit():
    input(tr('Press any key to exit ...', lang=lang))
    sys.exit(1)

if __name__ == '__main__':
    # устанавливаем язык выводимых сообщений
    while True:
        lang = input('Enter the language code [en|ru]: ')
        lang = lang.lower().strip()
        if lang == 'ru' or lang == 'en':
            break
        else:
            print('The language code is not found. Re-enter.')
            continue

    # проверям версию Python, всё из-за mod_wsgi и lxml
    # версия интерпритатора только 3.4.4
    OS = sys.platform
    sys.stdout = ConsoleOut(sys.stdout)
    if OS == 'win32':
        if not( sys.version_info.major == 3 and
        sys.version_info.minor == 4 and
        sys.version_info.micro == 4 ):
            print(tr('Further continuation impossible, Python version 3.4.4 is not equal.', lang=lang))
            prompt_exit()


    # Производим активацию virtualenv
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    PROJ_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    sys.path.append(PROJ_DIR)
    sys.path.append(os.path.join(PROJ_DIR, 'conf'))
    sys.path.append(os.path.join(BASE_DIR, 'Scripts'))

    if OS == 'win32':
        ACTIVATE_SCRIPT = os.path.join(BASE_DIR, 'Scripts', 'activate_this.py')
    elif  'linux' in OS:
        ACTIVATE_SCRIPT = os.path.join(BASE_DIR, 'bin', 'activate_this.py')
    else:
        print(tr('Installing Severcart are not available for the platform.', lang=lang))
        prompt_exit()
    activate_env=os.path.expanduser(ACTIVATE_SCRIPT)
    with open(activate_env) as f:
        code = compile(f.read(), activate_env, 'exec')
        exec(code, dict(__file__=activate_env))

    CPU_ARCH = platform.architecture()[0]
    print('-------------------------------------------------')
    print(tr('-------------Update packages---------', lang=lang))
    print('-------------------------------------------------')
    try:
        if CPU_ARCH == '64bit' and OS == 'win32':
            print(tr('Installation package dependencies for 64-bit Windows',lang=lang))
            packages_x64 = [
                ['Django==1.9.4'],
                [ os.path.join(PROJ_DIR, 'tkinstaller', 'Noarch', 'django-mptt-0.8.0.tar.gz') ],
                [ os.path.join(PROJ_DIR, 'tkinstaller', 'Win64', 'lxml-3.4.4-cp34-none-win_amd64.whl'), '--no-cache-dir'],
                [ os.path.join(PROJ_DIR, 'tkinstaller', 'Win64', 'Pillow-3.1.0-cp34-none-win_amd64.whl')],
                [ os.path.join(PROJ_DIR, 'tkinstaller', 'Win64', 'psycopg2-2.6.1-cp34-none-win_amd64.whl')],
                [os.path.join(PROJ_DIR, 'tkinstaller', 'Noarch', 'python-docx-0.8.5.tar.gz'), '--disable-pip-version-check'],
                ['reportlab'],
                ['pytz'],
            ]
            persent = 10
            for pack in packages_x64:
                sys.stdout.off()
                install(pack)
                sys.stdout.on()
                print(str(persent) + "%")
                persent += 10
            print("100%")
        
        elif CPU_ARCH == '32bit' and OS == 'win32':
            print(tr('Installation package dependencies for 32-bit Windows', lang=lang))
            packages_x86 = [
                ['Django==1.9.4'],
                [os.path.join(PROJ_DIR, 'tkinstaller', 'Noarch', 'django-mptt-0.8.0.tar.gz')],
                [os.path.join(PROJ_DIR, 'tkinstaller', 'Win32', 'lxml-3.4.4-cp34-none-win32.whl'), '--no-cache-dir'],
                [os.path.join(PROJ_DIR, 'tkinstaller', 'Win32', 'Pillow-3.1.0-cp34-none-win32.whl')],
                [os.path.join(PROJ_DIR, 'tkinstaller', 'Win32', 'psycopg2-2.6.1-cp34-none-win32.whl')],
                [os.path.join(PROJ_DIR, 'tkinstaller', 'Noarch', 'python-docx-0.8.5.tar.gz'), '--disable-pip-version-check'],
                ['reportlab'],
                ['pytz'],
            ]
            persent = 10
            for pack in packages_x86:
                sys.stdout.off()
                install(pack)
                sys.stdout.on()
                print(str(persent) + "%")
                persent += 10
            print("100%")
        elif 'linux' in OS:
            print(tr('Installation package dependencies for Linux', lang=lang))
            packages_unix = [
                ['Django==1.9'], 
                ['lxml==%s.%s.%s' % (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)],
                ['django-mptt'],
                ['psycopg2'],
                ['python-docx'],
                ['pillow==2.9.0'],
                ['reportlab'],
                ['pytz'],
            ]
            persent = 10
            for pack in packages_unix:
                sys.stdout.off()
                install(pack)
                sys.stdout.on()
                print(str(persent) + "%")
                persent += 10
            print("100%")
        else:
            print(tr('Support for this architecture is not implemented.', lang=lang))
            prompt_exit()
    except Exception as e:
        print(str(e))
        print(tr('Further continuation of the installation is not possible!',lang=lang))
        prompt_exit()
    else:
        # производим запуск миграции схемы Severcart и Django        
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')

        import django
        from django.core.management import execute_from_command_line

        django.setup()

        print('-------------------------------------------------')
        print(tr('--------------The migration scheme---------------', lang=lang))
        print('-------------------------------------------------')
        try:
            execute_from_command_line(['manage.py', 'makemigrations'])
            execute_from_command_line(['manage.py', 'migrate'])
        except Exception as e:
            print(str(e))
            prompt_exit()
        else:
            print(tr('The scheme was successfully migrated.', lang=lang))
        
        print('-------------------------------------------------')
        print(tr('------------Update successful--------------', lang=lang))
        print('-------------------------------------------------')
        sys.exit(0)
