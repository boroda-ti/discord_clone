import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from models import Base

class DBSingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class DataBase(metaclass = DBSingletonMeta):
    def __init__(self):
        url = self._create_url(os.getenv('PG_USER'), os.getenv('PG_PASS'), os.getenv('PG_HOST'), os.getenv('PG_PORT'), os.getenv('PG_NAME'))

        self.async_engine = create_async_engine(url, future=True)
        self.async_session = async_sessionmaker(bind=self.async_engine, expire_on_commit=False)

    async def get_query(self, query: str):
        async with self.async_session() as session:
            result = await session.execute(query)
            
        return result

    @staticmethod
    def _create_url(user: str, password: str, host: str, port: str, dbname: str) -> str:
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"
    
database = DataBase()