from django.db import models
from index.models import FirmTonerRefill, OrganizationUnits
    
class SCDoc(models.Model):
    """Документы - договора на поставку, заправку/обслуживание, акты списания, акты передачи
    """
    DOC_TYPE = (
        (1, 'Договор поставки'),
        (2, 'Договор обслуживания'),
        (3, 'Акт передачи'),
        (4, 'Акт списания'),
    )
    number      = models.CharField(db_index=True, max_length=256)
    date        = models.DateField(db_index=True)
    firm        = models.ForeignKey(FirmTonerRefill, null=True)
    title       = models.CharField(max_length=256)
    short_cont  = models.TextField(null=True)
    money       = models.IntegerField(db_index=True, null=True)
    departament = models.ForeignKey(OrganizationUnits)
    doc_type    = models.IntegerField(choices=DOC_TYPE, default=1)
    user        = models.CharField(max_length=256, null=True)

    def __str__(self):
        return ('%s %s') % (self.number, self.title,)
