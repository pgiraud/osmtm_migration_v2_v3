osmtm_v2_migration
==================

Script to migrate HOT Tasking Manager v2 data to v3

Usage
-----

Activate the v3 virtual env:

```
source /path/to/tasking/manager/venv/bin/activate
```

Then you can use the migration script as follows:

```
python migrate.py postgresql://tm2user:pwd@localhost/tm2db postgresql://tm3user:pwd@localhost/tm3db
```
