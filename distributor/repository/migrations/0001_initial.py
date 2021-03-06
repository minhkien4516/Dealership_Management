# Generated by Django 3.1.4 on 2020-12-03 04:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dealership', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Exportation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exportation_date', models.DateTimeField(auto_now_add=True)),
                ('total', models.IntegerField(default=0)),
                ('payed', models.IntegerField(default=0)),
                ('debt', models.IntegerField(default=0)),
                ('dealership', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dealership.dealership')),
            ],
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('product_id', models.CharField(editable=False, max_length=20, primary_key=True, serialize=False)),
                ('product_name', models.CharField(max_length=100)),
                ('product_price', models.IntegerField()),
                ('product_quantity', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='ExportationDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_price', models.IntegerField(default=0)),
                ('product_quantity', models.IntegerField(default=1)),
                ('total_price', models.IntegerField(default=0)),
                ('exportation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repository.exportation')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repository.repository')),
            ],
        ),
    ]
