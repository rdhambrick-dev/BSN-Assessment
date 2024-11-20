from flask import Blueprint, request, abort

from db import get_database
from rental import Rental

bp = Blueprint("report", __name__, url_prefix="/report")


class ReportRental:
    def __init__(self, vehicle_category, customer_name, customer_phone, customer_address,
                 customer_email, rental_id, vehicle_id, customer_id, pickup_date, return_date):
        self.vehicle_category = vehicle_category
        self.customer_name = customer_name
        self.customer_phone = customer_phone
        self.customer_address = customer_address
        self.customer_email = customer_email
        self.rental_id = rental_id
        self.vehicle_id = vehicle_id
        self.customer_id = customer_id
        self.pickup_date = pickup_date
        self.return_date = return_date

    def dict(self):
        return {
            "customer": {
                "id": self.customer_id,
                "name": self.customer_name,
                "phone": self.customer_phone,
                "address": self.customer_address,
                "email": self.customer_email
            },
            "vehicle": {
                "id": self.vehicle_id,
                "category": self.vehicle_category
            },
            "rental": {
                "id": self.rental_id,
                "pickup_date": self.pickup_date.strftime(Rental.DATE_FORMAT),
                "return_date": self.return_date.strftime(Rental.DATE_FORMAT)
            }
        }


@bp.get("/")
def get_report():
    request_data = request.get_json()

    if "date" not in request_data:
        abort(400, description="Missing report date.")

    query = ("SELECT "
             "vehicle.category, "
             "customer.name, customer.phone, customer.address, customer.email, "
             "rental.id, rental.vehicle_id, rental.customer_id, rental.pickup_date, rental.return_date "
             "FROM rental "
             "CROSS JOIN vehicle ON rental.vehicle_id = vehicle.id "
             "CROSS JOIN customer ON rental.customer_id = customer.id "
             "WHERE %(date)s BETWEEN rental.pickup_date AND rental.return_date ")
    if "category" in request_data:
        query += "AND vehicle.category = %(category)s "

    cursor = get_database().cursor()
    cursor.execute(query, request_data)
    rentals = cursor.fetchall()

    return [ReportRental(*rental).dict() for rental in rentals]
