from messaging.telegrambot import TelegramBot
from util.config.config import Config
from util.logger.logger import Logger


class Main:
    def __init__(self):
        logger = Logger(__file__)
        self.logger = logger.get_logger()

        config = Config()
        self.config = config

    def start_app(self):
        self.logger.info("Starting uCryptoWatcher")
        telegram_bot = TelegramBot(self.config, self.logger)
        telegram_bot.add_handlers()
        telegram_bot.start()


if __name__ == '__main__':
    main = Main()
    main.start_app()
