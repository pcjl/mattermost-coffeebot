from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class BaseModel(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True, autoincrement=True)
    date_created = Column(DateTime, default=func.now())
    date_modified = Column(DateTime, default=func.now(), onupdate=func.now())


Base = declarative_base(cls=BaseModel)


class User(Base):
    __tablename__ = 'users'

    user_id = Column(String, nullable=False, unique=True)
    active = Column(Boolean, default=True, nullable=False)
    is_paired = Column(Boolean, default=False)

    def __repr__(self):
        return '<User {} - {}>'.format(
            self.user_id,
            'Active' if self.active else 'Inactive')


class Pair(Base):
    __tablename__ = 'pairs'

    first_user_id = Column(
        Integer, ForeignKey('users.user_id'))
    first_user = relationship('User', foreign_keys=[first_user_id])

    second_user_id = Column(
        Integer, ForeignKey('users.user_id'))
    second_user = relationship('User', foreign_keys=[second_user_id])

    count = Column(Integer, default=0)

    def __repr__(self):
        return '<Pair {} <-> {} - {}>'.format(
            self.first_user.id, self.second_user.id, self.count)
