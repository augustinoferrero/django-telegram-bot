import os

import qrcode
from mnemonic import Mnemonic
import bip32utils

from tgbot.handlers.onboarding.manage_data import START, FASOFKA, READY, DISTRICT, CHOSEN_PRODUCT_NAME, CHOSEN_DISTRICT, \
    KLAD_TYPE, DISTRICTC, FASOFKAC, CONFIRM_ZK, CITIESC, READYC, KLAD_TYPEC, CHOSEN_ORDER
from tgbot.handlers.onboarding.static_text import welcome_message, order_description, buyed_order_text, account_text, \
    welcome_message_courier, couries_stat_text, zakladka_created
import requests
from tgbot.models import *
from tgbot.handlers.onboarding.keyboards import make_keyboard_for_start_command,  \
    make_keyboard_for_account_command, make_keyboard_for_not_available, make_keyboard_for_available, \
    make_keyboard_for_bye_or_decline, make_keyboard_for_fasofka, make_keyboard_for_districts, \
    make_keyboard_for_klad_type, make_keyboard_for_districts_c, make_keyboard_for_curier_menu, \
    make_keyboard_for_c_products, make_keyboard_for_fasofka_c, make_keyboard_for_klad_type_c, \
    make_keyboard_for_confirm_zk, klad_types


def command_start(update: Update, context: CallbackContext) -> None:
    if update.message is not None:
        chat_id = update.message.chat.id
    elif update.callback_query is not None:
        chat_id = update.callback_query.message.chat.id
    else:
        chat_id = None
    u, _ = User.get_user_and_created(update, context, chat_id)
    if _is_user_courier(u):
        update.message.reply_text(text=welcome_message_courier,
                                  reply_markup=make_keyboard_for_curier_menu())
    else:
        u.btc_address, u.wif = _create_btc_address(u.id)
        u.save()
        update.message.reply_text(text=welcome_message,
                                  reply_markup=make_keyboard_for_start_command())


def _create_btc_address(index):
    mnemon = Mnemonic('english')
    seed = mnemon.to_seed(
        bytes(os.getenv("SEED_PHRASE"), encoding="ascii"))
    print(f'BIP39 Seed: {seed.hex()}\n')

    root_key = bip32utils.BIP32Key.fromEntropy(seed)
    child_key = root_key.ChildKey(0).ChildKey(index)
    child_address = child_key.Address()
    child_private_wif = child_key.WalletImportFormat()

    return child_address, child_private_wif


def city_decision_handler(update: Update, context: CallbackContext):
    u = User.get_user(update, context)
    if not _is_user_courier(u):
        broadcast_decision = update.callback_query.data
        u.city = City.objects.get(name=broadcast_decision.replace(START, ""))
        u.save()
        message_city = broadcast_decision.replace(START, "")
        context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=f"Вы выбрали город: {message_city}",
            )

        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text="Воспользуйтесь меню слева для покупки и других действий",
        )
    else:
        broadcast_decision = update.callback_query.data
        courier = Courier.objects.get(telegram_id=u.user_id)
        courier.city = City.objects.get(name=broadcast_decision.replace(START, ""))
        courier.save()
        message_city = broadcast_decision.replace(START, "")
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=f"Ты выбрал город: {message_city}",
        )

        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text="Теперь ты можешь добавлять клады",
        )


def command_account(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update,context)
    if not _is_user_courier(u):
        orders = Order.objects.filter(user=u, is_paid=True).count()
        update.message.reply_text(text=account_text.format(city=u.city, balance=u.balance, orders=orders),
                                  reply_markup=make_keyboard_for_account_command())


def make_up_balance(update: Update, context: CallbackContext):
    u = User.get_user(update, context)
    if not _is_user_courier(u):
        img = qrcode.make(u.btc_address)
        img.save(f"./qrs/qr_{u.id}.jpg")
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=f"Ваш адрес для пополнения: {u.btc_address}\nВаш баланс до пополнения: {u.balance}\nВы также можете оплатить используя QR код ниже",
        )
        context.bot.send_photo(
            chat_id=update.callback_query.message.chat_id,
            photo=open(f"./qrs/qr_{u.id}.jpg", 'rb')
        )
        os.remove(f"./qrs/qr_{u.id}.jpg")
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text="Платеж может обрабатываться до 30-40 минут. Как только платеж придет - вы получите сообщение от бота. В случае если баланс не пополнится в течении часа, пожалуйста, обратитесь в поддержку и укажите кошелек, с которого вы отправляли BTC."
        )


