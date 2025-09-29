from django.db import models
from django.utils.text import slugify

class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: abstract = True

class Brand(TimeStamped):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    is_active = models.BooleanField(default=True)
    def save(self,*a,**kw):
        if not self.slug: self.slug = slugify(self.name)
        super().save(*a,**kw)
    def __str__(self): return self.name

class Category(TimeStamped):
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140)
    is_active = models.BooleanField(default=True)
    class Meta: unique_together = ("parent","slug")
    def save(self,*a,**kw):
        if not self.slug: self.slug = slugify(self.name)
        super().save(*a,**kw)
    def __str__(self): return self.name

class VehicleModel(TimeStamped):
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    name = models.CharField(max_length=120)
    year_from = models.IntegerField(null=True, blank=True)
    year_to = models.IntegerField(null=True, blank=True)
    engine_cc = models.IntegerField(null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    class Meta: unique_together = ("brand","name","year_from","year_to")
    def __str__(self): return f"{self.brand.name} {self.name}"

class Product(TimeStamped):
    oem_code = models.CharField(max_length=64, unique=True, db_index=True)  # mã OEM, unique
    sku = models.CharField(max_length=64, blank=True)  # tuỳ chọn, không unique

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True)

    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    description = models.TextField(blank=True)
    attributes = models.JSONField(default=dict, blank=True)
    specs = models.JSONField(default=dict, blank=True)

    retail_price = models.BigIntegerField(default=0)
    sale_price = models.BigIntegerField(null=True, blank=True)

    stock_on_hand = models.IntegerField(default=0)
    stock_reserved = models.IntegerField(default=0)
    reorder_point = models.IntegerField(default=0)
    status = models.CharField(max_length=12, default="ACTIVE")

    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.CharField(max_length=320, blank=True)
    is_featured = models.BooleanField(default=False)

    def save(self, *a, **kw):
        if not self.slug:
            self.slug = slugify(f"{self.oem_code}-{self.name}")
        super().save(*a, **kw)

    def __str__(self):
        return f"{self.oem_code} | {self.name}"
