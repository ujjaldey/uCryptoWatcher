from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, MetaData, String, Table, Numeric, Integer


class AlertDao:
    def __init__(self):
        self.table = Table(
            "alerts", MetaData(),
            Column("id", Integer, autoincrement=True, nullable=False, primary_key=True, unique=True),
            Column("chat_id", String, nullable=False),
            Column("crypto", String, nullable=False),
            Column("condition", String, nullable=False),
            Column("alert_price", Numeric, nullable=False),
            Column("base_ccy", String, nullable=False),
            Column("max_alert_count", Integer, nullable=True),
            Column("alert_count", Integer, nullable=True, default=0),
            Column("active", String, nullable=True),
            Column("last_alert_at", String, nullable=True, default=datetime.now),
            Column("created_at", String, nullable=True, default=datetime.now),
            Column("updated_at", String, nullable=True, default=datetime.now)
        )

    def dao_table(self):
        return self.table
