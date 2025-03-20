-- Sample data for EU Flight Monitor database

-- Insert German airports
INSERT INTO airports (name, iata_code, icao_code, country, city, latitude, longitude)
VALUES 
    ('Frankfurt Airport', 'FRA', 'EDDF', 'Germany', 'Frankfurt', 50.033333, 8.570556),
    ('Munich Airport', 'MUC', 'EDDM', 'Germany', 'Munich', 48.353889, 11.786111),
    ('Berlin Brandenburg Airport', 'BER', 'EDDB', 'Germany', 'Berlin', 52.366667, 13.503333),
    ('Hamburg Airport', 'HAM', 'EDDH', 'Germany', 'Hamburg', 53.630278, 9.988333),
    ('Düsseldorf Airport', 'DUS', 'EDDL', 'Germany', 'Düsseldorf', 51.289444, 6.766667);

-- Insert airlines
INSERT INTO airlines (name, iata_code, icao_code, country)
VALUES 
    ('Lufthansa', 'LH', 'DLH', 'Germany'),
    ('Eurowings', 'EW', 'EWG', 'Germany'),
    ('Ryanair', 'FR', 'RYR', 'Ireland'),
    ('Air France', 'AF', 'AFR', 'France'),
    ('British Airways', 'BA', 'BAW', 'United Kingdom');

-- Insert sample flights (mix of on-time and delayed)
INSERT INTO flights (flight_number, airline_id, departure_airport_id, arrival_airport_id, 
                   scheduled_departure, scheduled_arrival, actual_departure, actual_arrival, status)
VALUES
    -- On-time flights
    ('LH1234', 1, 1, 2, '2023-11-15 08:00:00', '2023-11-15 09:10:00', 
     '2023-11-15 08:05:00', '2023-11-15 09:15:00', 'landed'),
    
    ('EW5678', 2, 3, 1, '2023-11-15 10:30:00', '2023-11-15 11:45:00', 
     '2023-11-15 10:35:00', '2023-11-15 11:50:00', 'landed'),
    
    ('FR9012', 3, 4, 5, '2023-11-15 09:15:00', '2023-11-15 10:20:00', 
     '2023-11-15 09:20:00', '2023-11-15 10:25:00', 'landed'),
    
    ('AF3456', 4, 1, 3, '2023-11-15 14:00:00', '2023-11-15 15:30:00', 
     '2023-11-15 14:10:00', '2023-11-15 15:35:00', 'landed'),
    
    ('BA7890', 5, 2, 4, '2023-11-15 16:45:00', '2023-11-15 18:00:00', 
     '2023-11-15 16:50:00', '2023-11-15 18:05:00', 'landed'),
    
    -- Delayed flights (> 2 hours)
    ('LH5432', 1, 5, 1, '2023-11-15 07:30:00', '2023-11-15 08:45:00', 
     '2023-11-15 09:45:00', '2023-11-15 11:00:00', 'landed'),
    
    ('EW9876', 2, 2, 3, '2023-11-15 12:15:00', '2023-11-15 13:30:00', 
     '2023-11-15 14:30:00', '2023-11-15 15:45:00', 'landed'),
    
    ('FR5432', 3, 3, 5, '2023-11-15 11:00:00', '2023-11-15 12:15:00', 
     '2023-11-15 13:30:00', '2023-11-15 14:45:00', 'landed'),
    
    ('AF6789', 4, 4, 1, '2023-11-15 15:30:00', '2023-11-15 17:00:00', 
     '2023-11-15 18:00:00', '2023-11-15 19:30:00', 'landed'),
    
    ('BA1234', 5, 1, 2, '2023-11-15 18:15:00', '2023-11-15 19:30:00', 
     '2023-11-15 20:45:00', '2023-11-15 22:00:00', 'landed');

-- Insert flight status
INSERT INTO flight_status (flight_id, is_delayed, delay_minutes, delay_reason)
VALUES
    -- On-time flights
    (1, FALSE, 10, NULL),
    (2, FALSE, 5, NULL),
    (3, FALSE, 5, NULL),
    (4, FALSE, 10, NULL),
    (5, FALSE, 5, NULL),
    
    -- Delayed flights
    (6, TRUE, 135, 'Technical issues'),
    (7, TRUE, 135, 'Weather conditions'),
    (8, TRUE, 150, 'Air traffic control'),
    (9, TRUE, 150, 'Aircraft late arrival'),
    (10, TRUE, 150, 'Operational constraints');