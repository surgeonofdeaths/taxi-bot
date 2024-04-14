# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config.config import config


url = f"postgresql+{config.db.drivername}://" \
      f"{config.db.user}:{config.db.password}@" \
      f"{config.db.host}:{config.db.port}" \
      f"/{config.db.database}"
print(url)
engine = create_async_engine(url=url, echo=True)
sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
