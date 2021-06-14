from sqlalchemy import create_engine


class SqliteDb:
    def __init__(self, config):
        self.engine = create_engine(config.get_database_connection() + ":///" + config.get_database_file(), echo=False,
                                    isolation_level="AUTOCOMMIT")

    def connect(self):
        return self.engine.connect()
