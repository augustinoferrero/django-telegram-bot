# Generated by Django 3.2.13 on 2022-05-22 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0013_auto_20220522_2143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='price',
            field=models.FloatField(blank=True, null=True, verbose_name='Цена'),
        ),
    ]
