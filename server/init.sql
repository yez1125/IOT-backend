DROP DATABASE IF EXISTS IoT_Monitor;

CREATE DATABASE IoT_Monitor;

USE IoT_Monitor;

CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
);

CREATE TABLE plc(
	plc_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE sensor (
    sensor_id INT PRIMARY KEY AUTO_INCREMENT,
    plc_id INT,
    FOREIGN KEY (plc_id) REFERENCES plc(plc_id)
);

CREATE TABLE data (
    time TIMESTAMP PRIMARY KEY DEFAULT CURRENT_TIMESTAMP,
    sensor_id INT PRIMARY KEY,
    temperature FLOAT DEFAULT 0.0,
    humidity FLOAT DEFAULT 0.0,
    pm25 FLOAT DEFAULT 0.0,
    pm10 FLOAT DEFAULT 0.0,
    pm25_average_in_one_hour FLOAT DEFAULT 0.0,
    pm10_average_in_one_hour FLOAT DEFAULT 0.0,
    tvoc FLOAT DEFAULT 0.0,
    co2 FLOAT DEFAULT 0.0,
    FOREIGN KEY (sensor_id) REFERENCES sensor(sensor_id)
);

CREATE TABLE abox(
    abox_id INT PRIMARY KEY AUTO_INCREMENT,
    plc_id INT PRIMARY KEY,
    plc_output INT DEFAULT 0,
    abox_status BOOLEAN DEFAULT 0,
    FOREIGN KEY (plc_id) REFERENCES plc(plc_id)
);