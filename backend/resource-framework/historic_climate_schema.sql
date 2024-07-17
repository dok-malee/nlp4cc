CREATE TABLE historic_data (
    id INTEGER PRIMARY KEY,
    date TEXT UNIQUE,
    temperature_2m_max REAL,
    temperature_2m_min REAL,
    precipitation_sum REAL,
    rain_sum REAL,
    snowfall_sum REAL,
    precipitation_hours REAL
);

