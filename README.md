
# dacco-to-db

Playground to read [DACCO XML](https://github.com/cpina/dacco) files and using [SQLAlchemy](https://www.sqlalchemy.org/) to insert them into a database (sqlite currently).

Steps to test:
```sh
git clone git@github.com:cpina/dacco-to-db.git
cd dacco-to-db/
python3 -m virtualenv venv
. venv/bin/activate
python3 -m pip install -r requirements.txt
python3 dacco_to_db.py xml-to-db dacco_in_sqlite.db

# See the result:
sqlitebrowser --table entries dacco_in_sqlite.db

# To re-generate the DACCO files out of the sqlite3 file:
python3 db-to-xml dacco_in_sqlite.db /tmp/dacco_files
```

For the unit tests:
```sh
# For the unit tests
apt install xml-security-c-utils

Execute them:
./test_dacco-to-db.py -v
```
