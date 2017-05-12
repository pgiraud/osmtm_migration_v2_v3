#!env/bin/python
# -*- coding: utf-8 -*-

import sys

from sqlalchemy import (
    create_engine, )
from sqlalchemy.schema import (
    MetaData,
    Table, )
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

if len(sys.argv) < 3:
    print("Usage: %s postgresql://tm2user:pwd@localhost/tm2db "
          "postgresql://tm3user:pwd@localhost/tm3db" % sys.argv[0])
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


def reflect_table_to_declarative(metadata, tablename):
    """Reflects the table to declarative
    """
    Base = declarative_base()
    Base.metadata = metadata

    metadata.reflect()

    tableobj = Table(tablename, metadata, autoload=True)
    return type(str(tablename), (Base, ), {'__table__': tableobj})


# Print iterations progress
def printProgressBar(iteration,
                     total,
                     prefix='',
                     suffix='',
                     decimals=1,
                     length=100,
                     fill='█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(
        100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()


# v2
engine_v2 = create_engine(tm2_url)
metadata_v2 = MetaData(bind=engine_v2)
s2 = sessionmaker(bind=engine_v2)()
users_v2 = Table('users', metadata_v2, autoload=True)
projects_v2 = Table('project', metadata_v2, autoload=True)
licenses_v2 = Table('licenses', metadata_v2, autoload=True)
areas_v2 = Table('areas', metadata_v2, autoload=True)
priority_area_v2 = Table('priority_area', metadata_v2, autoload=True)
project_priority_areas_v2 = Table(
    'project_priority_areas', metadata_v2, autoload=True)
header('Connect to v2')
success('Connected to v2')

# v3
engine_v3 = create_engine(tm3_url)
metadata_v3 = MetaData(bind=engine_v3)
s3 = sessionmaker(bind=engine_v3)()
User = reflect_table_to_declarative(metadata_v3, 'users')
Project = reflect_table_to_declarative(metadata_v3, 'projects')
License = reflect_table_to_declarative(metadata_v3, 'licenses')
AreaOfInterest = reflect_table_to_declarative(metadata_v3, 'areas_of_interest')
PriorityArea = reflect_table_to_declarative(metadata_v3, 'priority_areas')
project_priority_areas_v3 = Table('project_priority_areas', metadata_v3)
header('Connect to v3')
success('Connected to v3')

header('Cleaning up db')
project_priority_areas_v3.delete().execute()
for c in [Project, License, AreaOfInterest, PriorityArea, User]:
    s3.query(c).delete()
s3.commit()
success('Cleaned up')

#
# Users
#
count = users_v2.count().scalar()
header('Importing %s users' % count)
i = 0
for user_v2 in s2.query(users_v2):
    user = User()
    user.id = user_v2.id
    user.role = 0
    user.username = user_v2.username
    user.mapping_level = 1
    user.tasks_mapped = 0
    user.tasks_validated = 0
    user.tasks_invalidated = 0
    s3.add(user)
    i += 1
    printProgressBar(i, count, prefix='Progress:', suffix='Complete', length=50)
s3.commit()

#
# Licenses
#
count = licenses_v2.count().scalar()
header('Importing %s licenses' % count)
i = 0
for license_v2 in s2.query(licenses_v2):
    license = License()
    license.id = license_v2.id
    s3.add(license)
    i += 1
    printProgressBar(i, count, prefix='Progress:', suffix='Complete', length=50)
s3.commit()

#
# Areas of interest
#
count = areas_v2.count().scalar()
header('Importing %s AOI' % count)
i = 0
for aoi_v2 in s2.query(areas_v2):
    aoi = AreaOfInterest()
    aoi.id = aoi_v2.id
    aoi.geometry = aoi_v2.geometry
    s3.add(aoi)
    i += 1
    printProgressBar(i, count, prefix='Progress:', suffix='Complete', length=50)

    # TODO: compute centroid
s3.commit()

#
# Priority Areas
#
count = priority_area_v2.count().scalar()
header('Importing %s priority areas' % count)
i = 0
for pa_v2 in s2.query(priority_area_v2):
    pa = PriorityArea()
    pa.id = pa_v2.id
    s3.add(pa)
    i += 1
    printProgressBar(i, count, prefix='Progress:', suffix='Complete', length=50)
s3.commit()

#
# Projects
#
count = projects_v2.count().scalar()
header('Importing %s projects' % count)
i = 0
for project_v2 in s2.query(projects_v2):
    project = Project()
    project.id = project_v2.id
    project.status = project_v2.status
    project.aoi_id = project_v2.area_id
    project.created = project_v2.created
    project.priority = project_v2.priority
    project.default_locale = 'en'  # FIXME
    project.author_id = project_v2.author_id \
        if project_v2.author_id is not None else 24529
    project.mapper_level = 0
    project.enforce_mapper_level = False
    project.enforce_validator_role = False

    project.private = project_v2.private
    project.entities_to_map = project_v2.entities_to_map
    project.changeset_comment = project_v2.changeset_comment
    project.due_date = project_v2.due_date
    project.imagery = project_v2.imagery
    project.josm_preset = project_v2.josm_preset
    project.last_updated = project_v2.last_update
    project.license_id = project_v2.license_id

    # Stats
    project.total_tasks = 0
    project.tasks_mapped = 0
    project.tasks_validated = 0
    project.tasks_bad_imagery = 0

    s3.add(project)
    i += 1
    printProgressBar(i, count, prefix='Progress:', suffix='Complete', length=50)
s3.commit()

#
# Project priority areas relation table
#
count = project_priority_areas_v2.count().scalar()
header('Linking projects and priority areas')
i = 0


# See http://docs.sqlalchemy.org/en/latest/faq/performance.html#i-m-inserting-400-000-rows-with-the-orm-and-it-s-really-slow
engine_v3.execute(
    project_priority_areas_v3.insert(),
    [{
        'project_id': ppa_v2.project_id,
        'priority_area_id': ppa_v2.priority_area_id
    } for ppa_v2 in s2.query(project_priority_areas_v2)]
)
s3.commit()
