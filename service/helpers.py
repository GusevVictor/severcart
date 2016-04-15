# -*- coding:utf-8 -*-

from service.models import Settings
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail import send_mail


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
            self.use_tls        = ''
            self.page_format    = 'A4'
        else:
            # если таблица уже содержит данные, то инициализируем внутренние переменные
            self.smtp_server    = self.m1.smtp_server
            self.smtp_port      = self.m1.smtp_port
            self.email_sender   = self.m1.email_sender
            self.smtp_login     = self.m1.smtp_login
            self.smtp_password  = self.m1.smtp_password
            self.use_ssl        = self.m1.use_ssl
            self.use_tls        = self.m1.use_tls
            self.page_format    = self.m1.page_format

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
            self.m1.use_tls        = self.use_tls
            self.m1.page_format    = self.page_format
            self.m1.save()
        else:
            # если в таблица пустая, то создаём первую строку           
            Settings.objects.create(
                            smtp_server    = self.smtp_server,
                            smtp_port      = self.smtp_port,
                            email_sender   = self.email_sender,
                            smtp_login     = self.smtp_login,
                            smtp_password  = self.smtp_password,
                            use_ssl        = self.use_ssl,
                            use_tls        = self.use_tls,
                            page_format    = self.page_format
                            )

def send_email(reciver=None, title=None, text=None):
    """Своя обёртка вокруг django send_email.
    """
    mconf         = SevercartConfigs()
    subject       = text.strip()
    message       = text.strip()
    from_email    = mconf.email_sender
    to_email      = reciver
    auth_user     = mconf.smtp_login
    auth_password = mconf.smtp_password

    connection = EmailBackend(
                    host = mconf.smtp_server,
                    port = mconf.smtp_port,
                    username=mconf.smtp_login,
                    password=mconf.smtp_password,
                    use_tls=mconf.use_tls,
                    use_ssl=mconf.use_ssl,
                    timeout=60
                )
    send_mail(title, text, from_email, [reciver], connection=connection)
    return None
