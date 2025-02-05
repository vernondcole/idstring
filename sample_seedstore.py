#!/usr/bin/env python
"""
Test code for the IDstring package
"""
__author__ = 'vernon'

import sqlite3
from typing import Union
from idstring.idstring import IDstring


DB_FILE_NAME = 'test_idstring_sqlite.db'
DB_TABLE_NAME = 'the_list'
DB_NEXT_ID_TABLE = 'next_id'
ID_FIELD_NAME = 'his_id'
FIRST_SEED_VALUE = '0'

# *** GENERAL NOTE -- I am using Python string functions to build SQL statements in places where
# *** SQL injection attacks are unlikely, since the values used come only from within this program.
# *** Paramaterized queries are used for other data values which may not be wholly reliable.

def next_id(conn):
    """ return the next available id value """
    # 1) Get the current (last) ID value from a 1-row table in the database
    cur = conn.cursor()
    cur.execute(f"SELECT saved_id FROM {DB_NEXT_ID_TABLE} WHERE only_id = 1")
    present_value = cur.fetchone()[0]

    # notice: we pass the save_id function to IDstring instance.
    # it will recurse, if needed, in case of a collision
    id = IDstring(present_value, seedstore=save_id, context={'conn': conn})

    # retain that value in the object, for concurrency checking later
    id.context['memory'] = str(id)

    cur.close()
    # 2) create a new ID each time called
    while ...:
        id += 1  # NOTE: the + operation calls seedstore(). It may recurse the +1 operation.
        yield id


def save_id(id: IDstring) -> Union[None, IDstring]:
    """ store the current seed value in the one-row database table
    if the input IDstring is invalid (already used) then generate a good one.
    """
    ret = None  # default value, used when the input id was valid
    cur = id.context['conn'].cursor()
    seedstore_memory = id.context['memory']
    # try to store the new value, using the last memorized value as a look up.
    cur.execute(f"UPDATE {DB_NEXT_ID_TABLE} SET saved_id = ? WHERE only_id = 1 and saved_id = ?",
                [id, seedstore_memory])
    # if all went well, the new value will have been stored.
    if cur.rowcount != 1:  # arrrgh! someone else must have stored a value.
        conn.rollback()  # forget that we tried a change
        # get the new last value
        cur.execute(f"SELECT saved_id FROM {DB_NEXT_ID_TABLE} WHERE only_id = 1")
        saved_id_str = cur.fetchone()[0]
        saved_id = IDstring(id, seed=saved_id_str)  # will raise InvalidIdError if corrupt
        saved_id.context['memory'] = saved_id_str
        # increment the new last value to get our new value
        saved_id += 1  # recursive call. Will store the new new value inside.
        ret = saved_id  # return the (new valid) updated ID
    else:
        conn.commit()  # save the good change
    cur.close()
    return ret  # will be used by IDsring.__add__() if not None


def init_db(conn):
    # ## create samplet tables if they do not already exist
    sql_create_main_table = f"CREATE TABLE IF NOT EXISTS {DB_TABLE_NAME} (entity_name TEXT, {ID_FIELD_NAME} TEXT);"
    cur = conn.cursor()
    cur.execute(sql_create_main_table)
    cur.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' and name='{DB_NEXT_ID_TABLE}'")
    count = cur.fetchone()[0]
    if count == 0:  # the table does not yet exist
        c = conn.cursor()
        cur.execute(f"CREATE TABLE {DB_NEXT_ID_TABLE} (only_id int, saved_id TEXT UNIQUE NOT NULL)")
        first_value = IDstring(seed=FIRST_SEED_VALUE)
        cur.execute(f"INSERT INTO {DB_NEXT_ID_TABLE} VALUES (1, '{first_value}')")
        c.close()
        conn.commit()


# try running this from multiple terminals to watch it bumping the serial number for each one.
if __name__ == '__main__':
    conn = sqlite3.connect(DB_FILE_NAME)

    # create sample tables if they do not exist.
    init_db(conn)

    # get a new ID from the factory
    id = next(next_id(conn))
    print(f'the next available ID was {id}')
    # make up a new client name
    funny_name = f"Elmer Fudd ({id.seed})"
    cur = conn.cursor()
    # store the now data into the main data table
    sql_main_insert = f"INSERT INTO {DB_TABLE_NAME} VALUES (?, ?)"
    cur.execute(sql_main_insert, [funny_name, id])
    cur.close()
    conn.commit()
    conn.close()
