import pandas as pd
import sqlite3

csv_file_path = '../data/HistoricData1980-2024.csv'
df = pd.read_csv(csv_file_path)
print(df)

db_path = 'climate_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS historic_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        temperature_2m_max REAL,
        temperature_2m_min REAL,
        precipitation_sum REAL,
        rain_sum REAL,
        snowfall_sum REAL,
        precipitation_hours REAL
    )
''')

for _, row in df.iterrows():
    cursor.execute('''
        INSERT INTO historic_data (
            date, temperature_2m_max, temperature_2m_min, precipitation_sum, rain_sum, snowfall_sum, precipitation_hours
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        row['date'], row['temperature_2m_max'], row['temperature_2m_min'], row['precipitation_sum'],
        row['rain_sum'], row['snowfall_sum'], row['precipitation_hours']
    ))

conn.commit()
conn.close()