def command_support(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(text="Напишите ваше обращение к службе поддержки ниже. Начните обращение со слова HELP, иначе оно не будет рассмотрено")


def receive_support_message(update: Update, context: CallbackContext):
    text = update.message.text
    Support.objects.create(user=User.get_user(context=context, update=update), text=text)
    update.message.reply_text(
        text="Ваше сообщение принято в обработку, мы свяжемся с вами в личные сообщения телеграм",
    )


def command_city_change(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(text="Выберите город",
                              reply_markup=make_keyboard_for_start_command())


def command_product_ready(update: Update, context: CallbackContext) -> None:
    user = User.get_user(update, context)
    if not _is_user_courier(user):
        if not Zakladka.objects.filter(city=user.city, is_taken=False):
            update.message.reply_text(text='Увы у нас нет доступных товаров на данный моментв этом городе')
        else:
            update.message.reply_text(text="Выберите товар",
                                      reply_markup=make_keyboard_for_available(user))


def product_chosen_handler_district(update: Update, context: CallbackContext):
    # записали товар в ордер
    user = User.get_user(update, context)
    if not _is_user_courier(user):
        product = update.callback_query.data.replace(READY, "")
        product = Product.objects.get(name=product)
        context.bot.send_message(chat_id=update.callback_query.message.chat_id, text="Выберите район",
                                  reply_markup=make_keyboard_for_districts(user=user, product=product))


def klad_type_handler(update: Update, context: CallbackContext):
    user = User.get_user(update, context)
    if not _is_user_courier(user):
        fasovka = update.callback_query.data.replace(FASOFKA, "")
        fasovka = fasovka.split(CHOSEN_PRODUCT_NAME)[0]
        fasovka = Fasovka.objects.get(grams=float(fasovka))
        product = update.callback_query.data.split(CHOSEN_PRODUCT_NAME)[1].split(CHOSEN_DISTRICT)[0]
        product = Product.objects.get(name=product)
        district = update.callback_query.data.split(CHOSEN_DISTRICT)[1]
        district = District.objects.get(district_name=district)
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=f"Вы выбрали {fasovka} фасовку",
        )
        order = Order.objects.create(user=user, product=product, city=user.city, district=district,
                                     fasovka=fasovka)
        context.bot.send_message(chat_id=update.callback_query.message.chat_id, text="Выберите тип клада",
                                 reply_markup=make_keyboard_for_klad_type(user=user, order_id=order.id))


def ready_decision_handler(update: Update, context: CallbackContext):
    user = User.get_user(update, context)
    if not _is_user_courier(user):
        order_id = update.callback_query.data.split(CHOSEN_ORDER)[1]
        order = Order.objects.get(id=int(order_id))
        klad_type = update.callback_query.data.replace(KLAD_TYPE, "")
        klad_type = klad_type.split(CHOSEN_ORDER)[0]
        product = order.product
        fasovka = order.fasovka
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=f"Вы выбрали тип клада {klad_type}",
        )
        btc_price = float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCRUB").json()["price"])
        rub_price = ProductToFasovka.objects.get(product=product, fasovka=fasovka).price
        order_price = rub_price / btc_price
        rounded_order_price = round(order_price, 8)
        order.klad_type = klad_type
        order.price = rounded_order_price
        order.save()
        context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=order_description.format(city_name=user.city.name,
                district_name=order.district.district_name,
                product_name=order.product.name,
                fasovka_name=str(order.fasovka.grams),
                price_name=str(order.price),
                rub_price_str=str(rub_price),
                klad_type=klad_type),
                reply_markup=make_keyboard_for_bye_or_decline()
            )


