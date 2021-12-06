import TelegramBot as tb
import CryptoAPIs as ca
import time
import datetime as dt


class ArbitrageAlert:
    def __init__(self, exchange_1, exchange_2, pair_1, pair_2, arbitrage_rate, interval, telegram_token):
        self.exchange_1_name = exchange_1
        self.exchange_2_name = exchange_2
        self.exchange_1 = ca.get_exchange(exchange_1)
        self.exchange_2 = ca.get_exchange(exchange_2)
        self.pair_1 = pair_1
        self.pair_2 = pair_2
        self.arbitrage_rate = arbitrage_rate
        self.interval = interval
        self.suspend_until = None
        self.telegram_token = telegram_token
        self.telegram_chat_id = None
        try:
            self.telegram_chat_id = tb.TelegramBot.getChatID(self.telegram_token)
        except Exception as e:
            raise e
        self.handle()

    def handle(self):
        bot = tb.TelegramBot(self.telegram_token, self.telegram_chat_id)
        while True:
            try:
                price_1 = self.exchange_1.get_price(self.pair_1)
                price_2 = self.exchange_2.get_price(self.pair_2)

                price_difference = round(price_1 - price_2, 2)
                percent_difference = round(1 - price_2 / price_1, 2)

                if percent_difference >= self.arbitrage_rate:
                    if not self.suspend_until:
                        self.suspend_until = dt.datetime.utcnow() + dt.timedelta(seconds=self.interval)
                        msg = f"Arbitrage Möglichkeit zwischen:\n " \
                              f"{self.exchange_1_name} = {price_1}$\n" \
                              f"{self.exchange_2_name} = {price_2}$\n" \
                              f"{price_difference}$ - {percent_difference * 100}%"
                        bot.sendMessage(msg)

                if self.suspend_until:
                    if self.suspend_until <= dt.datetime.utcnow():
                        self.suspend_until = None

                time.sleep(1)
            except Exception as e:
                print(e)
                print("Wird neu gestartet...")



token = "1910759993:AAGpzGdVPm3af7ld0VfmGKQEDncRFuk-fTA"
alert_1 = ArbitrageAlert("kucoin", "defichain_dex", "DFI-USDT", "USDT-DFI", 0.2, 14400, token)
alert_2 = ArbitrageAlert("kucoin", "defichain_dex", "DFI-USDT", "USDC-DFI", 0.2, 14400, token)
