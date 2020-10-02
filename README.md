
# dacco-to-db

Playground to read [DACCO XML](https://github.com/cpina/dacco) files and using [SQLAlchemy](https://www.sqlalchemy.org/) to insert them into a database (sqlite currently).

Steps to test:
```js
git clone git@github.com:cpina/dacco-to-db.git
cd dacco-to-db/
python3 -m virtualenv venv
. venv/bin/activate
python3 -m pip install -r requirements.txt
python3 main.py

# See the result:
sqlitebrowser --table entries dacco.db
```
