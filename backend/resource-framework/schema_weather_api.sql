CREATE TABLE weather_data (
    id INTEGER PRIMARY KEY,
    date TEXT UNIQUE,
    location_code TEXT,
    temperature_2m_max REAL,
    temperature_2m_min REAL,
    uv_index_max REAL,
    precipitation_sum REAL,
    rain_sum REAL,
    showers_sum REAL,
    snowfall_sum REAL,
    precipitation_probability_max REAL,
    soil_moisture_1_to_3cm REAL,
    soil_moisture_9_to_27cm REAL
);

