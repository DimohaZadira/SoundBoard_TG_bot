from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from tg_bot.config import load_config

config = load_config(".env")
engine = create_engine(
    f"postgresql+psycopg2://{config.db.user}:{config.db.password}@{config.db.host}/{config.db.name}"
)
Session = sessionmaker()
session = Session(bind=engine)

Base = declarative_base()


class Files(Base):
    __tablename__ = "files"
    Id = Column(Integer, primary_key=True)
    Id_user = Column(Integer)
    Id_audio = Column(String)
    Date_genering_id = Column(DateTime)
    Name_sound = Column(String)
    Path = Column(String)
    Size_audio = Column(Integer)


Base.metadata.create_all(engine)
