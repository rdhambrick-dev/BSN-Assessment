import datetime

from flask import abort, request, Blueprint

from db import get_database
from vehicle import Vehicle
from rental import Rental

bp = Blueprint("availability", __name__, url_prefix="/vehicles")


@bp.get("/<int:id>/availability")
def get_vehicle_availability(id):
    cursor = get_database().cursor()
    cursor.execute(
        "SELECT * FROM vehicle WHERE id = %s",
        [id]
    )

    vehicle = cursor.fetchone()
    if not vehicle:
        abort(404, description=f"Vehicle with id {id} not found.")

    cursor.execute(
        "SELECT pickup_date, return_date FROM rental WHERE vehicle_id = %s",
        [id]
    )
    # TODO optimization: select only rows where reservation overlaps two-week window starting today
    # i.e. (return date >= today and <= 2w) or (pickup date >= today and <= 2w)

    available_dates = {datetime.date.today() + datetime.timedelta(days=i) for i in range(14)}
    for pickup_date, return_date in cursor.fetchall():
        date = pickup_date
        while date <= return_date:
            if date in available_dates:
                available_dates.remove(date)
            date += datetime.timedelta(days=1)

    return sorted(date.strftime(Rental.DATE_FORMAT) for date in available_dates)


@bp.get("/availability")
def get_all_vehicles_availability():
    cursor = get_database().cursor()

    vehicle_category = request.args.get('category')
    query = "SELECT * FROM vehicle "
    if vehicle_category:
        query += "WHERE category = %(category)s"
    cursor.execute(query, request.args)
    all_vehicles = [Vehicle(*vehicle) for vehicle in cursor.fetchall()]

    query = ("SELECT vehicle.id, vehicle.category, pickup_date, return_date "
             "FROM vehicle CROSS JOIN rental ")
    if vehicle_category:
        query += "WHERE vehicle.category = %(category)s"
    rentals = cursor.fetchall()
    # TODO optimization: select only rows where reservation overlaps two-week window starting today
    # i.e. (return date >= today and <= 2w) or (pickup date >= today and <= 2w)

    availability_by_date = {
        vehicle.id: {datetime.date.today() + datetime.timedelta(days=i) for i in range(14)}
        for vehicle
        in all_vehicles
    }

    for vehicle_id, pickup_date, return_date in rentals:
        date = pickup_date
        while date <= return_date:
            if date in availability_by_date[vehicle_id]:
                availability_by_date[vehicle_id].remove(date)
            date += datetime.timedelta(days=1)

    available_vehicles = [
        {
            "id": vehicle_id,
            "available_dates": sorted([date.strftime(Rental.DATE_FORMAT) for date in available_dates])
        }
        for vehicle_id, available_dates in availability_by_date.items()
    ]
    return available_vehicles
