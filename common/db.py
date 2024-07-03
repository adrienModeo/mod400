from datetime import date

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, PrimaryKeyConstraint, String, create_engine, func
from sqlalchemy.orm import declarative_base, sessionmaker
from common.utils import normalize_name

DATABASE_URL = "postgresql://user:password@db:5432/game_db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()


class Game(Base):
    __tablename__ = "game"
    id = Column(Integer, primary_key=True)
    date = Column(Date, default=date.today)


class Player(Base):
    __tablename__ = "player"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)


class Round(Base):
    __tablename__ = "round"
    game_id = Column(Integer, ForeignKey("game.id"))
    round_number = Column(Integer)
    player_id = Column(Integer, ForeignKey("player.id"))
    team = Column(Integer)
    bet = Column(Integer)
    is_win = Column(Boolean)
    score = Column(Integer)

    __table_args__ = (PrimaryKeyConstraint("game_id", "round_number", "player_id"),)


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def get_or_create_player(session, name):
    normalized_name = normalize_name(name)
    player = session.query(Player).filter(func.lower(func.trim(Player.name)) == normalized_name).first()
    if not player:
        player = Player(name=normalized_name)
        session.add(player)
        session.commit()
    return player


def get_all_players():
    session = Session()
    players = session.query(Player.name).all()
    session.close()
    return [player[0] for player in players]
