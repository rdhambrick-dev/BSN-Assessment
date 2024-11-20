This project is a solution to the Backend Developer Assignment for Breach Secure Now.

## Setup
1. Using `poetry`, run `poetry install`. Otherwise, setup with pip using `requirements.txt`. 
2. Create a `.env` file inside `app/` with following contents. Replace the values in brackets with your database credentials.
```env
DB_HOST=<host>
DB_USER=<database username>
DB_PASSWORD=<database password>
```
3. From inside `app/` run `flask run`.

## Endpoints
Simple CRUD endpoints exist for vehicles, customers, and rentals at:
- `/vehciles/`
- `/customers/`
- `/rentals/`

Other feature endpoints include:
- `/vehciles/availability/` to check the availability of all vehicles. The query string parameter `category` can be used to check only vehicles of the specified category.
- `/vehciles/<id>/availability` to check the availability of a specific vehicle.
- `/report/` to check all reservations that occur on a specific date. The date must be specified in the request body, with the form:
```json
{
  "date": "2024-11-20"
}
```
a `"category"` property can be included in the request body to see the report for only vehicles of the specified category.

## TODO
Some requirements are not yet implemented:
- Emailing invoices to customers after a rental is confirmed.
- Emailing a confirmation to customers when the rental is booked in advance.

## Resources Used
- [Flask User Guide](https://flask.palletsprojects.com/en/stable/#user-s-guide)
- [Python MySQL Connector Developer Guide](https://dev.mysql.com/doc/connector-python/en/)