from telegram import ParseMode
from telegram.ext import Defaults, Updater, CommandHandler, CallbackQueryHandler

from api.coinmarketcap import CoinMarketCap
from database.alerthelper import AlertHelper
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

    def reload_active_alerts(self):
        alert_helper = AlertHelper(self.logger)
        result, output = alert_helper.select(self.db.connect())

        for rec in output:
            self.logger.info(f'Reloading active alert id {rec.id}')

            self.updater.job_queue.run_repeating(self._set_alert_callback,
                                                 interval=int(self.config.get_alert_frequency_sec()),
                                                 context=[rec.crypto, rec.condition, rec.alert_price, rec.base_ccy,
                                                          rec.chat_id, rec.max_alert_count, rec.alert_count, rec.id])

    def start(self):
        self.updater.start_polling()
        self.updater.idle()
