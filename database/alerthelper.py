from sqlalchemy import select

from model.database.alert import AlertDao
from sqlalchemy.sql import and_

from model.entity.alert import Alert


class AlertHelper:
    def __init__(self, logger):
        self.logger = logger

    def select(self, conn):
        alert_dao_obj = AlertDao()
        alert_dao = alert_dao_obj.dao_table()

        try:
            stmt = select([alert_dao.c.id, alert_dao.c.chat_id, alert_dao.c.crypto, alert_dao.c.condition,
                           alert_dao.c.alert_price, alert_dao.c.base_ccy, alert_dao.c.max_alert_count,
                           alert_dao.c.alert_count, alert_dao.c.active, alert_dao.c.last_alert_at,
                           alert_dao.c.created_at, alert_dao.c.updated_at]) \
                .where(and_(alert_dao.c.active == 'Y', alert_dao.c.max_alert_count >= alert_dao.c.alert_count)) \
                .order_by(alert_dao.c.id.asc())

            ret = conn.execute(stmt)

            active_alerts = []

            for rec in ret:
                alert_data = Alert(id=rec['id'], chat_id=rec['chat_id'], crypto=rec['crypto'],
                                   condition=rec['condition'], alert_price=float(rec['alert_price']),
                                   base_ccy=rec['base_ccy'], max_alert_count=int(rec['max_alert_count']),
                                   alert_count=int(rec['alert_count']), active=rec['active'],
                                   last_alert_at=rec['last_alert_at'], created_at=rec['created_at'],
                                   updated_at=rec['updated_at'])

                active_alerts.append(alert_data)

            return True, active_alerts
        except Exception as e:
            self.logger.error(f'Failed to select alert data from db. Error: {str(e)}')
            return False, str(e)

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
            return True if ret.lastrowid > 0 else False, ret.lastrowid
        except Exception as e:
            self.logger.error(f'Failed to insert alert data in db. Error: {str(e)}')
            return False, str(e)

    def update_alert_count(self, conn, alert_data, alert_count):
        alert_dao_obj = AlertDao()
        alert_dao = alert_dao_obj.dao_table()

        try:
            stmt = alert_dao \
                .update() \
                .values(alert_count=alert_count, last_alert_at=alert_data.last_alert_at,
                        updated_at=alert_data.updated_at) \
                .where(and_(alert_dao.c.id == alert_data.id))

            conn.execute(stmt)
            return True, None
        except Exception as e:
            self.logger.error(f'Failed to insert alert data in db. Error: {str(e)}')
            return False, str(e)

    def update_active_flg(self, conn, alert_data, active):
        alert_dao_obj = AlertDao()
        alert_dao = alert_dao_obj.dao_table()

        try:
            stmt = alert_dao \
                .update() \
                .values(active=active, updated_at=alert_data.updated_at) \
                .where(and_(alert_dao.c.id == alert_data.id))

            conn.execute(stmt)
            return True, None
        except Exception as e:
            self.logger.error(f'Failed to insert alert data in db. Error: {str(e)}')
            return False, str(e)
