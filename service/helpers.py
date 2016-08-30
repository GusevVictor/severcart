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
        except:
            self.smtp_server    = ''
            self.smtp_port      = 0
            self.email_sender   = ''
            self.smtp_login     = ''
            self.smtp_password  = ''
            self.use_ssl        = False
            self.use_tls        = False
            self.page_format    = 'A4'
            self.print_bar_code = False
            self.print_name_obj = True
            self.print_name_ou  = True
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
            self.print_bar_code = self.m1.print_bar_code
            self.print_name_obj = self.m1.print_name_obj
            self.print_name_ou  = self.m1.print_name_ou

    def commit(self):
        """Сохранение значений настроечных переменных в СУБД.
        """
        try:
            self.m1 = Settings.objects.get(pk=1)
        except:
            # если в таблица пустая, то создаём первую строку           
            m1 = Settings(
                            smtp_server    = self.smtp_server,
                            smtp_port      = self.smtp_port,
                            email_sender   = self.email_sender,
                            smtp_login     = self.smtp_login,
                            smtp_password  = self.smtp_password,
                            use_ssl        = self.use_ssl,
                            use_tls        = self.use_tls,
                            page_format    = self.page_format,
                            print_bar_code = self.print_bar_code,
                            print_name_obj = self.print_name_obj,
                            print_name_ou  = self.print_name_ou
                            )
            m1.save()
        else:
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
            self.m1.print_bar_code = self.print_bar_code
            self.m1.print_name_obj = self.print_name_obj
            self.m1.print_name_ou  = self.print_name_ou
            self.m1.save()

def send_email(reciver=None, title=None, text=None):
    """Своя обёртка вокруг django send_email.
    """
    mconf         = SevercartConfigs()
    subject       = title.strip()
    message       = text.strip()
    from_email    = mconf.email_sender

    connection = EmailBackend(
                    host = mconf.smtp_server,
                    port = mconf.smtp_port,
                    username=mconf.smtp_login,
                    password=mconf.smtp_password,
                    use_tls=mconf.use_tls,
                    use_ssl=mconf.use_ssl,
                    timeout=60
                )
    send_mail(subject, message, from_email, [reciver], connection=connection)
    return None
