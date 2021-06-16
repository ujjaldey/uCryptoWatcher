from database.sqlitedb import SqliteDb
from messaging.telegrambot import TelegramBot
from util.config.config import Config
from util.logger.logger import Logger


class Main:
    def __init__(self):
        logger = Logger(__file__)
        self.logger = logger.get_logger()

        self.config = Config()
        self.db = SqliteDb(self.config)

    def start_app(self):
        self.logger.info("Starting uCryptoWatcher")
        telegram_bot = TelegramBot(self.config, self.logger, self.db)
        telegram_bot.add_handlers()
        telegram_bot.reload_active_alerts()
        telegram_bot.start()


if __name__ == '__main__':
    main = Main()
    main.start_app()
