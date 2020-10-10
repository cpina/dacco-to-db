#!/usr/bin/env python3
import argparse
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


def delete_database(db_file_path):
    file_name = db_file_path
    try:
        os.unlink(file_name)
    except FileNotFoundError:
        pass


def open_database(db_file_path):
    engine = sqlalchemy.create_engine(f'sqlite:///{db_file_path}')

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
        generate_output_for_letter(output_directory, letter, session)


# def main():
#     session = open_database()
#     output_directory = '/tmp/cateng'
#
#     for letter in string.ascii_lowercase:
#         dacco_file_to_db(f'/usr/share/dacco-common/dictionaries/cateng/{letter}.dic', session)
#
#     generate_output(output_directory, session)
#
#     print('See sqlite file in dacco.db')
#     print(f'See output of XMLs after the SQL in {output_directory}')
#     print('Execute unit test with python3 test_dacco-to-db.py')


def xml_to_db(xml_directory_path, db_destination_path):
    delete_database(db_destination_path)
    session = open_database(db_destination_path)

    for letter in string.ascii_lowercase:
        file = os.path.join(xml_directory_path, 'cateng', f'{letter}.dic')
        dacco_file_to_db(file, session)


def db_to_xml(db_source_path, xml_directory_path):
    session = open_database(db_source_path)

    generate_output(xml_directory_path, session)


if __name__ == '__main__':
    main_parser = argparse.ArgumentParser()

    subparsers = main_parser.add_subparsers(dest='action', required=True)

    xml_to_db_parser = subparsers.add_parser('xml-to-db')
    xml_to_db_parser.add_argument('--xml-directory',
                                  help='Directory to read the DACCO XML files from. Defaults to /usr/share/dacco-common/dictionaries/',
                                  default='/usr/share/dacco-common/dictionaries/')
    xml_to_db_parser.add_argument('db_destination',
                                  help='sqlite3 filename where the output will be saved to. It is overwritten')

    db_to_xml_parser = subparsers.add_parser('db-to-xml')
    db_to_xml_parser.add_argument('db', help='sqlite3 filename of the database to output')
    db_to_xml_parser.add_argument('output_directory', help='Directory where the files will be saved')

    args = main_parser.parse_args()

    if args.action == 'xml-to-db':
        xml_to_db(args.xml_directory, args.db_destination)
    elif args.action == 'db-to-xml':
        db_to_xml(args.db, args.output_directory)
