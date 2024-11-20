from flask import current_app, g
from mysql.connector import connection


def get_database():
    if "database" not in g:
        g.database = connection.MySQLConnection(
            **current_app.config.get("DATABASE")
        )
    return g.database


def close_database(err):
    try:
        database = g.pop("database", None)

        if database is not None:
            database.close()
    except:
        print("Failed to close database connection.")
