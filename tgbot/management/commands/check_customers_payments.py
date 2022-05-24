import os

import requests
import time
from django.core.management.base import BaseCommand

from tgbot.dispatcher import bot
from tgbot.models import User

from bit import PrivateKey

class Command(BaseCommand):
    help = "Check if money arrived"

    def handle(self, *args, **options):
        print("Start")
        while True:
            try:
                users = User.objects.all()
                for user in users:
                    self.checked_balance(user)
                time.sleep(180)
            except Exception as e:
                print(str(e))
                time.sleep(60)

    def checked_balance(self, user):
        # Адрес кошелька пользователя
        wallet = user.btc_address

        url = f'https://blockchain.info/rawaddr/{wallet}'
        x = requests.get(url)
        wallet = x.json()
        inputs_txs = [tx for tx in wallet["txs"] if tx["result"] > 0]
        if user.transactions < len(inputs_txs):
            new_txs = len(inputs_txs) - user.transactions
            for tx in inputs_txs[-new_txs:]:
                user.balance += tx["result"] / 100000000
                user.transactions += 1
                my_key = PrivateKey(wif=user.wif)
                our_wallet = os.getenv("OUR_WALLET")
                fee = int(os.getenv("COMMISSION"))
                amount = (tx["result"] - fee) / 100000000
                tx_hash = my_key.create_transaction([(our_wallet, amount, 'btc')], fee=fee, absolute_fee=True)
                url = 'https://blockchain.info/pushtx'
                x = requests.post(url, data={'tx': tx_hash})
                result = x.text
                print("РЕЗУЛЬТАТ: ", result)
            user.save()
            bot.send_message(chat_id=user.chat_id, text=f"Ваш баланс пополнен и составляет {user.balance} BTC\nУдачных покупок!")
