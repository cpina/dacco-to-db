#!/usr/bin/env python3
import os
import shutil
import string
import subprocess
import tempfile
import unittest

from parameterized import parameterized

import dacco_to_db


class TestDacco_to_db(unittest.TestCase):
    def setUp(self):
        self._temporary_directory = tempfile.TemporaryDirectory(prefix='dacco_to_db')

    @parameterized.expand(string.ascii_lowercase)
    def test_generate_output(self, letter):
        db_file = tempfile.NamedTemporaryFile(delete=False)
        db_file.close()

        session = dacco_to_db.open_database(db_file.name)

        file_name = f'{letter}.dic'
        dacco_to_db.dacco_file_to_db(f'/usr/share/dacco-common/dictionaries/cateng/{file_name}', session)

        dacco_to_db.generate_output_for_letter(self._temporary_directory.name, letter, session)

        self.assertTrue(compare_dacco_file_to_generated(f'/usr/share/dacco-common/dictionaries/cateng/{file_name}',
                                                        os.path.join(self._temporary_directory.name, file_name)))


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
\t
</dictionary>
''', '''<dictionary>\n</dictionary>\n''')

        canonicalized = canonicalized.replace('\t<Entry frequency="',
                                              '<Entry frequency="')

        return canonicalized


def compare_dacco_file_to_generated(dacco_file, generated_file):
    base_dacco_directory, _ = os.path.split(dacco_file)
    base_destination_directory, _ = os.path.split(generated_file)

    shutil.copy(os.path.join(base_dacco_directory, 'dic.dtd'), base_destination_directory)
    return compare_xml_files(dacco_file, generated_file)


def compare_xml_files(file1, file2):
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
    unittest.main()