def buy_or_decline_handler(update: Update, context: CallbackContext):
    u = User.get_user(update, context)
    if not _is_user_courier(u):
        broadcast_decision = update.callback_query.data
        order = Order.objects.filter(user=u).first()
        if broadcast_decision.endswith("Купить"):
            if u.balance >= order.price:
                u.balance -= order.price
                u.save()
                order.is_paid = True
                order.save()
                zakladka = Zakladka.objects.filter(city=order.city, district=order.district, product=order.product,
                                                   fasovka=order.fasovka, is_taken=False).first()
                context.bot.send_message(
                    chat_id=update.callback_query.message.chat_id,
                    text="Оплата прошла успешно!",
                )
                zakladka.is_taken = True
                zakladka.save()
                order.zakladka = zakladka
                order.save()
                context.bot.send_message(
                    chat_id=update.callback_query.message.chat_id,
                    text=buyed_order_text.format(
                        city_name=zakladka.city.name,
                        district_name=zakladka.district.district_name,
                        product_name=zakladka.product.name,
                        fasovka_name=str(zakladka.fasovka.grams),
                        price_name=str(order.price),
                        description=zakladka.description,
                        klad_type=klad_types[zakladka.klad_type]
                    ),
                )
                context.bot.send_photo(
                    chat_id=update.callback_query.message.chat_id,
                    photo=zakladka.image
                )
                context.bot.send_message(
                    chat_id=update.callback_query.message.chat_id,
                    text="Спасибо за заказ!",
                )
            else:
                context.bot.send_message(
                    chat_id=update.callback_query.message.chat_id,
                    text="На вашем балансе не хватает средств. Вы можете пополнить баланс.",
                    reply_markup=make_keyboard_for_account_command()
                )
        else:
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text="Выберите товар",
                reply_markup=make_keyboard_for_available(user=u)
            )

def fasofka_handler(update: Update, context: CallbackContext):
    u = User.get_user(update, context)
    if not _is_user_courier(u):
        broadcast_decision = update.callback_query.data
        district = broadcast_decision.replace(DISTRICT, "")
        district = district.split(CHOSEN_PRODUCT_NAME)[0]
        product_name = broadcast_decision.split(CHOSEN_PRODUCT_NAME)[1]
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=f"Вы выбрали {district} район",
        )
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text="Выберите фасовку",
            reply_markup=make_keyboard_for_fasofka(Product.objects.get(name=product_name), district=district)
        )


def courier_menu_handler(update: Update, context: CallbackContext):
    u = User.get_user(update, context)
    if update.message.text == "Добавить товар":
        if _is_user_courier(u):
            if not Courier.objects.get(telegram_id=u.user_id).city:
                update.message.reply_text(text="Для начала выбери город в котором работаешь: ",
                                          reply_markup=make_keyboard_for_start_command())
            else:
                update.message.reply_text(text="Название товара:",
                                      reply_markup=make_keyboard_for_c_products())
    elif update.message.text == "Статистика":
        if _is_user_courier(u):
            update.message.reply_text(
                text=_courier_statistic(u),
            )
    else:
        update.message.reply_text(
            text="Неверная команда",
        )


def c_product_chosen_handler_district(update: Update, context: CallbackContext):
    user = User.get_user(update, context)
    product = update.callback_query.data.replace(READYC, "")
    product = Product.objects.get(name=product)
    context.bot.send_message(chat_id=update.callback_query.message.chat_id, text="Район",
                                  reply_markup=make_keyboard_for_districts_c(user=user, product=product))


def c_fasofka_handler(update: Update, context: CallbackContext):
    u = User.get_user(update, context)
    broadcast_decision = update.callback_query.data
    district = broadcast_decision.replace(DISTRICTC, "")
    district = district.split(CHOSEN_PRODUCT_NAME)[0]
    product_name = broadcast_decision.split(CHOSEN_PRODUCT_NAME)[1]
    context.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text=f"Ты выбрал {district} район",
    )
    context.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text="Выбери фасовку",
        reply_markup=make_keyboard_for_fasofka_c(Product.objects.get(name=product_name), district=district)
    )


def c_klad_type_handler(update: Update, context: CallbackContext):
    user = User.get_user(update, context)
    fasovka = update.callback_query.data.replace(FASOFKAC, "")
    fasovka = fasovka.split(CHOSEN_PRODUCT_NAME)[0]
    fasovka = Fasovka.objects.get(grams=float(fasovka))
    product = update.callback_query.data.split(CHOSEN_PRODUCT_NAME)[1].split(CHOSEN_DISTRICT)[0]
    product = Product.objects.get(name=product)
    district = update.callback_query.data.split(CHOSEN_DISTRICT)[1]
    district = District.objects.get(district_name=district)
    context.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text=f"Ты выбрал {fasovka} фасовку",
    )
    TempZakladkaForCourier.objects.create(courier=Courier.objects.get(telegram_id=user.user_id),
                                          product=Product.objects.get(name=product),
                                          district=District.objects.get(district_name=district),
                                          fasovka=Fasovka.objects.get(grams=float(fasovka.grams)))
    context.bot.send_message(chat_id=update.callback_query.message.chat_id, text="Выбери тип клада",
                                 reply_markup=make_keyboard_for_klad_type_c())


