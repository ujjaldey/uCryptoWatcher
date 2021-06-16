import datetime

from telegram import ParseMode
from telegram.ext import Defaults, Updater, CommandHandler, CallbackQueryHandler, PicklePersistence

from api.coinmarketcap import CoinMarketCap
from messaging.telegrambothelper import TelegramBotHelper


class TelegramBot(TelegramBotHelper):
    def __init__(self, config, logger, db):
        self._set_logger(logger)
        self._set_config(config)
        self._set_db(db)

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
        self.dp.add_handler(CommandHandler('setalert', self._set_alert))

        # self.updater.job_queue.run_once(self._status, when=0)
        chat_id = 1542846687  # TODO from db
        # self.updater.job_queue.run_repeating(self._set_alert_callback, interval=5, first=1, context=[123, chat_id])

    def start(self):
        self.updater.start_polling()
        self.updater.idle()
