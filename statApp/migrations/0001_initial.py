# Generated by Django 4.0.1 on 2022-01-23 21:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CityList',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID'
                    )
                ),
                ('city',
                 models.CharField(
                     max_length=30,
                     verbose_name='Название города'
                 )
                 ),
            ],
        ),
        migrations.CreateModel(
            name='OneDayData',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')
                 ),
                ('date', models.DateField()),
                ('maxTemp', models.SmallIntegerField()),
                ('minTemp', models.SmallIntegerField()),
                ('avgTemp', models.SmallIntegerField()),
                ('windSpeed', models.SmallIntegerField()),
                ('windDir', models.CharField(max_length=3)),
                ('precipitation',
                 models.DecimalField(
                     decimal_places=1,
                     max_digits=4
                 )
                 ),
                ('desc', models.CharField(max_length=40)),
                ('city', models.ForeignKey(
                    blank=True,
                    default=None,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    to='statApp.citylist'
                )
                 ),
            ],
        ),
    ]
