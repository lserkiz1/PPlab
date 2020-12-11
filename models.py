import os

from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    String,
    BigInteger,
    DateTime,
    Binary,
    func,
)
from sqlalchemy import orm
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session


DB_URI = os.getenv("DB_URI", "postgres://postgres:123456@localhost:5432/basad")
engine = create_engine(DB_URI)
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

BaseModel = declarative_base()


class Users(BaseModel):
    __tablename__ = "users"

    uid = Column(Integer, primary_key=True)
    email = Column(String)
    password = Column(Binary)
    first_name = Column(String)
    last_name = Column(String)


class calendar(BaseModel):
    __tablename__ = "calendar"

    uid = Column(Integer, primary_key=True)
    name = Column(String)
    case = Column(BigInteger)
    owner_uid = Column(Integer, ForeignKey(Users.uid))

    owner = orm.relationship(Users, backref="calendar", lazy="joined")


class events(BaseModel):
    __tablename__ = "events"

    uid = Column(Integer, primary_key=True)
    from_calendar_uid = Column(Integer, ForeignKey(calendar.uid))
    to_calendar_uid = Column(Integer, ForeignKey(calendar.uid))
    tekst = Column(BigInteger)
    datetime = Column(DateTime, server_default=func.now())

    from_calendar = orm.relationship(
        calendar, foreign_keys=[from_calendar_uid], backref="events_from", lazy="joined"
    )
    to_calendar = orm.relationship(
        calendar, foreign_keys=[to_calendar_uid], backref="events_to", lazy="joined"
    )