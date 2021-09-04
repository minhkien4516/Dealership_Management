from django.db import models


class ImportationRequest(models.Model):
    importation_date = models.DateTimeField(auto_now_add=True)
    total = models.IntegerField(default=0)


class ImportationDetailRequest(models.Model):
    importation_request = models.ForeignKey(ImportationRequest, on_delete=models.CASCADE)
    product_id = models.CharField(max_length=14)
    product_name = models.CharField(max_length=100)
    product_price = models.IntegerField()
    product_quantity = models.IntegerField(default=1)
    total_price = models.IntegerField()


class Importation(models.Model):
    importation_date = models.DateTimeField(auto_now_add=True)
    total = models.IntegerField(default=0)
    payed = models.IntegerField(default=0)
    debt = models.IntegerField(default=0)


class ImportationDetail(models.Model):
    importation = models.ForeignKey(Importation, on_delete=models.CASCADE)
    product_id = models.CharField(max_length=14)
    product_name = models.CharField(max_length=100)
    product_price = models.IntegerField()
    product_quantity = models.IntegerField(default=1)
    total_price = models.IntegerField()

