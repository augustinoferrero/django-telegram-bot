from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from tgbot.handlers.onboarding.manage_data import START, BALANCE, READY, BUY_OR_DECLINE, FASOFKA, CONFIRM, \
    DISTRICT, CHOSEN_PRODUCT_NAME, CHOSEN_DISTRICT, KLAD_TYPE, READYC, DISTRICTC, FASOFKAC, KLAD_TYPEC, \
    CONFIRM_ZK, CITIESC, CHOSEN_ORDER
from tgbot.models import *

klad_types = dict(KlAD_CHOICES)


def make_keyboard_for_start_command() -> InlineKeyboardMarkup:
    cities = City.objects.all()
    buttons = [[
        InlineKeyboardButton(city.name, callback_data=START+city.name) for city in cities
    ]]

    return InlineKeyboardMarkup(buttons)

def make_keyboard_for_bye_or_decline():
    buttons = [[
        InlineKeyboardButton("Купить", callback_data=BUY_OR_DECLINE + "Купить"),
        InlineKeyboardButton("Выбрать другой товар", callback_data=BUY_OR_DECLINE + "Другой"),
    ]]

    return InlineKeyboardMarkup(buttons)


def make_keyboard_for_fasofka(product, district):
    fasovkas = Fasovka.objects.filter(related_products=product)
    buttons = [[
        InlineKeyboardButton(fas.grams, callback_data=FASOFKA+str(fas.grams) +
                                                      CHOSEN_PRODUCT_NAME + product.name +
                                                      CHOSEN_DISTRICT + district) for fas in fasovkas
    ]]

    return InlineKeyboardMarkup(buttons)


def make_keyboard_for_account_command() -> InlineKeyboardMarkup:
    buttons = [[
        InlineKeyboardButton("Пополнить баланс", callback_data=BALANCE+"Пополнить баланс")
    ]]

    return InlineKeyboardMarkup(buttons)


def make_keyboard_for_not_available(user) -> InlineKeyboardMarkup:
    available = Zakladka.objects.filter(city=user.city)
    buttons = [[
        InlineKeyboardButton(a.product.name, callback_data=READY + a.product.name) for a in available if not
        a.product.is_available
    ]]

    return InlineKeyboardMarkup(buttons)


def make_keyboard_for_available(user) -> InlineKeyboardMarkup:
    available = Zakladka.objects.filter(city=user.city, is_taken=False)
    buttons = [[
        InlineKeyboardButton(a.product.name, callback_data=READY+a.product.name) for a in available if a.product.is_available
    ]]

    return InlineKeyboardMarkup(buttons)


def make_keyboard_for_districts(user, product) -> InlineKeyboardMarkup:
    zakladkas = Zakladka.objects.filter(product=product, city=user.city)
    districts = []
    for z in zakladkas:
        ds = District.objects.filter(zakladka=z)
        for i in ds:
            districts.append(i)
    buttons = [[
        InlineKeyboardButton(d.district_name, callback_data=DISTRICT + d.district_name + CHOSEN_PRODUCT_NAME +product.name) for d in districts
    ]]

    return InlineKeyboardMarkup(buttons)


def make_keyboard_for_klad_type(user, order_id):
    order = Order.objects.get(id=order_id)
    zakladkas = Zakladka.objects.filter(product=order.product, city=user.city, district=order.district, fasovka=order.fasovka)
    buttons = [[
        InlineKeyboardButton(klad_types[z.klad_type],
                             callback_data=KLAD_TYPE + klad_types[
                                 z.klad_type] + CHOSEN_ORDER + str(order_id)) for z in zakladkas
    ]]

    return InlineKeyboardMarkup(buttons)


def make_keyboard_for_curier_menu():
    return ReplyKeyboardMarkup(
        [[KeyboardButton(text="Добавить товар"), KeyboardButton(text="Статистика")]],
        resize_keyboard=True
    )


def make_keyboard_for_c_cities():
    cities = City.objects.all()
    buttons = [[
        InlineKeyboardButton(c.name, callback_data=CITIESC + c) for c in cities
    ]]

    return InlineKeyboardMarkup(buttons)


def make_keyboard_for_c_products():
    products = Product.objects.all()
    buttons = [[
        InlineKeyboardButton(p.name, callback_data=READYC+p.name) for p in products
    ]]

    return InlineKeyboardMarkup(buttons)


def make_keyboard_for_districts_c(user, product) -> InlineKeyboardMarkup:
    courier = Courier.objects.get(telegram_id=user.user_id)
    districts = District.objects.filter(city=courier.city)
    buttons = [[
        InlineKeyboardButton(d.district_name, callback_data=DISTRICTC + d.district_name + CHOSEN_PRODUCT_NAME +product.name) for d in districts
    ]]

    return InlineKeyboardMarkup(buttons)


def make_keyboard_for_fasofka_c(product, district):
    fasovkas = Fasovka.objects.all()
    buttons = [[
        InlineKeyboardButton(fas.grams, callback_data=FASOFKAC+str(fas.grams) +
                                                      CHOSEN_PRODUCT_NAME + product.name +
                                                      CHOSEN_DISTRICT + district) for fas in fasovkas
    ]]

    return InlineKeyboardMarkup(buttons)


def make_keyboard_for_klad_type_c():
    klad_types_list = klad_types.values()
    buttons = [[
        InlineKeyboardButton(kt,
                             callback_data=KLAD_TYPEC + kt) for kt in klad_types_list
    ]]

    return InlineKeyboardMarkup(buttons)


def make_keyboard_for_confirm_zk():
    buttons = [[
        InlineKeyboardButton("Сохранить" ,callback_data=CONFIRM_ZK+"Сохранить"),
        InlineKeyboardButton("Отмена", callback_data=CONFIRM_ZK+"Отмена"),
    ]]

    return InlineKeyboardMarkup(buttons)