import json

from requests import Session

from model.api.error import ApiError
from model.api.quote import Quote


class CoinMarketCap:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.api_base_url = config.get_coinmarketcap_api_base_url()
        self.api_key = config.get_coinmarketcap_api_keys()[0]  # TODO

    @staticmethod
    def __get_session(headers):
        session = Session()
        session.headers.update(headers)
        return session

    @staticmethod
    def __get_parameters(base_ccy, symbol):
        return {
            'symbol': symbol,
            'convert': base_ccy,
            'aux': 'num_market_pairs,cmc_rank,date_added,platform,max_supply,circulating_supply,total_supply,'
                   'market_cap_by_total_supply,volume_24h_reported,volume_7d,volume_7d_reported,'
                   'volume_30d,volume_30d_reported,is_active,is_fiat'
        }

    @staticmethod
    def __get_headers(api_key):
        return {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': api_key,
        }

    @staticmethod
    def __convert_to_quote_obj(data, symbol, base_ccy):
        crypto_data = data['data'][symbol]
        quote_data = crypto_data['quote'][base_ccy]

        return Quote(crypto_data['name'], crypto_data['symbol'], crypto_data['slug'], float(quote_data['price']),
                     base_ccy, float(quote_data['percent_change_1h']), float(quote_data['percent_change_24h']),
                     float(quote_data['percent_change_7d']), float(quote_data['percent_change_30d']),
                     float(quote_data['percent_change_60d']), float(quote_data['percent_change_90d']),
                     crypto_data['last_updated'])

    @staticmethod
    def __convert_to_api_error(data):
        status_data = data['status']
        return ApiError(status_data['error_code'], status_data['error_message'], status_data['timestamp'])

    def get_quotes_latest(self, symbol, base_ccy):
        url = 'quotes/latest'
        headers = self.__get_headers(self.api_key)
        session = self.__get_session(headers)
        parameters = self.__get_parameters(self.config.get_base_ccy(), symbol)

        try:
            self.logger.info(f'Calling url {url} for {symbol}')

            response = session.get(self.api_base_url + url, params=parameters)
            data = json.loads(response.text)

            if 'statusCode' in data and data['statusCode'] == 404:
                response_code = data['statusCode']
                response_message = data['message']
            else:
                response_code = data['status']['error_code']

                if response_code != 0:
                    response_message = data['status']['error_message']

            if response_code == 0:
                self.logger.info(f'Response Code from {url}: {response_code}')

                return True, self.__convert_to_quote_obj(data, symbol, base_ccy), None
            else:
                self.logger.error(f'Response Code from {url}: {response_code}. Error: {response_message}')
                return False, None, self.__convert_to_api_error(data)
        except Exception as e:
            self.logger.error(f'Failed {url}. Error: {str(e)}')
            return False, None
