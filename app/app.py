import os

from dotenv import load_dotenv
from flask import Flask

from db import close_database
import customer
import vehicle
import rental
import availabilty
import report


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

    app.register_blueprint(customer.bp)
    app.register_blueprint(vehicle.bp)
    app.register_blueprint(rental.bp)
    app.register_blueprint(report.bp)

    return app
