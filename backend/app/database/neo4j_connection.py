from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError
from app.config import get_settings

settings = get_settings()

class Neo4jConnection:
    def __init__(self):
        self.driver = None

    def connect(self):
        if self.driver is None:
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
            )
            self.driver.verify_connectivity()
        return self.driver

    def close(self):
        if self.driver:
            self.driver.close()
            self.driver = None

    def run_write(self, query: str, parameters: dict | None = None):
        driver = self.connect()
        try:
            with driver.session() as session:
                return session.execute_write(lambda tx: list(tx.run(query, parameters or {})))
        except Neo4jError:
            raise

    def run_read(self, query: str, parameters: dict | None = None):
        driver = self.connect()
        try:
            with driver.session() as session:
                rows = session.execute_read(lambda tx: list(tx.run(query, parameters or {})))
                return [record.data() for record in rows]
        except Neo4jError:
            raise

neo4j_db = Neo4jConnection()
