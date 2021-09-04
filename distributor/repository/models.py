from django.db import models

from dealership.models import Dealership


class Repository(models.Model):
    product_id = models.CharField(max_length=20, primary_key=True, editable=False)
    product_name = models.CharField(max_length=100)
    product_price = models.IntegerField()
    product_quantity = models.IntegerField(default=1)

    def __str__(self):
        return self.product_name


class Exportation(models.Model):
    exportation_date = models.DateTimeField(auto_now_add=True)
    total = models.IntegerField(default=0)
    payed = models.IntegerField(default=0)
    debt = models.IntegerField(default=0)
    dealership = models.ForeignKey(Dealership, on_delete=models.CASCADE)


class ExportationDetail(models.Model):
    exportation = models.ForeignKey(Exportation, on_delete=models.CASCADE)
    product = models.ForeignKey(Repository, on_delete=models.CASCADE)
    product_price = models.IntegerField(default=0)
    product_quantity = models.IntegerField(default=1)
    total_price = models.IntegerField(default=0)
