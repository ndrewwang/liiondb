
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import matplotlib as plt

def sqlalchemy_connect(db_connection):
    
    postgres_str = ('postgresql://{username}:{password}@{ipaddress}:{port}/{dbname}'
       .format(username=db_connection['username'],
               password=db_connection['password'],
               ipaddress=db_connection['address'],
               port=db_connection['port'],
               dbname=db_connection['dbname']))
    dfndb = create_engine(postgres_str)
    db_connection['dbobject']=dfndb
    return db_connection

def list_tables(db_connection):
    dfndb = db_connection['dbobject']
    output = pd.read_sql('''SELECT tablename
    FROM pg_catalog.pg_tables
    WHERE schemaname != 'pg_catalog'
    AND schemaname != 'information_schema';''',dfndb)
    return output
    
def get_connection(db_connection):
    connection = psycopg2.connect(user = db_connection['username'],
                                      password = db_connection['password'],
                                      host = db_connection['address'],
                                      port = db_connection['port'],
                                      database = db_connection['dbname'])

    return connection

def close_connection(connection):
    if connection:
        connection.close()
        print("Postgres connection is closed")
    
    
def drop_all_tables(db_connection):
    try:
        connection = get_connection(db_connection)
        cursor = connection.cursor()

        query = '''DROP SCHEMA public CASCADE; 
                CREATE SCHEMA public;'''

        cursor.execute(query)
        connection.commit()
        print("All tables dropped")

    except (Exception, psycopg2.DatabaseError) as error :
        print ("Error while dropping tables", error)
    finally:
        close_connection(connection)
                
def create_table(query, db_connection):
    try:
        connection = get_connection(db_connection)
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        print("Table created successfully in PostgreSQL ")


    except (Exception, psycopg2.DatabaseError) as error :
        print ("Error while creating PostgreSQL table", error)
    finally:
        close_connection(connection)
        
        
def postgres_query(query,param,db_connection):
    try:
        connection = get_connection(db_connection)
        cursor = connection.cursor()
        cursor.execute(query,param)
        connection.commit()
        print("Query successfully executed in PostgreSQL ")

    except (Exception, psycopg2.DatabaseError) as error :
        print ("Error while executing PostgreSQL query", error)
    finally:
        close_connection(connection)
