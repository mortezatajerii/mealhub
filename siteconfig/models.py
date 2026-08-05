from django.db import models
from django.core.validators import (
    FileExtensionValidator,
)


class SiteSettings(models.Model):
    site_title = models.CharField(
        max_length=255, default="مرتضی تاجری | توسعه دهنده Backend با Django و Python"
    )
    meta_description = models.TextField(blank=True)
    favicon = models.ImageField(upload_to="site/", blank=True, null=True)
    logo_header = models.ImageField(upload_to="site/", blank=True, null=True)
    logo_footer = models.ImageField(upload_to="site/", blank=True, null=True)

    footer_copyright = models.CharField(
        max_length=255, default="© 1403 - تمامی حقوق محفوظ است."
    )


    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"


class MenuItem(models.Model):
    title = models.CharField(max_length=100, verbose_name="Menu Title")
    url = models.CharField(max_length=255, verbose_name="(URL/Anchor)")
    order = models.PositiveIntegerField(default=0, verbose_name="Order")
    is_active = models.BooleanField(default=True, verbose_name="Active")

    show_in_desktop = models.BooleanField(default=True, verbose_name="Show on Desktop")
    show_in_mobile = models.BooleanField(default=True, verbose_name="Show on Mobile")

    class Meta:
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"
        ordering = ["order"]

    def __str__(self):
        return self.title
