from telegram import ParseMode
from telegram.ext import Defaults, Updater, PrefixHandler

from messaging.telegrambothelper import TelegramBotHelper


class TelegramBot(TelegramBotHelper):
    def __init__(self, config, logger):
        self._set_logger(logger)

        defaults = Defaults(parse_mode=ParseMode.HTML)
        self.updater = Updater(token=config.get_telegram_api_key(), use_context=True, defaults=defaults)
        self.dp = self.updater.dispatcher

    def add_handlers(self):
        self.dp.add_handler(PrefixHandler('/', 'status', self._status))
        self.dp.add_handler(PrefixHandler('/', 'help', self._help))
        # self.dp.add_handler(PrefixHandler('/', 'price', self._send_price))
        # self.dp.add_handler(PrefixHandler('/', 'detail', self._send_detail))
        # self.dp.add_handler(PrefixHandler('/', 'alert', self._send_alert))

    def start(self):
        self.updater.start_polling()
        self.updater.idle()
