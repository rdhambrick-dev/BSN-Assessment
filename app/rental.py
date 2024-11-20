from datetime import datetime, timedelta

from flask import Blueprint, request, abort

from db import get_database

bp = Blueprint("rental", __name__, url_prefix="/rentals")


class Rental:
    DATE_FORMAT = "%Y-%m-%d"

    def __init__(self, id, vehicle_id, customer_id, pickup_date, return_date):
        self.id = id
        self.vehicle_id = vehicle_id
        self.customer_id = customer_id
        self.pickup_date = pickup_date
        self.return_date = return_date

        if isinstance(self.pickup_date, str):
            self.pickup_date = datetime.strptime(self.pickup_date, Rental.DATE_FORMAT)

        if isinstance(self.return_date, str):
            self.return_date = datetime.strptime(self.return_date, Rental.DATE_FORMAT)

    def dict(self):
        return {
            "id": self.id,
            "vehicle_id": self.vehicle_id,
            "customer_id": self.customer_id,
            "pickup_date": self.pickup_date.strftime(Rental.DATE_FORMAT),
            "return_date": self.return_date.strftime(Rental.DATE_FORMAT)
        }


def validate_rental_dates(pickup_date: str, return_date: str):
    today = datetime.today().date()
    if not pickup_date:
        abort(400, description="Missing pickup date.")
    if not return_date:
        abort(400, description="Missing return date.")

    try:
        pickup_date = datetime.strptime(pickup_date, Rental.DATE_FORMAT).date()
        return_date = datetime.strptime(return_date, Rental.DATE_FORMAT).date()
    except (TypeError, ValueError):
        abort(400, description="Invalid date. Accepted format: YYYY-MM-DD")

    if pickup_date < today:
        abort(400, description="Pickup date cannot be in the past.")
    if pickup_date > today + timedelta(weeks=1):
        abort(400, description="Reservation cannot be made more than one week in advance.")
    if return_date > pickup_date + timedelta(weeks=1):
        abort(400, description="Reservation cannot be longer than one week.")
    if pickup_date > return_date:
        abort(400, description="Return date cannot be before pickup date.")


@bp.post("/")
def create_rental():
    request_data = request.get_json()
    rental_data = {
        "vehicle_id": request_data.get("vehicle_id"),
        "customer_id": request_data.get("customer_id"),
        "pickup_date": request_data.get("pickup_date"),
        "return_date": request_data.get("return_date")
    }

    validate_rental_dates(rental_data["pickup_date"], rental_data["return_date"])

    # TODO prevent rental creation if vehicle is already rented during requested dates

    database = get_database()
    cursor = database.cursor()
    cursor.execute(
        "INSERT INTO rental "
        "(vehicle_id, customer_id, pickup_date, return_date) "
        "VALUES (%(vehicle_id)s, %(customer_id)s, %(pickup_date)s, %(return_date)s)",
        rental_data
    )
    new_rental_id = cursor.lastrowid
    database.commit()

    new_rental = Rental(new_rental_id, **rental_data)

    # todo send an invoice to user via email
    # todo send confirmation email to user if reservation is made in advance

    return new_rental.dict(), 201


@bp.get("/<int:id>")
def get_rental(id):
    cursor = get_database().cursor()
    cursor.execute(
        "SELECT * FROM rental WHERE id = %s",
        [id]
    )

    rental = cursor.fetchone()
    if not rental:
        abort(404, description=f"Rental with id {id} not found.")
    return Rental(*rental).dict()


@bp.get("/")
def get_all_rentals():
    cursor = get_database().cursor()
    cursor.execute("SELECT * FROM rental")
    return [Rental(*rental).dict() for rental in cursor.fetchall()]


@bp.route("/<int:id>", methods=["PUT", "PATCH"])
def update_rental(id):
    database = get_database()
    cursor = database.cursor()
    cursor.execute(
        "SELECT * FROM rental WHERE id = %s",
        [id]
    )

    existing_rental = cursor.fetchone()
    if not existing_rental:
        abort(404, description=f"Rental with id {id} not found.")

    existing_rental = Rental(*existing_rental)

    request_data = request.get_json()
    if request.method == "PATCH":
        new_rental_data = {
            "id": id,
            "vehicle_id": request_data.get("vehicle_id", existing_rental.vehicle_id),
            "customer_id": request_data.get("customer_id", existing_rental.customer_id),
            "pickup_date": request_data.get("pickup_date", existing_rental.pickup_date),
            "return_date": request_data.get("return_date", existing_rental.return_date)
        }
    else:  # request.method == "POST"
        new_rental_data = {
            "id": id,
            "vehicle_id": request_data.get("vehicle_id"),
            "customer_id": request_data.get("customer_id"),
            "pickup_date": request_data.get("pickup_date"),
            "return_date": request_data.get("return_date")
        }

    validate_rental_dates(new_rental_data["pickup_date"], new_rental_data["return_date"])

    # TODO prevent rental update if vehicle is already reserved during requested dates (by another rental)

    cursor.execute(
        "UPDATE rental SET "
        "vehicle_id = %(vehicle_id)s, "
        "customer_id = %(customer_id)s, "
        "pickup_date = %(pickup_date)s, "
        "return_date = %(return_date)s "
        "WHERE id = %(id)s",
        new_rental_data
    )
    database.commit()

    new_rental = Rental(**new_rental_data)
    return new_rental.dict()


@bp.delete("/<int:id>")
def delete_rental(id):
    database = get_database()
    cursor = database.cursor()
    cursor.execute(
        "DELETE FROM rental WHERE id = %s",
        [id]
    )
    database.commit()
    return {}, 204
