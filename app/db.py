"""SQLite persistence for the RoadSafe Nepal demonstration app."""
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.getenv('ROADSAFE_DB', Path(__file__).resolve().parent.parent / 'roadsafe.db'))
SCHEMA = '''
CREATE TABLE IF NOT EXISTS incidents (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 occurred_on TEXT NOT NULL,
 district TEXT NOT NULL,
 location TEXT NOT NULL,
 severity TEXT NOT NULL CHECK(severity IN ('Low','Medium','High','Critical')),
 category TEXT NOT NULL CHECK(category IN ('Collision','Near miss','Road hazard','Other')),
 description TEXT NOT NULL,
 latitude REAL,
 longitude REAL,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_incidents_date ON incidents(occurred_on);
CREATE INDEX IF NOT EXISTS idx_incidents_district ON incidents(district);
'''

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.executescript(SCHEMA)
    return db

DEMO = [
 ('2026-09-02','Kathmandu','Kalanki','High','Collision','Demo: vehicle collision at a busy junction',27.6934,85.2818),
 ('2026-09-04','Lalitpur','Satdobato','Medium','Near miss','Demo: pedestrian near miss',27.6588,85.3247),
 ('2026-09-07','Bhaktapur','Suryabinayak','Low','Road hazard','Demo: damaged road surface',27.6652,85.4279),
 ('2026-09-09','Kathmandu','Koteshwor','Critical','Collision','Demo: multi-vehicle collision',27.6781,85.3490),
 ('2026-09-12','Pokhara','Prithvi Chowk','Medium','Road hazard','Demo: poor visibility near junction',28.2096,83.9856),
 ('2026-09-16','Kathmandu','Maharajgunj','Low','Near miss','Demo: near miss during peak hour',27.7397,85.3330),
 ('2026-09-20','Lalitpur','Lagankhel','High','Collision','Demo: collision at intersection',27.6684,85.3201),
 ('2026-09-23','Kathmandu','Baneshwor','Medium','Other','Demo: obstructed traffic lane',27.6882,85.3426),
 ('2026-09-27','Bhaktapur','Thimi','High','Road hazard','Demo: unmarked construction zone',27.6753,85.3875),
 ('2026-10-01','Pokhara','Lakeside','Low','Near miss','Demo: cyclist near miss',28.2090,83.9595),
 ('2026-10-03','Kathmandu','Chabahil','Critical','Collision','Demo: serious intersection incident',27.7164,85.3461),
 ('2026-10-05','Lalitpur','Jawalakhel','Medium','Road hazard','Demo: traffic signal malfunction',27.6725,85.3121),
]

def seed(db):
    if db.execute('SELECT COUNT(*) FROM incidents').fetchone()[0] == 0:
        db.executemany('INSERT INTO incidents (occurred_on,district,location,severity,category,description,latitude,longitude) VALUES (?,?,?,?,?,?,?,?)', DEMO)
        db.commit()
