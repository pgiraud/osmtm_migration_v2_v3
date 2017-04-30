#!env/bin/python
# -*- coding: utf-8 -*-

import sys

from sqlalchemy import (
    create_engine,
)
from sqlalchemy.schema import MetaData
from sqlalchemy.orm import sessionmaker

if len(sys.argv) < 3:
    print("Usage: %s postgresql://tm2user:pwd@localhost/tm2db postgresql://tm3user:pwd@localhost/tm3db" % sys.argv[0])  # noqa
    sys.exit(2)

tm2_url = sys.argv[1]
tm3_url = sys.argv[2]


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def header(msg):
    print(bcolors.HEADER + "# " + msg + bcolors.ENDC)


def success(msg):
    print(bcolors.OKGREEN + msg + bcolors.ENDC)


def failure(msg):
    print(bcolors.FAIL + msg + bcolors.ENDC)


# v2
metadata_v2 = MetaData()
engine_v2 = create_engine(tm2_url)
session_v2 = sessionmaker(bind=engine_v2)()
metadata_v2.reflect(bind=engine_v2)
projects_v2 = metadata_v2.tables['project']
header('Connect to v2')

# v3
metadata_v3 = MetaData()
engine_v3 = create_engine(tm2_url)
session_v3 = sessionmaker(bind=engine_v3)()
metadata_v3.reflect(bind=engine_v3)
projects_v3 = metadata_v3.tables['projects']
header('Connect to v3')


header("Importing projects")
for project_v2 in session_v2.query(projects_v2):
    project = Project()
    project.created = project_v2.created
    session_v3.add(project)

