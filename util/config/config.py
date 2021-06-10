from dotenv import dotenv_values


class Config:
    def __init__(self):
        self.config = dotenv_values('.env')

    def get_telegram_api_key(self):
        return self.config['TELEGRAM_API_KEY']

    def get_coinmarketcap_api_base_url(self):
        return self.config['COINMARKETCAP_API_BASE_URL']

    def get_coinmarketcap_api_keys(self):
        return self.config['COINMARKETCAP_API_KEYS'].split(",")

    def get_default_ccy(self):
        return self.config['DEFAULT_CCY']
