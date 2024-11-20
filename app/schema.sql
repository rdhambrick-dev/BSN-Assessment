CREATE TABLE vehicle (
    id INT NOT NULL AUTO_INCREMENT,
    category VARCHAR(20) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE customer (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    address VARCHAR(256),
    email VARCHAR(256) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE rental (
    id INT NOT NULL AUTO_INCREMENT,
    vehicle_id INT NOT NULL,
    customer_id INT NOT NULL,
    pickup_date DATE NOT NULL,
    return_date DATE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicle(id),
    FOREIGN KEY (customer_id) REFERENCES customer(id),
    CONSTRAINT return_date_after_pickup_date CHECK (return_date >= pickup_date)
);
