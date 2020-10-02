#!/usr/bin/env python3
import os

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Entry(Base):
    __tablename__ = 'entries'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    word = sqlalchemy.Column(sqlalchemy.String)
    translation = sqlalchemy.Column(sqlalchemy.String)

    def __str__(self):
        return f'{self.word}'


def create_database():
    file_name = 'dacco.db'
    try:
        os.unlink(file_name)
    except FileNotFoundError:
        pass

    engine = sqlalchemy.create_engine(f'sqlite:///{file_name}')

    Base.metadata.create_all(engine)

    return engine


def main():
    engine = create_database()

    Session = sessionmaker(bind=engine)
    session = Session()

    entry = Entry(word='núvol', translation='cloud')
    session.add(entry)
    session.commit()


if __name__ == '__main__':
    main()
