from dotenv import dotenv_values


class Config:
    def __init__(self):
        self.config = dotenv_values('.env')

    def get_telegram_bot_name(self):
        return self.config['TELEGRAM_BOT_NAME']

    def get_telegram_api_key(self):
        return self.config['TELEGRAM_API_KEY']

    def get_coinmarketcap_api_base_url(self):
        return self.config['COINMARKETCAP_API_BASE_URL']

    def get_coinmarketcap_api_keys(self):
        return self.config['COINMARKETCAP_API_KEYS'].split(",")

    def get_base_ccy(self):
        return self.config['BASE_CCY']
