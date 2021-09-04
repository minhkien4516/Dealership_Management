from django.db import models

from dealership.models import City, DealershipType, District, Dealership


class DealershipRegistrationQueue(models.Model):
    name = models.CharField(max_length=100)
    type = models.ForeignKey(DealershipType, max_length=2, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, default=None)
    address = models.CharField(max_length=200)
    registration_date = models.DateTimeField(auto_now_add=True)
    owner_name = models.CharField(max_length=200)
    owner = models.IntegerField()
    owner_phone = models.CharField(max_length=15)
    owner_email = models.CharField(max_length=320)
    is_done = models.BooleanField(default=False)
    status = models.CharField(max_length=100, default='Đang chờ duyệt')


class DealershipCancellationQueue(models.Model):
    dealership = models.ForeignKey(Dealership, on_delete=models.CASCADE)
    message = models.TextField(default="")
    status = models.CharField(max_length=200, default='Đang chờ duyệt')
    is_done = models.BooleanField(default=False)

