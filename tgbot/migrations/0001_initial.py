# Generated by Django 3.2.13 on 2022-05-21 13:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Название города')),
            ],
        ),
        migrations.CreateModel(
            name='Courier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.PositiveBigIntegerField(unique=True, verbose_name='Telegram id курьера')),
            ],
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('district_name', models.CharField(max_length=255, verbose_name='Название района')),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tgbot.city', verbose_name='Город в котором находится район')),
            ],
        ),
        migrations.CreateModel(
            name='Fasovka',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grams', models.FloatField(unique=True, verbose_name='Фасовка в граммах')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Название товара')),
                ('is_available', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Zakladka',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
                ('is_taken', models.BooleanField(default=False, verbose_name='Заказано')),
                ('latitude', models.FloatField(verbose_name='Широта')),
                ('longitude', models.FloatField(verbose_name='Долгота')),
                ('description', models.TextField(verbose_name='Описание')),
                ('image', models.ImageField(upload_to='images', verbose_name='Изображение')),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tgbot.city', verbose_name='Город')),
                ('courier', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tgbot.courier', verbose_name='Курьер')),
                ('district', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tgbot.district', verbose_name='Район')),
                ('fasovka', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tgbot.fasovka', verbose_name='Фасовка')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tgbot.product', verbose_name='Название товара')),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
                ('user_id', models.PositiveBigIntegerField()),
                ('username', models.CharField(blank=True, max_length=32, null=True)),
                ('first_name', models.CharField(max_length=256)),
                ('last_name', models.CharField(blank=True, max_length=256, null=True)),
                ('language_code', models.CharField(blank=True, help_text="Telegram client's lang", max_length=8, null=True)),
                ('deep_link', models.CharField(blank=True, max_length=64, null=True)),
                ('is_blocked_bot', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('balance', models.FloatField(default=0.0)),
                ('btc_address', models.CharField(max_length=34, verbose_name='Дочерний BTC адрес')),
                ('wif', models.CharField(max_length=255, verbose_name='Wallet import format')),
                ('city', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tgbot.city', verbose_name='Город')),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Support',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
                ('text', models.TextField()),
                ('is_solved', models.BooleanField(default=False, verbose_name='Проблема решена')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tgbot.user', verbose_name='Репортер')),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductToFasovka',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField(blank=True, null=True, verbose_name='Цена в рублях')),
                ('fasovka', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tgbot.fasovka', verbose_name='Фасовка')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tgbot.product', verbose_name='Товар')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='related_fasovka',
            field=models.ManyToManyField(blank=True, default=None, related_name='related_products', through='tgbot.ProductToFasovka', to='tgbot.Fasovka', verbose_name='Доступные фасовки'),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
                ('price', models.FloatField(verbose_name='Цена')),
                ('is_paid', models.BooleanField(default=False, verbose_name='Оплата прошла')),
                ('city', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tgbot.city', verbose_name='Город')),
                ('district', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tgbot.district', verbose_name='Район')),
                ('fasovka', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tgbot.fasovka', verbose_name='Фасовка')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tgbot.product', verbose_name='Товар')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tgbot.user', verbose_name='Клиент')),
                ('zakladka', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tgbot.zakladka', verbose_name='Закладка')),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
        ),
    ]
