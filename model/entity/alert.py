from datetime import datetime


class Alert:
    def __init__(self, chat_id, crypto, condition, alert_price, base_ccy, max_alert_count, active,
                 last_alert_at, id=0, alert_count=0, created_at=datetime.now().replace(microsecond=0),
                 updated_at=datetime.now().replace(microsecond=0)):
        self.id = id
        self.chat_id = chat_id
        self.crypto = crypto
        self.condition = condition
        self.alert_price = alert_price
        self.base_ccy = base_ccy
        self.max_alert_count = max_alert_count
        self.alert_count = alert_count
        self.active = active
        self.last_alert_at = last_alert_at
        self.created_at = created_at
        self.updated_at = updated_at
