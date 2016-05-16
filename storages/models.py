from django.db import models
from index.models import OrganizationUnits

class Storages(models.Model):
    title       = models.CharField(max_length=256)
    description = models.TextField(null=True)
    departament = models.ForeignKey(OrganizationUnits, on_delete=models.PROTECT)
    address     = models.CharField(max_length=512)
    default     = models.BooleanField(default=False)

    def __str__(self):
        return self.title