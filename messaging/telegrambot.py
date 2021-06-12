from telegram import ParseMode
from telegram.ext import Defaults, Updater, CommandHandler, CallbackQueryHandler

from api.coinmarketcap import CoinMarketCap
from messaging.telegrambothelper import TelegramBotHelper


class TelegramBot(TelegramBotHelper):
    def __init__(self, config, logger):
        self._set_logger(logger)
        self._set_config(config)

        self.cmc = CoinMarketCap(self.config, self.logger)
        self._set_coinmarketcap(config)

        defaults = Defaults(parse_mode=ParseMode.HTML)
        self.updater = Updater(token=config.get_telegram_api_key(), use_context=True, defaults=defaults)
        self.dp = self.updater.dispatcher

    def add_handlers(self):
        self.dp.add_handler(CommandHandler('status', self._status))
        self.dp.add_handler(CommandHandler('help', self._help))
        self.dp.add_handler(CallbackQueryHandler(self._button))
        self.dp.add_handler(CommandHandler('getprice', self._get_price))
        self.dp.add_handler(CommandHandler('getdetail', self._get_detail))
        # self.dp.add_handler(CommandHandler('alert', self._send_alert))

    def start(self):
        self.updater.start_polling()
        self.updater.idle()
