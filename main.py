#!/usr/bin/env python3
import os

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import xml.dom.minidom
import xml.etree.ElementTree as ET

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
    print(f'Created file {file_name}')

    Base.metadata.create_all(engine)

    return engine


def dacco_file_to_db(file_path, db_session):
    tree = ET.parse(file_path)

    for element in tree.findall('.//Entry'):
        for translation in element.findall('.//translation'):
            entry = Entry(word=element.text, translation=translation.text)
            db_session.add(entry)

    db_session.commit()
    print(f'file {file_path} inserted into {db_session.bind.url}')


def main():
    engine = create_database()

    Session = sessionmaker(bind=engine)
    session = Session()

    entry = Entry(word='núvol', translation='cloud')
    session.add(entry)
    session.commit()

    dacco_file_to_db('/usr/share/dacco-common/dictionaries/cateng/a.dic', session)


if __name__ == '__main__':
    main()
