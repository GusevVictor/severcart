# -*- coding:utf-8  -*-

from django.db import models

class Settings(models.Model):
    
    # настройка подключения к серверу электронной почты
    smtp_server   = models.CharField(max_length=256, null=True)
    smtp_port     = models.IntegerField(db_index=True, null=True)
    email_sender  = models.EmailField(max_length=254, null=True, blank=True)
    smtp_login    = models.CharField(max_length=256, null=True)
    smtp_password = models.CharField(max_length=256, null=True)
    use_ssl       = models.BooleanField(default=False)
    use_tls       = models.BooleanField(default=False)

    # настройки формата печатаемых наклеек
    # принимает значения A4, A5, ...
    page_format    =  models.CharField(max_length=2, null=True, default='A4')
    print_bar_code = models.BooleanField(default=False)
    print_name_obj = models.BooleanField(default=True)
    print_name_ou  = models.BooleanField(default=True)
