from django.db import models
from index.models import OrganizationUnits

class Events(models.Model):
    """Список событий, использется для генерации различных отчётов.
    """

    ETYPE_CHOICES = (
        ('AD', 'Добавление нового расходника'),
        ('TR', 'Передача расходника в пользование'),
        ('TF', 'Передача расходника на заправку'),
        ('RS', 'Возврат восстановленного картриджа на склад'),
        ('TB', 'Перемещение в корзину'),
        ('DC', 'Списание расходника'),
        ('TS', 'Передача пустого расходника на склад'),
        ('CU', 'Создание нового пользователя'),
        ('DU', 'Удаление пользователя'),
    )
    # устанавливаем слабую связанность для объектов
    date_time   = models.DateTimeField()
    cart_number = models.IntegerField(db_index=True)
    cart_type   = models.CharField(max_length=256, null=True)
    cart_action = models.IntegerField(null=True)
    # cart_action хранит данные о восстановительных действиях с объектом 5 значном числе.
    # 1 в 5 разряде - заправка и очитска
    # 1 в 4 разряде - замена фотовала
    # 1 в 3 разряде - замена ракеля
    # 1 в 2 разряде - замена чипа
    # 1 в 1 разряде - замена магнитного вала
    # если действий не производилось, то в соответствующем разряде ставится 0
    event_type  = models.CharField(choices=ETYPE_CHOICES, max_length=32)
    event_user  = models.CharField(max_length=64)
    event_org   = models.CharField(max_length=256, null=True)
    event_firm  = models.CharField(max_length=256, null=True)
    departament = models.IntegerField()


