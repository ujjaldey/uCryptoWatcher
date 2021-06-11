class Quote:
    def __init__(self, name, symbol, slug, price, convert_ccy, percent_change_1h, percent_change_24h, percent_change_7d,
                 percent_change_30d, percent_change_60d, percent_change_90d, timestamp):
        self.name = name
        self.symbol = symbol
        self.slug = slug
        self.price = price
        self.convert_ccy = convert_ccy
        self.percent_change_1h = percent_change_1h
        self.percent_change_24h = percent_change_24h
        self.percent_change_7d = percent_change_7d
        self.percent_change_30d = percent_change_30d
        self.percent_change_60d = percent_change_60d
        self.percent_change_90d = percent_change_90d
        self.timestamp = timestamp
