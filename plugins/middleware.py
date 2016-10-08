# -*- coding:utf-8 -*-

import datetime
from django.utils import translation
from django.conf import settings

from service.helpers import SevercartConfigs


class InsertVarToRequest(object):
    """Встраивание переменных в объект request
    """

    def process_request(self, request):
        # lang_code принимает значения либо ru, либо en
        lang_code = request.session.get('lang_code', 0)
        if lang_code:
            translation.activate(lang_code)
            request.LANGUAGE_CODE = translation.get_language()
        # иначе оставляем всё как есть

        request.HOME_SITE    = settings.HOME_SITE
        request.VERSION      = settings.VERSION
        request.YEAR         = datetime.date.today().year
        # оиспользуется для обновления браузерного кэша статических 
        # файлов при выпуске нового релиза
        request.CACHEVERSION = settings.VERSION.replace('.', '')
        # длина номера РМ после которого будет производиться усечение
        request.TRLEN        = settings.TRLEN

        # отключаем показ копирайтов
        request.SHOW_COPYRIGHT = settings.SHOW_COPYRIGHT
        conf = SevercartConfigs()
        request.TZ = conf.time_zone
        request.SHOW_TIME = conf.show_time