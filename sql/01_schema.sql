-- =====================================================================
-- SCHEMA for MySQL 8 / PostgreSQL   (SQLite users: skip this file, data/hotel.db is ready)
-- Create a database first:   CREATE DATABASE hotel_revpar;   then USE / connect to it.
-- Load the CSVs from data/tables/ in THIS order (parents first, bookings next, stay_nights last).
--   MySQL    : Table Data Import Wizard in Workbench (right-click table > Import)  or LOAD DATA LOCAL INFILE
--   PostgreSQL: pgAdmin > right-click table > Import/Export  or  \copy table FROM 'file.csv' CSV HEADER
-- =====================================================================
CREATE TABLE room_types (room_type_id INT PRIMARY KEY, room_type VARCHAR(20) NOT NULL);
CREATE TABLE segments   (segment_id   INT PRIMARY KEY, market_segment VARCHAR(30) NOT NULL);
CREATE TABLE meal_plans (meal_plan_id INT PRIMARY KEY, meal_plan VARCHAR(20) NOT NULL);

CREATE TABLE customers (
  customer_id INT PRIMARY KEY, adults INT, children INT, total_guests INT,
  repeated_guest INT, prev_cancellations INT, prev_not_cancelled INT);

CREATE TABLE calendar (
  date_key DATE PRIMARY KEY, year INT, month INT, month_name VARCHAR(12), quarter INT,
  weekday VARCHAR(12), is_weekend INT, season VARCHAR(10));

CREATE TABLE hotel_info (hotel_name VARCHAR(60), total_rooms INT);

CREATE TABLE bookings (
  booking_id VARCHAR(12) PRIMARY KEY,
  customer_id INT REFERENCES customers(customer_id),
  room_type_id INT REFERENCES room_types(room_type_id),
  segment_id INT REFERENCES segments(segment_id),
  meal_plan_id INT REFERENCES meal_plans(meal_plan_id),
  arrival_date DATE, arrival_year INT, arrival_month INT,
  total_nights INT, weekend_nights INT, week_nights INT,
  lead_time INT, lead_bucket VARCHAR(15),
  avg_price_per_room DECIMAL(10,2), room_revenue DECIMAL(12,2),
  is_cancelled INT, is_complimentary INT, special_requests INT, parking_required INT);

CREATE TABLE stay_nights (
  booking_id VARCHAR(12) REFERENCES bookings(booking_id),
  stay_date DATE REFERENCES calendar(date_key));

CREATE INDEX idx_stay_date ON stay_nights(stay_date);
CREATE INDEX idx_book_seg  ON bookings(segment_id);
