# Generated by Django 3.2.13 on 2022-05-22 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0011_auto_20220522_2128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='klad_type',
            field=models.CharField(choices=[('Снежный прикоп', 'Снежный прикоп'), ('Магнит', 'Магнит'), ('Тайник', 'Тайник'), ('Прикоп', 'Прикоп'), ('Другой', 'Другой')], default='Магнит', max_length=16, verbose_name='Тип клада'),
        ),
        migrations.AlterField(
            model_name='tempzakladkaforcourier',
            name='klad_type',
            field=models.CharField(blank=True, choices=[('Снежный прикоп', 'Снежный прикоп'), ('Магнит', 'Магнит'), ('Тайник', 'Тайник'), ('Прикоп', 'Прикоп'), ('Другой', 'Другой')], default='Магнит', max_length=16, null=True, verbose_name='Тип клада'),
        ),
        migrations.AlterField(
            model_name='zakladka',
            name='klad_type',
            field=models.CharField(choices=[('Снежный прикоп', 'Снежный прикоп'), ('Магнит', 'Магнит'), ('Тайник', 'Тайник'), ('Прикоп', 'Прикоп'), ('Другой', 'Другой')], default='Магнит', max_length=16, verbose_name='Тип клада'),
        ),
    ]