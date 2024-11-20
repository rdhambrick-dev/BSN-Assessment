from flask import Blueprint, request, abort, jsonify

from db import get_database


class Customer:
    def __init__(self, id, name, phone, address, email):
        self.id = id
        self.name = name
        self.phone = phone
        self.address = address
        self.email = email

    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "address": self.address,
            "email": self.email
        }


bp = Blueprint("customer", __name__, url_prefix="/customers")


@bp.errorhandler(404)
def customer_not_found(e):
    return jsonify(error=str(e)), 404


@bp.post("/")
def create_customer():
    request_data = request.get_json()
    customer_data = {
        "name": request_data.get("name"),
        "phone": request_data.get("phone"),
        "address": request_data.get("address"),
        "email": request_data.get("email")
    }

    # todo error handling

    database = get_database()
    cursor = database.cursor()
    cursor.execute(
        "INSERT INTO customer "
        "(name, phone, address, email) "
        "VALUES (%(name)s, %(phone)s, %(address)s, %(email)s)",
        customer_data
    )
    new_customer_id = cursor.lastrowid
    database.commit()

    # todo error handling if failed to create (eg email constraint in db)

    new_customer = Customer(new_customer_id, **customer_data)
    return new_customer.dict(), 201


@bp.get("/<int:id>")
def get_customer(id):
    cursor = get_database().cursor()
    cursor.execute(
        "SELECT * FROM customer WHERE id = %s",
        [id]
    )

    customer = cursor.fetchone()
    if not customer:
        abort(404, description=f"Customer with id {id} not found.")
    return Customer(*customer).dict()


@bp.get("/")
def get_all_customers():
    cursor = get_database().cursor()
    cursor.execute("SELECT * FROM customer")
    return [Customer(*customer).dict() for customer in cursor.fetchall()]


@bp.route("/<int:id>", methods=["PUT", "PATCH"])
def update_customer(id):
    database = get_database()
    cursor = database.cursor()
    cursor.execute(
        "SELECT * FROM customer WHERE id = %s",
        [id]
    )

    existing_customer = cursor.fetchone()
    if not existing_customer:
        abort(404, description=f"Customer with id {id} not found.")

    existing_customer = Customer(*existing_customer)

    request_data = request.get_json()
    if request.method == "PATCH":
        new_customer_data = {
            "id": id,
            "name": request_data.get("name", existing_customer.name),
            "phone": request_data.get("phone", existing_customer.phone),
            "address": request_data.get("address", existing_customer.address),
            "email": request_data.get("email", existing_customer.email)
        }
    else:  # request.method == "POST"
        new_customer_data = {
            "id": id,
            "name": request_data.get("name"),
            "phone": request_data.get("phone"),
            "address": request_data.get("address"),
            "email": request_data.get("email")
        }

    cursor.execute(
        "UPDATE customer SET "
        "name = %(name)s, "
        "phone = %(phone)s, "
        "address = %(address)s, "
        "email = %(email)s "
        "WHERE id = %(id)s",
        new_customer_data
    )
    database.commit()

    # todo error handling if failed to create (eg email constraint in db)

    new_customer = Customer(**new_customer_data)
    return new_customer.dict()


@bp.delete("/<int:id>")
def delete_customer(id):
    database = get_database()
    cursor = database.cursor()
    cursor.execute(
        "DELETE FROM customer WHERE id = %s",
        [id]
    )
    database.commit()
    return {}, 204
