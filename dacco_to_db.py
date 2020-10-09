#!/usr/bin/env python3
import glob
import os
import shutil
import string
import subprocess
import tempfile
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


def canonical_xml(file1):
    with subprocess.Popen(['xsec-c14n', '-n', file1], stdout=subprocess.PIPE) as proc:
        canonicalized = proc.stdout.read()
        canonicalized = canonicalized.decode('utf-8')

        # For some reason the canonicalizatio process is not fixing these differences (!)
        canonicalized = canonicalized.replace('     <Entry frequency="101">babaganuix<nouns>',
                                              '<Entry frequency="101">babaganuix<nouns>')

        canonicalized = canonicalized.replace('    <Entry frequency="2780">dacsa<nouns>',
                                              '<Entry frequency="2780">dacsa<nouns>')

        canonicalized = canonicalized.replace('    <Entry frequency="2040">eben<nouns>',
                                              '<Entry frequency="2040">eben<nouns>')

        canonicalized = canonicalized.replace('    <Entry frequency="71200">laberint<nouns>',
                                              '<Entry frequency="71200">laberint<nouns>')

        canonicalized = canonicalized.replace(' <Entry frequency="218">nabiu<nouns>',
                                              '<Entry frequency="218">nabiu<nouns>')

        canonicalized = canonicalized.replace('     <Entry frequency="199">qatarià<nouns>',
                                              '<Entry frequency="199">qatarià<nouns>')

        canonicalized = canonicalized.replace('  <Entry frequency="24400">tabac<nouns>',
                                              '<Entry frequency="24400">tabac<nouns>')

        canonicalized = canonicalized.replace('        <Entry frequency="154">xacal<nouns>',
                                              '<Entry frequency="154">xacal<nouns>')

        canonicalized = canonicalized.replace('''<dictionary>
	
</dictionary>
''', '''<dictionary>\n</dictionary>\n''')

        canonicalized = canonicalized.replace('\t<Entry frequency="',
                                              '<Entry frequency="')

        return canonicalized


def compare_xml_files(file1, file2):
    shutil.copy('/usr/share/dacco-common/dictionaries/cateng/dic.dtd', '/tmp/cateng')
    canonical_xml_file1 = canonical_xml(file1)
    canonical_xml_file2 = canonical_xml(file2)

    same_result = (canonical_xml_file1 == canonical_xml_file2)
    if same_result:
        return True
    else:
        tempfile1 = tempfile.NamedTemporaryFile(delete=False, suffix=file1.replace('/', '_'), mode='w')
        tempfile2 = tempfile.NamedTemporaryFile(delete=False, suffix=file2.replace('/', '_'), mode='w')

        tempfile1.write(canonical_xml_file1)
        tempfile2.write(canonical_xml_file2)

        print('files are not the same. Compare the canonicalized files:')
        print(tempfile1.name)
        print(tempfile2.name)
        print(f'vimdiff {tempfile1.name} {tempfile2.name}')

        return False


if __name__ == '__main__':
    main()
