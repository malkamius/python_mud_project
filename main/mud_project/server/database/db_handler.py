import aiosqlite
import asyncio
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class DatabaseHandler:
    def __init__(self, db_config):
        self.db_path = db_config['path']
        self._connection = None
        self._lock = asyncio.Lock()

    async def initialize(self):
        try:
            self._connection = await aiosqlite.connect(self.db_path)
            await self._connection.execute("PRAGMA journal_mode=WAL")
            await self.create_tables()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    async def create_tables(self):
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Add more table creation statements as needed
        await self._connection.commit()

    @asynccontextmanager
    async def get_connection(self):
        async with self._lock:
            yield self._connection

    async def close(self):
        if self._connection:
            async with self._lock:
                await self._connection.close()
                self._connection = None
            logger.info("Database connection closed")

    # Example of a database operation method
    async def add_player(self, username, password_hash):
        async with self.get_connection() as conn:
            await conn.execute(
                "INSERT INTO players (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            await conn.commit()

    # Add more methods for other database operations

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()