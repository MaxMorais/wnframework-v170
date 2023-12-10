#!/bin/bash

. ./env/bin/activate
export DB_STORAGE="$(pwd)/data/wnframework.db"

mkdir data
rm $DB_STORAGE
sqlite3 $DB_STORAGE < wnframework/v170/data/Framework-lite.sql
python wnframework/v170/cgi-bin/webnotes/install_lib/install.py admin admin $DB_STORAGE -s wnframework/v170/data/Framework-lite.sql
sqlite3 $DB_STORAGE < wnframework-modules/master-lite.sql
python server.py