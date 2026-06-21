from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from .config import settings
from .logger import get_logger

logger = get_logger(__name__)

engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(bind=engine)
metadata = MetaData()

def init_db(sql_file: str = './sql/init_db.sql') -> None:
    with engine.connect() as conn:
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql = f.read()
        conn.execute(sql)
        conn.commit()
    logger.info('Database initialized using %s', sql_file)
