from django.db import models

class Events(models.Model):
    """Список событий, использется для статистики и на морде сайта
    """
    ETYPE_CHOICES = (
        (1, 'Добавление нового расходника'),
        (2, 'Передача расходника в пользование'),
        (3, 'Передача расходники на заправку'),
        (4, 'Утилизация'),
        (5, 'Передача пустого расходника на склад'),
        (6, 'Создание нового пользователя'),
        (7, 'Удаление пользователя'),
    )
    cart_id = models.IntegerField() # устанавливаем слабую связанность для объекта
    date_time = models.DateTimeField()
    event_type = models.IntegerField(choices=ETYPE_CHOICES, null=True)
    text = models.CharField(max_length=256)
