#!/usr/bin/env python3
import glob
import os
import string
import xml.etree.ElementTree as ET

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Entry(Base):
    __tablename__ = 'entries'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    entry = sqlalchemy.Column(sqlalchemy.String)

    # Original file is used to reconstruct the files. Some entries like "a continuació" are in "c.dic" not "a.dic"
    original_file = sqlalchemy.Column(sqlalchemy.String)
    xml = sqlalchemy.Column(sqlalchemy.Text)

    def __str__(self):
        return f'{self.entry}'


def create_database_session():
    file_name = 'dacco.db'
    try:
        os.unlink(file_name)
    except FileNotFoundError:
        pass

    engine = sqlalchemy.create_engine(f'sqlite:///{file_name}')

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    return session


def dacco_file_to_db(file_path, db_session):
    tree = ET.parse(file_path)

    for element in tree.findall('.//Entry'):
        xml = ET.tostring(element, encoding='utf-8').decode('utf-8')
        original_file = file_path.split('/')[-1]
        entry = Entry(entry=element.text, original_file=original_file, xml=xml)
        db_session.add(entry)

        # for translation in element.findall('.//translation'):
        #     print('translation text:', translation.text)

    db_session.commit()


def dacco_directory_to_db(directory, session):
    for file in glob.glob(os.path.join(directory, '*.dic')):
        dacco_file_to_db(file, session)


def generate_output_for_letter(output_directory, letter, session):
    result = session.query(Entry).filter(Entry.original_file.ilike(f'{letter}.dic')).order_by(Entry.id)
    file_name = f'{letter}.dic'
    with open(os.path.join(output_directory, file_name), 'w') as f:
        if file_name == 'a.dic':
            # a.dic in cateng has a different header
            f.write('''<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE dictionary SYSTEM "dic.dtd">
            <dictionary xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="file:///C:/Documents%20and%20Settings/James/My%20Documents/My%20Projects/dacco%20projects/Publisher/input/cateng/dic.xsd">\n''')
        else:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<dictionary>\n')

        for row in result:
            f.write(row.xml)

        f.write('</dictionary>')


def generate_output(output_directory, session):
    os.makedirs(output_directory, exist_ok=True)

    for letter in string.ascii_lowercase:
        generate_output_for_letter('/tmp/cateng', letter, session)


def main():
    session = create_database_session()
    output_directory = '/tmp/cateng'

    for letter in string.ascii_lowercase:
        dacco_file_to_db(f'/usr/share/dacco-common/dictionaries/cateng/{letter}.dic', session)

    generate_output(output_directory, session)

    print('See sqlite file in dacco.db')
    print(f'See output of XMLs after the SQL in {output_directory}')
    print('Execute unit test with python3 test_dacco-to-db.py')


if __name__ == '__main__':
    main()
