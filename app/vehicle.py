from flask import Blueprint, request, abort, jsonify

from db import get_database


class Vehicle:
    def __init__(self, id, category):
        self.id = id
        self.category = category

    def dict(self):
        return {
            "id": self.id,
            "category": self.category
        }


bp = Blueprint("vehicle", __name__, url_prefix="/vehicles")


@bp.errorhandler(404)
def vehicle_not_found(e):
    return jsonify(error=str(e)), 404


@bp.post("/")
def create_vehicle():
    request_data = request.get_json()
    vehicle_category = request_data.get("category")

    # todo error handling if no category

    database = get_database()
    cursor = database.cursor()
    cursor.execute(
        "INSERT INTO vehicle (category) VALUES (%s)",
        [vehicle_category]
    )
    new_vehicle_id = cursor.lastrowid
    database.commit()

    # todo error handling if failed to create (category constraint in db)

    new_vehicle = Vehicle(new_vehicle_id, vehicle_category)
    return new_vehicle.dict(), 201


@bp.get("/<int:id>")
def get_vehicle(id):
    cursor = get_database().cursor()
    cursor.execute(
        "SELECT * FROM vehicle WHERE id = %s",
        [id]
    )

    vehicle = cursor.fetchone()
    if not vehicle:
        abort(404, description=f"Vehicle with id {id} not found.")
    return Vehicle(*vehicle).dict()


@bp.get("/")
def get_all_vehicles():
    cursor = get_database().cursor()
    cursor.execute("SELECT * FROM vehicle")
    return [Vehicle(*vehicle).dict() for vehicle in cursor.fetchall()]


@bp.route("/<int:id>", methods=["PUT", "PATCH"])
def update_vehicle(id):
    database = get_database()
    cursor = database.cursor()
    cursor.execute(
        "SELECT * FROM vehicle WHERE id = %s",
        [id]
    )

    existing_vehicle = cursor.fetchone()
    if not existing_vehicle:
        abort(404, description=f"Vehicle with id {id} not found.")

    existing_vehicle = Vehicle(*existing_vehicle)

    request_data = request.get_json()
    if request.method == "PATCH":
        new_vehicle_data = {
            "id": id,
            "category": request_data.get("category", existing_vehicle.category)
        }
    else:  # request.method == "POST"
        new_vehicle_data = {
            "id": id,
            "category": request_data.get("category")
        }

    cursor.execute(
        "UPDATE vehicle SET category = %(category)s WHERE id = %(id)s",
        new_vehicle_data
    )
    database.commit()

    # todo error handling if failed to create

    new_vehicle = Vehicle(**new_vehicle_data)
    return new_vehicle.dict()


@bp.delete("/<int:id>")
def delete_vehicle(id):
    database = get_database()
    cursor = database.cursor()
    cursor.execute(
        "DELETE FROM vehicle WHERE id = %s",
        [id]
    )
    database.commit()
    return {}, 204
