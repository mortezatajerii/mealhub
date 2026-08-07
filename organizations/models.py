from django.db import models


class Organization(models.Model):
    name = models.CharField("نام شرکت", max_length=255)

    class Meta:
        verbose_name = "شرکت"
        verbose_name_plural = "شرکت‌ها"

    def __str__(self):
        return self.name


class Department(models.Model):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="departments"
    )
    name = models.CharField("نام واحد", max_length=255)

    class Meta:
        verbose_name = "واحد"
        verbose_name_plural = "واحدها"

    def __str__(self):
        return self.name
