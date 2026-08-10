from django.db import models


class FoodItem(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return self.name


class DailyMenu(models.Model):
    date = models.DateField(unique=True)
    items = models.ManyToManyField(FoodItem, related_name="menus")

    def __str__(self):
        return str(self.date)
