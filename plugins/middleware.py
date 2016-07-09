# -*- coding:utf-8 -*-

from django.utils import translation

class ChangeUserLang(object):
    """
    """

    def process_request(self, request):
        # lang_code принимает значения либо ru, либо en
        lang_code = request.session.get('lang_code', 0)
        if lang_code:
            translation.activate(lang_code)   
            request.LANGUAGE_CODE = translation.get_language()
        
        # иначе оставляем всё как есть
