import os

from dotenv import load_dotenv
from flask import Flask

from db import close_database


def create_app():
    load_dotenv()
    app = Flask(__name__)

    app.config["DATABASE"] = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": "bsn"
    }

    app.teardown_appcontext(close_database)

    return app