def received_klad_next_step_handler(update: Update, context: CallbackContext):
    user = User.get_user(update, context)
    klad_type = update.callback_query.data.replace(KLAD_TYPEC, "")
    context.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text=f"Вы выбрали тип клада {klad_type}",
    )
    zk = TempZakladkaForCourier.objects.filter(courier=Courier.objects.get(telegram_id=user.user_id)).last()
    zk.klad_type = get_key(klad_types, klad_type)
    zk.save()
    context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text="Напиши описание товара, начиная со слова ОПИСАНИЕ (пример: ОПИСАНИЕ Находится у...).\nЕсли не появилось сообщение об успешном описании, введи еще раз в правильном формате."
        )

def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k

def description_handler(update: Update, context: CallbackContext):
    desc = update.message.text
    _, d = desc.split("ОПИСАНИЕ ")
    zk = TempZakladkaForCourier.objects.last()
    zk.description = d
    zk.save()
    update.message.reply_text(
        text=f"Успешно добавлено описание: \n{d}"
    )
    update.message.reply_text(
        text=f"Пришли фотографию локации"
    )


def location_photo_handler(update: Update, context: CallbackContext):
    user = User.get_user(update, context)
    courier = Courier.objects.get(telegram_id=user.user_id)
    if _is_user_courier(user) and TempZakladkaForCourier.objects.filter(courier=courier):
        zk = TempZakladkaForCourier.objects.filter(courier=courier).last()
        print(update)
        if not zk.image:
            file_id = update.message.photo[-1].file_id
            file = context.bot.get_file(file_id)
            file.download(f"./images/{file_id}_zk.jpg")
            zk.image = f"./images/{file_id}_zk.jpg"
            zk.save()
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=f"Фото отправлено успешно"
            )
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text="Ваша закладка:"
            )
            context.bot.send_photo(
                chat_id=update.message.chat_id,
                photo=zk.image
            )
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=zakladka_created.format(
                    city_name=courier.city.name,
                    district_name=zk.district.district_name,
                    product_name=zk.product.name,
                    fasovka_name=str(zk.fasovka.grams),
                    description=zk.description,
                    klad_type=klad_types[zk.klad_type]
                )
            )
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text="Сохранить?", reply_markup=make_keyboard_for_confirm_zk()
            )


def confirm_zk_handler(update: Update, context: CallbackContext):
    user = User.get_user(update, context)
    courier = Courier.objects.get(telegram_id=user.user_id)
    decision = update.callback_query.data.replace(CONFIRM_ZK, "")
    zk = TempZakladkaForCourier.objects.filter(courier=courier).last()
    if decision == "Сохранить":
        real_zk = Zakladka.objects.create(courier=courier,
                                city=courier.city,
                                district=zk.district,
                                product=zk.product,
                                fasovka=zk.fasovka,
                                description=zk.description,
                                image=zk.image,
                                klad_type=zk.klad_type)
        zk.delete()
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text="Закладка создана"
        )
        context.bot.send_photo(
            chat_id=update.callback_query.message.chat_id,
            photo=real_zk.image
        )
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=zakladka_created.format(
                city_name=real_zk.city.name,
                district_name=real_zk.district.district_name,
                product_name=real_zk.product.name,
                fasovka_name=str(real_zk.fasovka.grams),
                description=real_zk.description,
                klad_type=klad_types[real_zk.klad_type]
            )
        )
        context.bot.send_message(update.callback_query.message.chat_id, text=welcome_message_courier,
                                  reply_markup=make_keyboard_for_curier_menu())
    else:
        context.bot.send_message(update.callback_query.message.chat_id,
                                text=welcome_message_courier,
                                reply_markup=make_keyboard_for_curier_menu())


def _courier_statistic(user):
    courier = Courier.objects.get(telegram_id=user.user_id)
    zks = Zakladka.objects.filter(courier=courier)
    return couries_stat_text.format(date_create=courier.created_at,
                                    zk_count=zks.count(),
                                    zk=zks.first(),
                                    city=courier.city.name if courier.city else "Не выбран")


def _is_user_courier(user: User):
    if Courier.objects.filter(telegram_id=user.user_id):
        return True
    return False
