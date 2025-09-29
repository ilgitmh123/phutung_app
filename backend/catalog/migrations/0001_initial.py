from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),('created_at', models.DateTimeField(auto_now_add=True)),('updated_at', models.DateTimeField(auto_now=True)),('name', models.CharField(max_length=120, unique=True)),('slug', models.SlugField(max_length=140, unique=True)),('is_active', models.BooleanField(default=True))],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),('created_at', models.DateTimeField(auto_now_add=True)),('updated_at', models.DateTimeField(auto_now=True)),('name', models.CharField(max_length=120)),('slug', models.SlugField(max_length=140)),('is_active', models.BooleanField(default=True)),('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='catalog.category'))],
            options={'unique_together': {('parent', 'slug')}},
        ),
        migrations.CreateModel(
            name='Product',
            fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),('created_at', models.DateTimeField(auto_now_add=True)),('updated_at', models.DateTimeField(auto_now=True)),('sku', models.CharField(max_length=64, unique=True)),('oem_code', models.CharField(blank=True, max_length=64)),('name', models.CharField(max_length=255)),('slug', models.SlugField(max_length=280, unique=True)),('description', models.TextField(blank=True)),('attributes', models.JSONField(blank=True, default=dict)),('specs', models.JSONField(blank=True, default=dict)),('retail_price', models.BigIntegerField(default=0)),('sale_price', models.BigIntegerField(blank=True, null=True)),('stock_on_hand', models.IntegerField(default=0)),('stock_reserved', models.IntegerField(default=0)),('reorder_point', models.IntegerField(default=0)),('status', models.CharField(default='ACTIVE', max_length=12)),('meta_title', models.CharField(blank=True, max_length=255)),('meta_description', models.CharField(blank=True, max_length=320)),('is_featured', models.BooleanField(default=False)),('brand', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='catalog.brand')),('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.category'))],
        ),
        migrations.CreateModel(
            name='VehicleModel',
            fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),('created_at', models.DateTimeField(auto_now_add=True)),('updated_at', models.DateTimeField(auto_now=True)),('name', models.CharField(max_length=120)),('year_from', models.IntegerField(blank=True, null=True)),('year_to', models.IntegerField(blank=True, null=True)),('engine_cc', models.IntegerField(blank=True, null=True)),('notes', models.CharField(blank=True, max_length=255)),('brand', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='catalog.brand'))],
            options={'unique_together': {('brand', 'name', 'year_from', 'year_to')}},
        ),
    ]
