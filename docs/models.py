# -*- coding:utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from index.models import FirmTonerRefill, OrganizationUnits
    
class SCDoc(models.Model):
    """Документы - договора на поставку, заправку/обслуживание, акты списания, акты передачи
    """
    DOC_TYPE = (
        (1, _('Delivery agreement')),
        (2, _('Service agreement')),
        (3, _('Deed of conveyance')),
        (4, _('Act of write-off')),
    )
    number           = models.CharField(db_index=True, max_length=256)
    date_of_signing  = models.DateField(db_index=True, null=True, blank=True) # дата договора
    date_created     = models.DateField(db_index=True, null=True) # дата добавления договора в СУБД
    firm             = models.ForeignKey(FirmTonerRefill, null=True)
    title            = models.CharField(max_length=256)
    short_cont       = models.TextField(null=True)
    money            = models.IntegerField(db_index=True, null=True)
    spent            = models.IntegerField(db_index=True, null=True)
    departament      = models.ForeignKey(OrganizationUnits)
    doc_type         = models.IntegerField(choices=DOC_TYPE)
    user             = models.CharField(max_length=256, null=True)

    def __str__(self):
        return ('%s %s') % (self.number, self.title,)
