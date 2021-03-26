# everstone

A simple database query generator.


### This project is still in active develpment and is not ready of usage.

## Installation
```sh
pip install everstone
```

**Requires Python 3.9.0+**

## Usage

### Connecting a Database
```py
from everstone import db

db.connect("test_database", "user_one", "abcd5432")
```

### Creating a Schema:

```python
from everstone import db

auth_schema = db.Schema("auth")
await auth_schema.create()
```
#### Resulting SQL
```sql
CREATE TABLE user (user_id INTEGER PRIMARY KEY, name TEXT);
```

### Creating a Table:

```py
from everstone import constraints, db, types
from everstone import Column
user_table = db.Table("user")
user_table.add_columns(
    Column("user_id", types.Integer, constraints.PrimaryKey),
    Column("name", types.Text)
)
await user_table.create()
```
#### Resulting SQL
```sql
CREATE TABLE user (user_id INTEGER PRIMARY KEY, name TEXT);
```
