DROP DATABASE IF EXISTS sensor_data

CREATE DATABASE sensor_data;

USE sensor_data;

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
);

CREATE TABLE plc(
	id INT AUTO_INCREMENT,
    user_id INT,
    y0 FLOAT DEFAULT 0.0,
    y1 FLOAT DEFAULT 0.0,
    y2 FLOAT DEFAULT 0.0,
    y3 FLOAT DEFAULT 0.0;
    PRIMARY KEY (id, user_id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE data (
    id INT PRIMARY KEY AUTO_INCREMENT,
    plc_id INT,
    temperature FLOAT DEFAULT 0.0,
    humidity FLOAT DEFAULT 0.0,
    pm25 FLOAT DEFAULT 0.0,
    pm10 FLOAT DEFAULT 0.0,
    pm25_average_in_one_hour FLOAT DEFAULT 0.0,
    pm10_average_in_one_hour FLOAT DEFAULT 0.0,
    tvoc FLOAT DEFAULT 0.0,
    co2 FLOAT DEFAULT 0.0,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plc_id) REFERENCES plc(id)
);