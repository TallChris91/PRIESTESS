import os
import sqlite3
import sys
import time
import regex as re
import random

def create_project(conn, project):
    # create table
    sql = '''CREATE TABLE participantnumbers (participantnumber)'''
    insert = '''INSERT INTO participantnumbers (participantnumber) VALUES(?)'''

    cur = conn.cursor()
    cur.execute(sql)
    cur.execute(insert, (project,))


def extend_project(conn, project):
    sql = '''INSERT INTO participantnumbers (participantnumber) VALUES(?)'''
    cur = conn.cursor()
    #Try to find out whether the table exists
    cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='participantnumbers' ''')
    #If it does, add new entry to the table
    if cur.fetchone()[0] == 1:
        while True:
            try:
                cur.execute(sql, (project,))
                break
            except sqlite3.OperationalError:
                time.sleep(1)
    #If it does not, create the table
    else:
        create_project(conn, project)


def database_main(db, dbinfo):
    if os.path.exists(db) == True:
        # create a database connection
        with sqlite3.connect(db) as conn:
            # extend the project
            extend_project(conn, dbinfo)
    else:
        with sqlite3.connect(db) as conn:
            create_project(conn, dbinfo)

def database_search(db, searchword):
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()

        # Try to find out whether the table exists
        cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='participantnumbers' ''')
        # If it does, add new entry to the table
        if cur.fetchone()[0] == 0:
            return 'notFound'

        while True:
            try:
                cur.execute("SELECT * FROM participantnumbers WHERE participantnumber = ?", (searchword,))
                break
            except sqlite3.OperationalError:
                time.sleep(1)
        data = cur.fetchone()
        if data is None:
            return 'notFound'
        else:
            return data[0]




