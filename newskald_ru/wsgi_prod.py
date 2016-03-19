import os, sys, site

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SEVERCART_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#site.addsitedir('C:/venv/Lib/site-packages/')

site.addsitedir(os.path.join(BASE_DIR, 'Lib', 'site-packages'))

#BASE_DIR = C:/venv/
# Add the app's directory to the PYTHONPATH
#sys.path.append('C:/venv/Severcart/newskald_ru/')
#sys.path.append('C:/venv/Severcart/')
#sys.path.append('C:/venv/Scripts/')

sys.path.append(SEVERCART_DIR)
sys.path.append(os.path.join(SEVERCART_DIR, 'newskald_ru'))
sys.path.append(os.path.join(BASE_DIR, 'Scripts'))

# Activate your virtual env
activate_env=os.path.expanduser(os.path.join(BASE_DIR, 'Scripts', 'activate_this.py'))

with open(activate_env) as f:
    code = compile(f.read(), activate_env, 'exec')
    exec(code, dict(__file__=activate_env))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newskald_ru.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
