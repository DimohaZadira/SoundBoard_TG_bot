from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine,  Column, Integer, String
from tg_bot.config import load_config

config = load_config('.env')
engine = create_engine(f"postgresql+psycopg2://{config.db.user}:{config.db.password}@{config.db.host}/{config.db.name}")
Session = sessionmaker()
session = Session(bind=engine)

Base = declarative_base()

class Files(Base):
    __tablename__= "files"
    Id = Column(Integer, primary_key=True)
    Id_user = Column(Integer)
    Name_sound = Column(String)
    Path = Column(String)

Base.metadata.create_all(engine)
