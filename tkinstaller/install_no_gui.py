#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, sys



def prompt_exit():
    input('Press any key to exit ...')
    sys.exit(1)

if __name__ == '__main__':
    # Производим активацию virtualenv
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    PROJ_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    sys.path.append(PROJ_DIR)
    sys.path.append(os.path.join(PROJ_DIR, 'conf'))
    sys.path.append(os.path.join(BASE_DIR, 'bin'))


    ACTIVATE_SCRIPT = os.path.join(BASE_DIR, 'bin', 'activate_this.py')
    activate_env=os.path.expanduser(ACTIVATE_SCRIPT)
    with open(activate_env) as f:
        code = compile(f.read(), activate_env, 'exec')
        exec(code, dict(__file__=activate_env))    

    from django.utils.crypto import get_random_string
    import json
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    secret_key = get_random_string(50, chars)
    SECRETS = dict()
    SECRETS['secret_key'] = secret_key
    with open(os.path.join(PROJ_DIR, 'conf', 'secrets.json'), 'w') as j:
        json.dump(SECRETS, j)
    # производим запуск миграции схемы Severcart и Django        
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')

    import django
    from django.core.management import execute_from_command_line

    django.setup()

    try:
        execute_from_command_line(['manage.py', 'makemigrations'])
        execute_from_command_line(['manage.py', 'migrate'])
    except Exception as e:
        print(str(e))
        prompt_exit()
    else:
        print('The scheme was successfully migrated.')
    
    # создаём суперпользователя admin
    from accounts.models import AnconUser
    user = AnconUser(username='admin', is_admin = True)
    user.set_password('admin')
    user.save()
    print('The user was created successfully.')    
    print('------------Installation successful--------------')
    sys.exit(0)
