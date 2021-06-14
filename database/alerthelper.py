from model.database.alert import AlertDao


class AlertHelper:
    def __init__(self, logger):
        self.logger = logger

    def insert(self, conn, alert_data):
        alert_dao_obj = AlertDao()
        alert_dao = alert_dao_obj.dao_table()

        try:
            stmt = alert_dao \
                .insert() \
                .values(chat_id=alert_data.chat_id, crypto=alert_data.crypto, condition=alert_data.condition,
                        alert_price=alert_data.alert_price, base_ccy=alert_data.base_ccy,
                        max_alert_count=alert_data.max_alert_count, active=alert_data.active,
                        last_alert_at=alert_data.last_alert_at, created_at=alert_data.created_at,
                        updated_at=alert_data.updated_at)

            ret = conn.execute(stmt)
            return True if ret.lastrowid > 0 else False, None
        except Exception as e:
            self.logger.error(f'Failed to insert alert data in db. Error: {str(e)}')
            return False, str(e)
