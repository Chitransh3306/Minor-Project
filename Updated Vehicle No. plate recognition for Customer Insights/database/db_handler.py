import sqlite3
import pandas as pd
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "vehicle_data.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"
DEMOGRAPHICS_CSV = BASE_DIR / "database" / "demographics.csv"
ITEMS_CSV = BASE_DIR / "database" / "items.csv"
PREFERS_CSV = BASE_DIR / "database" / "prefers.csv"

# Pre-populate state master data
DEFAULT_STATES = {
    "AN": "Andaman & Nicobar Islands", "AP": "Andhra Pradesh", "AR": "Arunachal Pradesh",
    "AS": "Assam", "BR": "Bihar", "CH": "Chandigarh", "CG": "Chhattisgarh",
    "DD": "Daman & Diu", "DN": "Dadra & Nagar Haveli", "DL": "Delhi", "GA": "Goa",
    "GJ": "Gujarat", "HR": "Haryana", "HP": "Himachal Pradesh", "JH": "Jharkhand",
    "JK": "Jammu & Kashmir", "KA": "Karnataka", "KL": "Kerala", "LA": "Ladakh",
    "LD": "Lakshadweep", "MP": "Madhya Pradesh", "MH": "Maharashtra", "MN": "Manipur",
    "ML": "Meghalaya", "MZ": "Mizoram", "NL": "Nagaland", "OD": "Odisha",
    "PB": "Punjab", "PY": "Puducherry", "RJ": "Rajasthan", "SK": "Sikkim",
    "TN": "Tamil Nadu", "TS": "Telangana", "TR": "Tripura", "UK": "Uttarakhand",
    "UA": "Uttarakhand (Legacy)", "OR": "Odisha (Legacy)", "UP": "Uttar Pradesh",
    "WB": "West Bengal", "BH": "Bharat Series"
}

def connect_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Initialize DB schema and populate default state master table."""
    with connect_db() as conn:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        
        # Populate State master records
        for code, name in DEFAULT_STATES.items():
            conn.execute(
                "INSERT OR IGNORE INTO State (State_Code, State_Name) VALUES (?, ?)",
                (code, name)
            )
        conn.commit()

def import_csv_data():
    """Import reference tables only if they are not already populated (idempotent)."""
    with connect_db() as conn:
        cursor = conn.cursor()

        # Demographics
        cursor.execute("SELECT COUNT(*) FROM Demographics")
        if cursor.fetchone()[0] == 0 and DEMOGRAPHICS_CSV.exists():
            df_demo = pd.read_csv(DEMOGRAPHICS_CSV)
            df_demo.to_sql("Demographics", conn, if_exists="append", index=False)

        # Items
        cursor.execute("SELECT COUNT(*) FROM Items")
        if cursor.fetchone()[0] == 0 and ITEMS_CSV.exists():
            df_items = pd.read_csv(ITEMS_CSV)
            df_items.to_sql("Items", conn, if_exists="append", index=False)

        # Prefers
        cursor.execute("SELECT COUNT(*) FROM Prefers")
        if cursor.fetchone()[0] == 0 and PREFERS_CSV.exists():
            df_prefers = pd.read_csv(PREFERS_CSV)
            df_prefers.to_sql("Prefers", conn, if_exists="append", index=False)

        conn.commit()

def insert_vehicle(plate_no, state_code, state_name, confidence=1.0):
    """Insert recognized vehicle and ensure state is recorded."""
    with connect_db() as conn:
        # Ensure state exists in master
        conn.execute(
            "INSERT OR IGNORE INTO State (State_Code, State_Name) VALUES (?, ?)",
            (state_code, state_name)
        )
        conn.execute(
            "INSERT INTO Vehicle_Record (Plate_No, State_Code, Confidence) VALUES (?, ?, ?)",
            (plate_no, state_code, float(confidence))
        )
        conn.commit()

def fetch_state_counts():
    """Fetch aggregated vehicle counts with both state code and state name."""
    with connect_db() as conn:
        df = pd.read_sql_query("""
            SELECT s.State_Code as state_code, s.State_Name as state_name, COUNT(v.Record_ID) as count
            FROM Vehicle_Record v
            JOIN State s ON v.State_Code = s.State_Code
            GROUP BY s.State_Code, s.State_Name
            ORDER BY count DESC
        """, conn)
    return df

def fetch_recommendations(top_state_codes):
    """Fetch demographic preferences and suggested inventory items for top states."""
    if not top_state_codes:
        return pd.DataFrame()
    
    placeholders = ",".join(["?"] * len(top_state_codes))
    query = f"""
        SELECT 
            d.State_Code,
            s.State_Name,
            d.Age_bracket as Age_Bracket,
            d.Gender_Ratio,
            d.Essentials,
            d.Food_Preference,
            COALESCE(GROUP_CONCAT(i.Item_Name, ', '), 'General Essentials') as Suggested_Items
        FROM Demographics d
        JOIN State s ON d.State_Code = s.State_Code
        LEFT JOIN Prefers p ON d.Demographic_ID = p.Demographic_ID
        LEFT JOIN Items i ON p.Item_ID = i.Item_ID
        WHERE d.State_Code IN ({placeholders})
        GROUP BY d.State_Code, s.State_Name, d.Age_bracket, d.Gender_Ratio, d.Essentials, d.Food_Preference
    """
    with connect_db() as conn:
        df = pd.read_sql_query(query, conn, params=top_state_codes)
    return df

def fetch_recent_vehicles(limit=50):
    """Fetch latest vehicle detection logs with timestamps."""
    with connect_db() as conn:
        df = pd.read_sql_query("""
            SELECT 
                v.Record_ID,
                v.Plate_No,
                s.State_Name as Region,
                v.Confidence,
                v.Timestamp
            FROM Vehicle_Record v
            JOIN State s ON v.State_Code = s.State_Code
            ORDER BY v.Record_ID DESC
            LIMIT ?
        """, conn, params=[limit])
    return df
