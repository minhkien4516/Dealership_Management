from django.db import models


class City(models.Model):
    id = models.CharField(primary_key=True, max_length=4, editable=False)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class District(models.Model):
    id = models.CharField(primary_key=True, editable=False, max_length=3)
    name = models.CharField(max_length=50)
    city = models.ForeignKey(City, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.name


class DealershipType(models.Model):
    id = models.CharField(primary_key=True, max_length=2, editable=None)
    name = models.CharField(max_length=10)
    maximum_number_of_dealerships = models.IntegerField()
    maximum_debt = models.IntegerField(default=0)
    discount_rate = models.FloatField(default=0.0)

    def __str__(self):
        return self.name


class Owner(models.Model):
    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)
    email = models.CharField(max_length=320)

    def __str__(self):
        return self.name


class Dealership(models.Model):
    id = models.CharField(primary_key=True, editable=False, max_length=9)
    name = models.CharField(max_length=100)
    type = models.ForeignKey(DealershipType, max_length=2, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, default=None)
    address = models.CharField(max_length=200)
    registration_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    debt = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    # Customizing id
    def save(self, *args, **kwargs):
        if self.type.id == 'DQ':
            max_number_of_dealerships = self.type.maximum_number_of_dealerships
        else:
            max_number_of_dealerships = self.type.maximum_number_of_dealerships

        for i in range(1, max_number_of_dealerships + 1):
            available_dealership_id = Dealership.objects.filter(
                id=f'{self.city.id}{self.district.id}{self.type.id}{i}'
            ).count()
            if available_dealership_id == 0:
                self.id = f'{self.city.id}{self.district.id}{self.type.id}{i}'
                break
        super(Dealership, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
