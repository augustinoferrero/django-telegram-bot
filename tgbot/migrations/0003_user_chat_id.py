# Generated by Django 3.2.13 on 2022-05-21 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0002_user_transactions'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='chat_id',
            field=models.IntegerField(default=354657, verbose_name='id чата'),
            preserve_default=False,
        ),
    ]
