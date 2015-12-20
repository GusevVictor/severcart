from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from index.models import OrganizationUnits

class AnconUser(AbstractBaseUser):
    """
    Custom user class.
    Details: http://blackglasses.me/2013/09/17/custom-django-user-model/
    """
    username = models.CharField('Логин', unique=True, db_index=True, max_length=64)
    departament = models.ForeignKey(OrganizationUnits, blank=True, null=True, verbose_name='Организация')
    joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    fio = models.CharField('Фамилие Имя Отчество', max_length=256, blank=True, null=True)
    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username
