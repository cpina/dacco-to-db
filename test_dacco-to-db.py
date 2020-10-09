#!/usr/bin/env python3
import string
import unittest

from parameterized import parameterized

import dacco_to_db


class TestDacco_to_db(unittest.TestCase):
    @parameterized.expand(string.ascii_lowercase)
    def test_generate_output(self, letter):
        session = dacco_to_db.create_database_session()
        file_name = f'{letter}.dic'
        dacco_to_db.dacco_file_to_db(f'/usr/share/dacco-common/dictionaries/cateng/{file_name}', session)

        dacco_to_db.generate_output_for_letter('/tmp/cateng', letter, session)

        self.assertTrue(dacco_to_db.compare_xml_files(f'/usr/share/dacco-common/dictionaries/cateng/{file_name}',
                                                      f'/tmp/cateng/{file_name}'))


if __name__ == '__main__':
    unittest.main()
