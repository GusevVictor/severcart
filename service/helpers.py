# -*- coding:utf-8 -*-

from service.models import Settings

class SevercartConfigs(object):
    """Вспомогательный класс для хранения настроечных параметров в СУБД.
    """
    def __init__(self):        
        try:
            self.m1 = Settings.objects.get(pk=1)
        except Settings.DoesNotExist:
            self.smtp_server    = ''
            self.smtp_port      = ''
            self.email_sender   = ''
            self.smtp_login     = ''
            self.smtp_password  = ''
            self.use_ssl        = ''
        else:
            # если таблица уже содержит данные, то инициализируем внутренние переменные
            self.smtp_server    = self.m1.smtp_server
            self.smtp_port      = self.m1.smtp_port
            self.email_sender   = self.m1.email_sender
            self.smtp_login     = self.m1.smtp_login
            self.smtp_password  = self.m1.smtp_password
            self.use_ssl        = self.m1.use_ssl

    def commit(self):
        """Сохранение значений настроечных переменных в СУБД.
        """
        self.m1 = Settings.objects.all()
        if self.m1:
            # если данные уже есть, то перезаписываем
            self.m1 = Settings.objects.get(pk=1)
            self.m1.smtp_server    = self.smtp_server
            self.m1.smtp_port      = self.smtp_port 
            self.m1.email_sender   = self.email_sender
            self.m1.smtp_login     = self.smtp_login
            self.m1.smtp_password  = self.smtp_password
            self.m1.use_ssl        = self.use_ssl
            self.m1.save()
        else:
            # если в таблица пустая, то создаём первую строку           
            Settings.objects.create(
                            smtp_server    = self.smtp_server,
                            smtp_port      = self.smtp_port,
                            email_sender   = self.email_sender,
                            smtp_login     = self.smtp_login,
                            smtp_password  = self.smtp_password,
                            use_ssl        = self.use_ssl
                            )
